============
teeplot
============


.. image:: https://img.shields.io/pypi/v/teeplot.svg
        :target: https://pypi.python.org/pypi/teeplot

.. image:: https://img.shields.io/travis/mmore500/teeplot.svg
        :target: https://travis-ci.com/mmore500/teeplot

.. image:: https://readthedocs.org/projects/teeplot/badge/?version=latest
        :target: https://teeplot.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




teeplot automatically saves a copy of rendered Jupyter notebook plots


* Free software: MIT license
* Documentation: https://teeplot.readthedocs.io.


.. code-block:: python3

  from teeplot import teeplot as tp
  import seaborn as sns

  # adapted from https://seaborn.pydata.org/examples/errorband_lineplots.html
  tp.tee(
    sns.lineplot,
    x='timepoint',
    y='signal',
    hue='region',
    style='event',
    data=sns.load_dataset('fmri'),
    teeplot_outattrs={
      'additional' : 'metadata',
      'for' : 'output-filename',
    },
  )

  tp.tee(
    sns.catplot,
    data=sns.load_dataset('penguins'),
    kind='bar',
    x='species',
    y='body_mass_g',
    hue='sex',
    ci='sd',
    palette='dark',
    alpha=.6,
    height=6,
  )

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
