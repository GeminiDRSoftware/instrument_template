from astrodata import astro_data_tag, astro_data_descriptor, TagSet
from . import lookup
from gemini_instruments.gemini import AstroDataGemini


class AstroData{{ cookiecutter.instrument_name }}(AstroDataGemini):
    # single keyword mapping.  add only the ones that are different
    # from what's already defined in AstroDataGemini.

    __keyword_dict = dict()

    @staticmethod
    def _matches_data(source):
        return source[0].header.get("INSTRUME", "").upper() == "{{ cookiecutter.instrument_fits_name }}"

    @astro_data_tag
    def _tag_instrument(self):
        return TagSet(["{{ cookiecutter.instrument_name }}", "VERSION2"])

    @astro_data_tag
    def _tag_flat(self):
        # if self.phu.get('SOMEKEYWORD') == 'Flat_or_something':
        #    return TagSet(['FLAT', 'CAL']])
        pass

    # ------------------
    # Common descriptors
    # ------------------

    @astro_data_descriptor
    def gain(self):
        """
        Returns the gain (electrons/ADU) from lookup table

        Returns
        -------
        float/list
            gain
        """
        return lookup.array_properties.get("gain")
