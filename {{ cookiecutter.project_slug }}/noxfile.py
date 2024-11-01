"""This is the noxfile for the {{ cookiecutter.instrument_name }} package.

For a list of sessions and their descriptions, run:

.. code-block::
    nox -l

Please note that, to prevent undesirable execution, there are no default
sessions, so running ``nox`` in isolation will do nothing.
"""

from __future__ import annotations

from pathlib import Path
import re

import nox

nox.options.sessions = []
nox.options.error_on_external_run = True

DRAGONS_URL = R"https://github.com/GeminiDRSoftware/DRAGONS"
CALMGR_URL = R"https://github.com/GeminiDRSoftware/GeminiCalMgr.git@release/1.1.x"
OBSDB_URL = R"https://github.com/GeminiDRSoftware/GeminiObsDB.git@release/1.0.x"

DRAGONS_BRANCH = "{{ cookiecutter.dragons_branch }}"
DRAGONS_LOCATION = "{{ cookiecutter.dragons_location }}"


def check_dragons_version(session: nox.Session):
    """Check if dragons is the expected version."""
    with session.chdir(DRAGONS_LOCATION):
        result = session.run("git", "branch", silent=True, external=True)

        match = re.match(r"^.*\s+(\w+)\s*.*$", result)

        if not match:
            raise ValueError("No DRAGONS branch found.")

        branch_name = match.group(1)

        if branch_name != DRAGONS_BRANCH:
            session.warn(f"Unexpected git branch: {branch_name} (not {DRAGONS_BRANCH})")

        else:
            session.log(f"Found correct branch: {branch_name}")

        result = session.run("git", "fetch", "--dry-run", silent=True, external=True)

        if result:
            session.warn(
                f"Your DRAGONS version is not up-to-date.\n"
                f"Please check the latest version at:\n"
                f"    {DRAGONS_URL}\n"
                f"And, if you would like to update, run:\n\n"
                f"    git fetch && git pull\n\n"
                f" We strongly encourage you do this regularly in case of "
                f" important updates."
            )

        else:
            session.log("DRAGONS is up to date!")


def install_dragons(session: nox.Session, python: Path | None = None):
    """Install dragons into the given session.

    If python is not None, it assumes it is a path to the
    correct python binary to use.
    """
    dragons_path = Path(DRAGONS_LOCATION)

    if not dragons_path.exists():
        # Clone dragons locally
        session.run(
            "git",
            "clone",
            "-b",
            DRAGONS_BRANCH,
            DRAGONS_URL,
            str(dragons_path),
            external=True,
        )

    check_dragons_version(session)

    if python:
        session.run(
            str(python),
            "-m",
            "pip",
            "install",
            "-e",
            str(dragons_path),
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

    session.install("-e", str(dragons_path))
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


@nox.session(venv_backend=None)
def devconda(session: nox.Session):
    """Create a conda development environment."""
    env_name = "{{ cookiecutter.instrument_name_lower }}_dev"
    session.run(
        "conda",
        "create",
        "--yes",
        "--force",
        "-n",
        env_name,
        "-c",
        "conda-forge",
        "python=3.12",
        external=True,
    )

    result = session.run("conda", "info", "-e", silent=True, external=True)

    env_path = None
    for line in result.splitlines():
        line = line.split("#")[0]

        columns = line.split()

        if len(columns) != 2:
            continue

        name, path = columns

        if name == env_name:
            env_path = Path(path)
            break

    assert env_path is not None, f"Could not find environment {env_name}"

    env_python = env_path / "bin" / "python"

    install_dragons(session, python=env_python)

    session.log("Conda environemtn generated, to activate run:")
    session.log(f"   conda activate {env_name}")


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

    session.run("pytest", "tests", *session.posargs)


@nox.session()
def lint(session: nox.Session):
    """Lint using pre-commit hooks."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")
