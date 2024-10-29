"""This is the noxfile for the {{ cookiecutter.instrument_name }} package.

For a list of sessions and their descriptions, run:

.. code-block::
    nox -l

Please note that, to prevent undesirable execution, there are no default
sessions, so running ``nox`` in isolation will do nothing.
"""

from __future__ import annotations

from pathlib import Path

import nox

nox.options.sessions = []
nox.options.error_on_external_run = True

DRAGONS_URL = R"https://github.com/GeminiDRSoftware/DRAGONS"
CALMGR_URL = R"https://github.com/GeminiDRSoftware/GeminiCalMgr.git@release/1.1.x"
OBSDB_URL = R"https://github.com/GeminiDRSoftware/GeminiObsDB.git@release/1.0.x"


def install_dragons(session: nox.Session, python: Path | None = None):
    """Install dragons into the given session.

    If python is not None, it assumes it is a path to the
    correct python binary to use.
    """
    if python:
        session.run(
            str(python),
            "-m",
            "pip",
            "install",
            f"git+{DRAGONS_URL}",
            external=True,
        )

        session.run(
            str(python),
            "-m",
            "pip",
            "install",
            f"git+{CALMGR_URL}",
            f"git+{OBSDB_URL}",
            external=True,
        )

        return

    session.install(f"git+{DRAGONS_URL}")
    session.install(f"git+{CALMGR_URL}", f"git+{OBSDB_URL}")


@nox.session(venv_backend=None)
def devenv(session: nox.Session):
    """Create a development environment.

    This will perform the following steps:

    + Create a new virtual environment at ``venv/``
    + Install DRAGONS:
        + If DRAGONS does not exist locally, clone it.
        + Otherwise, perform a ``git fetch && git pull``
    + Install any other dependencies needed.
    """
    session.run(
        "python",
        "-m",
        "venv",
        "venv/",
        "--clear",
        "--upgrade-deps",
        "--prompt",
        "{{ cookiecutter.instrument_name_lower }}_env",
        external=True,
    )

    venv_loc = Path("venv")
    venv_python = venv_loc / "bin" / "python"

    # Install DRAGONS
    install_dragons(session, python=venv_python)

    requirements_file = Path("requirements.txt")

    session.run(
        venv_python,
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements_file),
        external=True,
    )

    venv_activate = venv_loc / "bin" / "activate"

    session.log(
        f"Successfully created virtual environment at {venv_loc}! "
        f"To activate your environment, run: \n"
        f"     source {venv_activate}\n"
    )

    session.notify("install_pre_commit_hooks")


@nox.session()
def install_pre_commit_hooks(session: nox.Session):
    """Installs pre-commit hooks."""
    session.install("pre-commit")
    session.run("pre-commit", "install")


@nox.session()
def tests(session: nox.Session):
    """Run all tests for this repository.

    Assumes a test structure as follows:

    + All test files should be named ``test_(some_name).py``
        + See pytest documentation for details.
    + There are example test files for "null checks" -- checks that should run
      on an empty repository.
        + We do not recommend deleting these; they may prove useful checks in the
          future, and don't take much time to run.
    """
    install_dragons(session)
    session.install("pytest")

    session.run("pytest", *session.posargs)


@nox.session()
def lint(session: nox.Session):
    """Lint using pre-commit hooks."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")
