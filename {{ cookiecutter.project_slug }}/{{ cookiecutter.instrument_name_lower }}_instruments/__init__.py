# Import the modules under this package to trigger any class
# registering that may be needed.

import astrodata  # noqa: F401

from . import {{ cookiecutter.instrument_name_lower }}  # noqa: F401
