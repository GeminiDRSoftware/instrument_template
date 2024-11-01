"""Tests the template setup."""

from itertools import chain
import logging
import os
import subprocess
from pathlib import Path
import re

import pytest

LOGGER = logging.getLogger(__name__)


def test_no_igrins_references(cookies):
    """There should not be any reference to igrins in the template."""
    for root, directories, files in os.walk("{{ cookiecutter.project_slug }}"):
        for path in (Path(root) / base for base in chain(directories, files)):
            # Skip correction scipt
            if "_correct_all_igrins_ref" in str(path):
                continue

            assert "igrins" not in str(path).lower(), f"Igrins found in: {path}"

            if path.is_dir():
                continue

            try:
                contents = path.read_text()

            except UnicodeDecodeError as err:
                message = (
                    f"Skipping file {path}, could not decode ({err.__class__}: {err}"
                )
                LOGGER.info(message)

            # Slow but doesn't need to be fast (no big files).
            lines = contents.splitlines()

            for i, line in enumerate(lines, start=1):
                assert (
                    "igrins" not in line.lower()
                ), f"IGRINS ref found ({path}::{i}):\n{line}"


@pytest.mark.parametrize("instrument_name", ["IGRINS", "GIRMOS", "FOX"])
def test_no_instrument_refs(instrument_name, cookies, monkeypatch):
    """Tests for references to several different instrument names."""
    result = cookies.bake()

    assert result.exit_code == 0

    monkeypatch.chdir(result.project_path)

    comp_instrument_name = instrument_name.casefold()

    for root, directories, files in os.walk("."):
        assert comp_instrument_name not in root.casefold(), root

        for path in (Path(root) / Path(p) for p in chain(directories, files)):
            assert comp_instrument_name not in str(path).casefold(), path

            if path.is_file():
                try:
                    file_lines = path.read_text().splitlines()

                except UnicodeDecodeError:
                    LOGGER.info(f"Skipping file: {path}")
                    continue

                for i, line in enumerate(file_lines):
                    msg = f"{path}::{i} -> {line.strip()}"
                    assert comp_instrument_name not in line.casefold(), msg


def test_default_template(cookies, monkeypatch):
    """Test that the default template fills in correctly."""
    result = cookies.bake()

    assert result.exit_code == 0

    monkeypatch.chdir(str(result.project_path))
    for root, directories, files in os.walk(Path(".")):
        for path in (Path(root) / base for base in chain(directories, files)):
            # Ignore all git repo files.
            if ".git" in str(path):
                continue

            assert "cookie" not in str(path).lower(), path
            assert not any(c in str(path) for c in R"{}"), path

            if not path.is_file():
                continue

            try:
                contents = path.read_text()

            # This is kind of lazy, it'd be better to specify files to ignore in case an unexpected item slips in that would be caught here.
            except UnicodeDecodeError as err:
                LOGGER.info(f"Skipping {path}: got UnicodeDecodeError {err}")
                continue

            for i, line in enumerate(contents.splitlines(), start=1):
                errstr = f"{path}::{i} - {line}"

                # Ignore markdown links
                if "cookie" in line and re.match(r"^\[[^\]]*\]:.*", line):
                    continue

                assert "cookie" not in line, errstr

                if path.suffix in [".yml", ".yaml"] and "github" in str(path):
                    continue

                assert "{{" not in line, errstr
                assert "}}" not in line, errstr


@pytest.mark.parametrize(
    "extra_context",
    [{}, {"instrument_name": "OTHERNAME"}, {"instrument_name": "othername"}],
)
def test_lowercase_package_names(extra_context, cookies, monkeypatch):
    """Test that certain dirs follow PEP8 package name guidelines.

    See: https://peps.python.org/pep-0008/#package-and-module-names
    """
    result = cookies.bake(extra_context=extra_context)

    monkeypatch.chdir(result.project_path)

    instrument_name = result.context["instrument_name"]

    expected_lowercase_paths = [
        f"{instrument_name}dr/",
        f"{instrument_name}_instruments/",
    ]

    expected_lowercase_paths = [Path(p.lower()) for p in expected_lowercase_paths]

    for path in expected_lowercase_paths:
        assert path.exists()
        assert path.is_dir()


