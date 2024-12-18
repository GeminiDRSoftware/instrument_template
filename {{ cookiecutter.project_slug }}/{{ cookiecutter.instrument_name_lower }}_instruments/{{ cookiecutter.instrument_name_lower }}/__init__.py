__all__ = ["AstroData{{ cookiecutter.instrument_name }}"]

from astrodata import factory
from gemini_instruments.gemini import addInstrumentFilterWavelengths
from .adclass import AstroData{{ cookiecutter.instrument_name_title }}
from .lookup import filter_wavelengths

factory.addClass(AstroData{{ cookiecutter.instrument_name_title }})

addInstrumentFilterWavelengths("{{ cookiecutter.instrument_name }}", filter_wavelengths)
