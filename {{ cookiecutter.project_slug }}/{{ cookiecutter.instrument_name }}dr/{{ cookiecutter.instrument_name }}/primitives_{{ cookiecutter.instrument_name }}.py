#
#                                                                       DRAGONS
#
#                                                         primitives_{{ cookiecutter.instrument_name_lower }}.py
# ------------------------------------------------------------------------------

from gempy.gemini import gemini_tools as gt

from geminidr.gemini.primitives_gemini import Gemini

from . import parameters_{{ cookiecutter.instrument_name_lower }}

from .lookups import timestamp_keywords as {{ cookiecutter.instrument_name_lower }}_stamps

from recipe_system.utils.decorators import parameter_override
# ------------------------------------------------------------------------------


@parameter_override
class {{ cookiecutter.instrument_name_title }}(Gemini):
    """
    This class inherits from the level above.  Any primitives specific
    to {{ cookiecutter.instrument_name }} can go here.
    """

    tagset = {"GEMINI", "{{ cookiecutter.instrument_name }}"}

    def __init__(self, adinputs, **kwargs):
        super({{ cookiecutter.instrument_name_title }}, self).__init__(adinputs, **kwargs)
        self._param_update(parameters_{{ cookiecutter.instrument_name_lower }})
        # Add {{ cookiecutter.instrument_name }} specific timestamp keywords
        self.timestamp_keys.update({{ cookiecutter.instrument_name_lower }}_stamps.timestamp_keys)

    def someStuff(self, adinputs=None, **params):
        """
        Write message to screen.  Test primitive.

        Parameters
        ----------
        adinputs
        params

        Returns
        -------

        """
        log = self.log
        log.debug(gt.log_message("primitive", self.myself(), "starting"))

        for ad in adinputs:
            log.status("I see " + ad.filename)

            gt.mark_history(ad, primname=self.myself(), keyword="TEST")
            ad.update_filename(suffix=params["suffix"], strip=True)

        return adinputs

    @staticmethod
    def _has_valid_extensions(ad):
        """Check that the AD has a valid number of extensions."""

        # this needs to be updated at appropriate.
        return len(ad) in [1]
