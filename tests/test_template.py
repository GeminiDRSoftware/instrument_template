"""Tests the template setup."""

from itertools import chain
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def test_no_igrins_references(cookies):
    """There should not be any reference to igrins in the template."""
    for root, directories, files in Path(".").walk():
        for path in (root / base for base in chain(directories, files)):
            # Skip correction scipt
            if "_correct_all_igrins_ref" in str(path):
                continue

            # Skip this file
            if path.resolve() == Path(__file__).resolve():
                continue

            # Ignore caches
            if "cache" in str(path):
                continue

            # Ignore .git
            if ".git/" in str(path):
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

            for i, line in enumerate(lines):
                assert (
                    "igrins" not in line.lower()
                ), f"IGRINS ref found ({path}::{i}):\n{line}"
