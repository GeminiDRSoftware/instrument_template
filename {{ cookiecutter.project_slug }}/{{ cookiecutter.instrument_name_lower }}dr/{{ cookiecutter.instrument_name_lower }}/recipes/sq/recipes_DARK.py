"""
Recipes available to data with tags ['{{ cookiecutter.instrument_name }}', 'CAL', 'DARK'].
Default is "makeProcessedDark"
"""

recipe_tags = {"{{ cookiecutter.instrument_name }}", "CAL", "DARK"}


def makeProcessedDark(p):
    """
    This recipe performs the standardization and corrections needed to convert
    the raw input dark images into a single stacked dark image. This output
    processed dark is stored on disk and its information added to the calibration
    database using storeProcessedDark and has a name
    equal to the name of the first input bias image with "_bias.fits" appended.

    Parameters
    ----------
    p : PrimitivesCORE object
        A primitive set matching the recipe_tags.
    """

    p.prepare()
    p.addDQ()
    p.addVAR(read_noise=True)
    # ....
    p.storeProcessedDark()
    return


_default = makeProcessedDark