def test_git_repo(cookies, monkeypatch):
    """Test that the git repo initializes properly."""
    result = cookies.bake()

    monkeypatch.chdir(result.project_path)

    assert Path(".git").exists(), "No git dir created"


@pytest.mark.parametrize("dragons_branch", ["release/3.2.x"])
def test_download_correct_dragons_version_from_env(
    dragons_branch, cookies, monkeypatch
):
    """Test that proper branches are downloaded when specified by a user."""
    instrument_name = "BLAH"
    result = cookies.bake(extra_context={"instrument_name": instrument_name})

    assert result.exit_code == 0

    monkeypatch.chdir(result.project_path)

    command_env = {
        "DRAGONS_BRANCH": dragons_branch,
    }

    command_env |= os.environ

    command = ["nox", "-s", "devenv"]

    subprocess.run(command, env=command_env)

    monkeypatch.chdir(result.project_path / "DRAGONS/")

    branch_command = ["git", "branch"]
    result = subprocess.run(branch_command, capture_output=True)

    output = result.stdout.decode("utf-8")

    for line in output.splitlines():
        if match := re.match(r"^\s+\*\s+([A-Za-z0-9\-/_]+)\s*$", line):
            assert match.group(1) == dragons_branch
            break


@pytest.mark.parametrize("dragons_branch", ["release/3.2.x"])
def test_download_correct_dragons_version_in_template(
    dragons_branch, cookies, monkeypatch
):
    """Test specifying the dragons branch in the cookiecutter prompt."""
    instrument_name = "BLAH"
    extra_context = {
        "dragons_branch": dragons_branch,
        "instrument_name": instrument_name,
    }

    result = cookies.bake(extra_context=extra_context)

    assert result.exit_code == 0

    monkeypatch.chdir(result.project_path)

    command = ["nox", "-s", "devenv"]

    subprocess.run(command)

    monkeypatch.chdir(result.project_path / "DRAGONS/")

    branch_command = ["git", "branch"]
    result = subprocess.run(branch_command, capture_output=True)

    output = result.stdout.decode("utf-8")

    for line in output.splitlines():
        if match := re.match(r"^\s+\*\s+([A-Za-z0-9\-/_]+)\s*$", line):
            assert match.group(1) == dragons_branch
            break


@pytest.mark.parametrize("dragons_location", ["bing/", "bong"])
def test_download_dragons_to_location_template(dragons_location, cookies, monkeypatch):
    """Test setting default dragons path in template."""
    instrument_name = "BLAH"
    extra_context = {
        "instrument_name": instrument_name,
        "dragons_location": dragons_location,
    }

    result = cookies.bake(extra_context=extra_context)

    assert result.exit_code == 0

    monkeypatch.chdir(result.project_path)

    command = ["nox", "-s", "devenv"]

    subprocess.run(command)

    assert Path(dragons_location).exists()
    assert Path(dragons_location).is_dir()
    assert list(Path(dragons_location).iterdir())


def test_conda_dev_environment(cookies, monkeypatch):
    """Test conda development environemtn"""
    instrument_name = "BLAH"
    env_name = f"{instrument_name.lower()}_dev"
    result = cookies.bake(extra_context={"instrument_name": instrument_name})

    assert result.exit_code == 0

    monkeypatch.chdir(result.project_path)

    try:
        subprocess.run(["nox", "-s", "devconda"])
        result = subprocess.run(["conda", "info", "-e"], capture_output=True)

        output = result.stdout.decode("utf-8")

        entries = output.splitlines()

        assert any(env_name in entry for entry in entries), f"Env {env_name} not found"

        script = "\n".join(
            [
                "import astrodata",
                "import gemini_instruments",
                "import geminidr",
                "import gempy",
                "import gemini_obs_db",
                "import gemini_calmgr",
                f"import {instrument_name}_instruments",
                f"import {instrument_name}_instruments.{instrument_name}",
                f"from {instrument_name}_instruments.{instrument_name} import AstroData{instrument_name.title()}",
                f"import {instrument_name}dr",
            ]
        )

        subprocess.run(["conda", "run", "python", "-c", script])

    finally:
        subprocess.run(["conda", "remove", "-n", env_name, "--all", "-y"])
