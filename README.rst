.. figure:: docs/assets/teeplot-wordmark.png
   :target: https://github.com/mmore500/teeplot
   :alt: teeplot wordmark


.. image:: https://img.shields.io/pypi/v/teeplot.svg
        :target: https://pypi.python.org/pypi/teeplot

.. image:: https://github.com/mmore500/teeplot/actions/workflows/CI.yml/badge.svg
        :target: https://github.com/mmore500/teeplot/actions/workflows/CI.yml


teeplot organizes saving data visualizations, automatically picking meaningful names based on semantic plotting variables


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
