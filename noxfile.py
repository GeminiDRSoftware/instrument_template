"""Noxfile meant for the cookiecutter repository itself."""

from pathlib import Path
import shutil

import nox

nox.options.sessions = ["cookiecutter_tests"]


@nox.session(python="3.12")
def cookiecutter_tests(session: nox.Session):
    """Tests for the cookiecutter itself."""
    # Remove cache files for nox if they exist in the template directory.
    rmdirs = [".nox", ".pytest_cache"]
    template_path = Path("{{cookiecutter.project_slug}}")

    for rmdir in rmdirs:
        if (template_path / rmdir).exists():
            session.log(f"Removing {rmdir} directory.")
            shutil.rmtree(template_path / rmdir)

    session.install("pytest", "pytest-cookies", "hypothesis")
    session.run("pytest", "tests/", *session.posargs)


@nox.session
def lint(session: nox.Session):
    """Run linters. Since cookiecutter formatting (double curly braces) is not
    supported by ruff, we will escape those values specifically for ruff.
    """
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
