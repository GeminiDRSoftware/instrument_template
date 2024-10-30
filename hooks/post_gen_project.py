"""Post-generation hooks for the project."""

import subprocess


def git_init():
    """Initialize a git repository here, and make the initial commit to it."""
    init_command = ["git", "init"]
    add_files = ["git", "add", "."]
    first_commit = ["git", "commit", "-m", "Initial commit."]

    subprocess.run(init_command)
    subprocess.run(add_files)
    subprocess.run(first_commit)


def main():
    """This function runs after the repository is generated.

    This means all names are filled in, all directories and files generated
    and placed where they're expected to be.
    """
    git_init()


if __name__ == "__main__":
    main()
