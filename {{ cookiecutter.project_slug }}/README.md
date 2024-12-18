# `{{ cookiecutter.instrument_name }}` Data Reduction package

You've initialized a new project template using the DRAGONS instrument template.
$This template it meant to help with onboarding your pipeline to the DRAGONS
ecosystem.

To get started, read through the following information information.

# Quickstart to building your pipeline

## Step 1: Confirm the contents of this directory

Make sure everything you expect is here. If you don't know what to expect, you
can compare to the [project slug][project_slug_link].

## Step 2: Read important documentation

There are several `README.md` files spread throughout this repo. They are kept
in their specific places for the purposes of our own organization and to avoid
them getting deleted prematurely.

If this is your first time working on a DRAGONS instrument package, please take
the time to read through them, or at least familiarize yourself with their
locations for when you do need to read them. If you have access to `find`, you
can just use:

```bash
find . -type f -name "README.md"
```

These files should cover specific nuances of the code.

## Step 3: Create a development environment

We've created some automations for generating development environments for your
machine. It ensures you're using the development version of DRAGONS and
downloads the appropriate dependencies.

We use `nox` for the purposes of automation. To use `nox`, you'll need to
install it. We strongly encourage you install it using [`pipx`][pipx_link], but
you can do what you'd like.

- **To install using [`pipx`][pipx_link] (recommended):**

```bash
pipx install nox
```

- To install using `pip`:

```bash
python -m pip install nox
```

Once installed, to create your new development environment run:

```bash
nox -s devenv
```

This enters a `nox` session that sets up a local `virtualenv`, located at
`./venv`, that you can use as a development environment. To start the virtual
environment, run

```bash
source venv/bin/activate
```

If you ever want to create a fresh environment, you can just run `nox -s devenv`
again. It will create a new environment from scratch.

### What if I want to use `conda`?

You can create a conda development environment as well, by running:

```bash
nox -s devconda
```

This creates a conda environment with the name
`{{ cookiecutter.instrument_name_lower }}_dev`, and can be activated using:

```bash
conda activate {{ cookiecutter.instrument_name_lower }}_dev
```

### What if I need any extra dependencies?

There's a `requirements.txt` file that can also be installed. _However_, we ask
you reach out before declaring new dependencies of any kind (including special
dependencies).

### What about testing?

Tests are also run through `nox`:

```bash
nox -s tests
```

This will run `pytest` for you in an isolated environment, which ensures no
global or external dependencies sneak in.

### What about linting?

You can lint your code manually using `nox` by running

```bash
nox -s lint
```

This will run [`pre-commit`][pre-commit install] over your code. It is already
installed in your development environment, and the development environment setup
also installs `pre-commit` hooks that run automatically before you commit your
changes.

## Step 4: Explore DRAGONS developer documentation

We encourage developers to familiarize themselves with the layout of the
[DRAGONS documentation][dragons docs], especially:

- [AstroData developer documentation][astrodata dev docs]
- [Recipe System developer documentation][recipe dev docs]

## Step 5: Start coding and ask questions!

If you have any questions, at any time, please reach out to the DRAGONS team!

If you have any questions or comments about this template, please
[raise an issue][github_issues_page].

### Can I get rid of all the READMEs?

At this point, yes! They will be available (in non-templated form) in the
[`{{ cookiecutter.project_slug }}/` directory of the template repo!][project_slug_link].
Don't forget to write your own documentation!

[astrodata dev docs]: https://dragons.readthedocs.io/projects/astrodata/en/v3.2.0/progmanual/index.html
[dragons docs]: https://dragons.readthedocs.io/en/v3.2.0/
[github_issues_page]: https://github.com/GeminiDRSoftware/instrument_template/issues
[pipx_link]: https://pipx.pypa.io/stable/
[pre-commit install]: https://pre-commit.com/
[project_slug_link]: https://github.com/GeminiDRSoftware/instrument_template/tree/main/%7B%7B%20cookiecutter.project_slug%20%7D%7D
[recipe dev docs]: https://dragons.readthedocs.io/projects/recipe-system-prog-manual/en/v3.2.0/
