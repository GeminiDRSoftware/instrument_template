"""Tests the template setup."""

from itertools import chain
import logging
import os
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


def test_conda_dev_environment(cookies, monkeypatch):
    """Test conda development environemtn"""
