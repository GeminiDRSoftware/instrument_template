"""Tests for the adclass.

This should be defined in
{{ cookiecutter.instrument_name }}_instruments/adclass.py.
"""

from {{ cookiecutter.instrument_name }} import AstroData{{ cookiecutter.instrument_name_title }}


def test_adclass_exists():
    """Just tests that the adclass has imported correctly.

    Mostly here for the template, you can remove if it's
    causing a problem, though it really shouldn't be.
    """
    assert AstroData{{ cookiecutter.instrument_name_title }}
