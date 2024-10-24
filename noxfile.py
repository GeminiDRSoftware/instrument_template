"""Noxfile meant for the cookiecutter repository itself."""

from pathlib import Path
import os
import shutil

import nox

nox.options.sessions = ["test"]
nox.options.error_on_external_run = True


@nox.session
def lint(session: nox.Session):
    """Run linters. Since cookiecutter formatting (double curly braces) is not
    supported by ruff, we will escape those values specifically for ruff."""
    session.install("pre-commit")
    session.run_install("pre-commit", "install")
    session.run("pre-commit", "run", "--all-files")


@nox.session
def initialize_commit_hooks(session: nox.Session):
    """Run pre-commit to install various hooks.

    The hooks are in `.pre-commit-config.yaml`.
    """
    session.install("pre-commit")
    session.run(
        "pre-commit",
        "install",
        "--install-hooks",
        "--hook-type=pre-commit",
        "--hook-type=commit-msg",
    )


@nox.session(python=["3.10", "3.11", "3.12"])
def test(session: nox.Session):
    """Test the cookiecutter template."""
    session.install("pytest", "pytest-cookies")

    session.run("pytest", "tests/", *session.posargs)

    session.notify("test_filled_template")


@nox.session(python=["3.10", "3.11", "3.12"])
def test_filled_template(session: nox.Session):
    """Test a freshly generated template."""
    session.install("cookiecutter", "pre-commit", "nox")

    tmp_dir = Path(session.create_tmp()).resolve()

    if tmp_dir.exists():
        all_dirs = [
            Path(root) / dir for root, dirs, _ in os.walk(tmp_dir) for dir in dirs
        ]
        for path in all_dirs:
            if path.exists():
                shutil.rmtree(path)

    template_dir = Path(".").resolve()

    with session.chdir(".."):
        session.run(
            "cookiecutter",
            "--no-input",
            "--default-config",
            str(template_dir),
            "-o",
            str(tmp_dir),
        )

    new_package_path = tmp_dir / "default_instrument_name_dr_package"

    with session.chdir(tmp_dir):
        assert new_package_path.exists()

    with session.chdir(new_package_path):
        # Create a development environment and ensure packages are installed.
        session.log(80 * "=")
        session.log("  GENERATING DEVELOPMENT ENVIRONMENT")
        session.log(80 * "=")
        session.run("nox", "-s", "devenv")

        venv_loc = Path("venv")
        venv_python = venv_loc / "bin" / "python"

        instrument = "default_instrument_name"
        instrument_title = "Default_Instrument_Name"

        test_imports = (
            "import astrodata",
            "import gemini_instruments",
            "import geminidr",
            "import gempy",
            "import gemini_obs_db",
            "import gemini_calmgr",
            f"import {instrument}_instruments",
            f"import {instrument}_instruments.{instrument}",
            f"from {instrument}_instruments.{instrument} import AstroData{instrument_title}",
            f"import {instrument}dr",
        )

        session.run(
            str(venv_python),
            "-c",
            "\n".join(test_imports),
            external=True,
        )

        session.log(80 * "=")
        session.log("  RUNNING TESTS ON GENERATED TEMPLATE")
        session.log(80 * "=")

        # Run the tests.
        session.run("nox", "-s", "tests", "--verbose")
