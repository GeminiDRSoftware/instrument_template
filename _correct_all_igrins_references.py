"""Script that finds {{ cookiecutter.instrument_name }} references and inserts the appropriate name."""

import difflib
from pathlib import Path
import re
import tempfile

IGNORE_PATTERNS = (r".*\.nox.*", r".*/_.*")


def replace_igrins_instances(text: str) -> str:
    """Replace {{ cookiecutter.instrument_name_lower }} instances with the appropriate case."""
    new_text = text.replace("igrins", "{{ cookiecutter.instrument_name_lower }}")
    new_text = new_text.replace("IGRINS-2", "{{ cookiecutter.instrument_fits_name }}")
    new_text = new_text.replace("IGRINS", "{{ cookiecutter.instrument_name }}")
    new_text = new_text.replace("Igrins", "{{ cookiecutter.instrument_name_title }}")

    return new_text


def fix_file(path: Path, *, dry_run: bool = False) -> tuple[str, bool]:
    """Fix a single file's contents."""
    content = path.read_text()

    new_content = replace_igrins_instances(content)

    if new_content == content:
        return ("", False)

    if not dry_run:
        path.write_text(new_content)

    # Check if there's changes to the file.
    diff = diff_text(content, new_content)

    return (diff, bool(diff))


def diff_text(text_1: str, text_2: str) -> str:
    lines_1 = [f"{line}" for line in text_1.splitlines()]
    lines_2 = [f"{line}" for line in text_2.splitlines()]
    return "\n".join(line for line in difflib.unified_diff(lines_1, lines_2))


def test_change_lowercase():
    """Test that the script changes lowercase {{ cookiecutter.instrument_name_lower }}."""
    test_file_contents = (
        "def make_igrins_thing():\n"
        "    '''Another igrins reference.'''\n"
        "    igrins_variable = {}\n"
        "    operation = BLAH_CONSTANT * igrins_variable\n"
    )

    expected_file_contents = (
        "def make_{{ cookiecutter.instrument_name_lower }}_thing():\n"
        "    '''Another {{ cookiecutter.instrument_name_lower }} reference.'''\n"
        "    {{ cookiecutter.instrument_name_lower }}_variable = {}\n"
        "    operation = BLAH_CONSTANT * {{ cookiecutter.instrument_name_lower }}_variable\n"
    )

    with tempfile.NamedTemporaryFile() as tmp_file:
        temp_file = Path(tmp_file.name)
        temp_file.write_text(test_file_contents)

        fix_file(temp_file)

        file_text = temp_file.read_text()

        assert file_text
        assert file_text == expected_file_contents, diff_text(
            file_text, expected_file_contents
        )


def test_change_uppercase():
    """Test that the script changes uppercase {{ cookiecutter.instrument_name }}."""
    test_file_contents = (
        "def make_IGRINS_thing():\n"
        "    '''Another IGRINS reference.'''\n"
        "    IGRINS_variable = {}\n"
        "    operation = BLAH_CONSTANT * IGRINS_variable\n"
    )

    expected_file_contents = (
        "def make_{{ cookiecutter.instrument_name }}_thing():\n"
        "    '''Another {{ cookiecutter.instrument_name }} reference.'''\n"
        "    {{ cookiecutter.instrument_name }}_variable = {}\n"
        "    operation = BLAH_CONSTANT * {{ cookiecutter.instrument_name }}_variable\n"
    )

    with tempfile.NamedTemporaryFile() as tmp_file:
        temp_file = Path(tmp_file.name)
        temp_file.write_text(test_file_contents)

        fix_file(temp_file)

        file_text = temp_file.read_text()

        assert file_text
        assert file_text == expected_file_contents, diff_text(
            file_text, expected_file_contents
        )


def test_change_titlecase():
    """Test that the script changes uppercase {{ cookiecutter.instrument_name }}."""
    test_file_contents = (
        "def make_Igrins_thing():\n"
        "    '''Another Igrins reference.'''\n"
        "    Igrins_variable = {}\n"
        "    operation = BLAH_CONSTANT * Igrins_variable\n"
    )

    expected_file_contents = (
        "def make_{{ cookiecutter.instrument_name_title }}_thing():\n"
        "    '''Another {{ cookiecutter.instrument_name_title }} reference.'''\n"
        "    {{ cookiecutter.instrument_name_title }}_variable = {}\n"
        "    operation = BLAH_CONSTANT * {{ cookiecutter.instrument_name_title }}_variable\n"
    )

    with tempfile.NamedTemporaryFile() as tmp_file:
        temp_file = Path(tmp_file.name)
        temp_file.write_text(test_file_contents)

        diff, changed = fix_file(temp_file)

        file_text = temp_file.read_text()

        assert file_text
        assert file_text == expected_file_contents, diff_text(
            file_text, expected_file_contents
        )

        assert diff
        assert changed


def test_change_FITS_keyword():
    """Test that the script changes uppercase {{ cookiecutter.instrument_name }}."""
    test_file_contents = "blah\nblah2 = 'IGRINS-2'"

    expected_file_contents = "blah\nblah2 = '{{ cookiecutter.instrument_fits_name }}'"

    with tempfile.NamedTemporaryFile() as tmp_file:
        temp_file = Path(tmp_file.name)
        temp_file.write_text(test_file_contents)

        diff, changed = fix_file(temp_file)

        file_text = temp_file.read_text()

        assert file_text
        assert file_text == expected_file_contents, diff_text(
            file_text, expected_file_contents
        )

        assert diff
        assert changed


def test_no_change():
    """Test unchanged file."""
    test_file_contents = "Blah\nblah\nbing bong"
    expected_file_contents = "Blah\nblah\nbing bong"

    with tempfile.NamedTemporaryFile() as tmp_file:
        temp_file = Path(tmp_file.name)
        temp_file.write_text(test_file_contents)

        diff, changed = fix_file(temp_file)

        file_text = temp_file.read_text()

        assert file_text
        assert file_text == expected_file_contents, diff_text(
            file_text, expected_file_contents
        )

        assert not diff
        assert not changed


def main():
    # Health checks
    test_change_lowercase()
    test_change_uppercase()
    test_change_titlecase()
    test_change_FITS_keyword()
    test_no_change()
    print("Tests passed!")

    print("Modifying files (dry run)... (listing them)")

    for root, _, files in Path(".").walk():
        for file in files:
            if not str(file).endswith(".py"):
                continue

            path = root / file

            if path.resolve() == Path(__file__):
                print("Skipping this file...")
                continue

            if any(re.match(rstr, str(path)) for rstr in IGNORE_PATTERNS):
                continue

            diff, changed = fix_file(path, dry_run=True)

            if changed:
                print(f"CHANGED: {path}")
                print("-" * 80)
                print(diff)

            else:
                print(f"UNCHANGED: {path}")


if __name__ == "__main__":
    main()
