"""
Recipes available to data with tags ['{{ cookiecutter.instrument_name }}', 'ECHELLE']
Default is "reduce".
"""

recipe_tags = {"{{ cookiecutter.instrument_name }}", "ECHELLE"}


def reduce(p):
    """
    This recipe processes {{ cookiecutter.instrument_name }} echelle science data.

    Parameters
    ----------
    p : PrimitivesCORE object
        A primitive set matching the recipe_tags.
    """

    p.prepare()
    p.addDQ()
    p.addVAR(read_noise=True)
    p.ADUToElectrons()
    p.addVAR(poisson_noise=True)
    # ....
    # ....
    return


_default = reduce
