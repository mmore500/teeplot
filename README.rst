.. figure:: docs/assets/teeplot-wordmark.png
   :target: https://github.com/mmore500/teeplot
   :alt: teeplot wordmark


*teeplot* wrangles your data visualizations out of notebooks for you
--------------------------------------------------------------------

|PyPi| |docs| |GitHub stars| |CI| |zenodo|

* Free software: MIT license
* Installation: ``python3 -m pip install teeplot``
* Documentation: https://github.com/mmore500/teeplot/blob/master/README.rst
* Repository: https://github.com/mmore500/teeplot

*teeplot*'s ``tee`` function can wrap your plotting calls to **automatically manage matplotlib file output**, picking meaningful names based on semantic plotting variables.

.. code-block:: python

    # adapted from https://seaborn.pydata.org/generated/seaborn.FacetGrid.html#seaborn.FacetGrid
    import seaborn as sns; from teeplot import teeplot as tp

    tp.tee(sns.lmplot,  # plotter
        sns.load_dataset("tips"), col="time", hue="sex", x="total_bill", y="tip",  # fwded kw/args
        teeplot_postprocess=sns.FacetGrid.add_legend)  # teeplot options

..

    ..

        .. code-block::

            teeplots/col=time+hue=sex+post=add_legend+viz=lmplot+x=total-bill+y=tip+ext=.pdf
            teeplots/col=time+hue=sex+post=add_legend+viz=lmplot+x=total-bill+y=tip+ext=.png

    .. image:: docs/assets/col=time+hue=sex+post=add_legend+viz=lmplot+x=total-bill+y=tip+ext=_padded.png


**Here's how it works:** *teeplot*'s ``tee`` function that acts as a wrapper around your plotting calls.
Give ``tee`` your plotting function (e.g., ``sns.lineplot``) as the first argument and then add the arguments you want to call it with.

*teeplot* automatically captures the function and its arguments, calls the plotter as instructed, and then it handles the matplotlib file output for you.
It generates descriptive filenames for the saved plots by extracting key information from the plot parameters and arguments.
This feature allows you to *keep track of your visualizations easily* by making the process of saving and cataloging your plots more *efficient*, *systematic* and *meaningful*, taking the hassle out of manual file management.

*teeplot* contains several advanced features, such as a ``draftmode`` flag, which will disable file output globally, and the ``teeplot_callback`` kwarg, which delays plot output to allow for figure tweaks.
Read on for details.

Contents
--------

- **Usage** : `Example 1 <#example-1>`_ | `Example 2 <#example-2>`_ | `Example 3 <#example-3>`_ | `Example 4 <#example-4>`_ | `Example 5 <#example-5>`_
- **API** : `teeplot.tee() <#teeplottee>`_ | `Module-Level Configuration <#module-level-configuration>`_ | `Environment Variables <#environment-variables>`_
- **Citing** `here <#citing>`_ | **Credits** `link <#credits>`_

Usage
-----

Example 1
^^^^^^^^^

Simple example demonstrating use with *pandas* built-in plotting.

.. code-block:: python

    # adapted from https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.box.html
    import pandas as pd; from teeplot import teeplot as tp

    age_list = [8, 10, 12, 14, 72, 74, 76, 78, 20, 25, 30, 35, 60, 85]
    df = pd.DataFrame({"gender": list("MMMMMMMMFFFFFF"), "age": age_list})

    tp.tee(df.plot.box,  # plotter...
        column="age", by="gender", figsize=(4, 3))  # ...forwarded kwargs

..

    ..

        .. code-block::

            teeplots/by=gender+column=age+viz=box+ext=.pdf
            teeplots/by=gender+column=age+viz=box+ext=.png

    .. image:: docs/assets/by=gender+column=age+viz=box+ext=_padded.png

----

Example 2
^^^^^^^^^

Example with *seaborn* showing use of ``teed`` context manager interface to allow for plot tweaks before saving.

.. code-block:: python

    # adapted from https://seaborn.pydata.org/examples/horizontal_boxplot.html
    from matplotlib import pyplot as plt
    import seaborn as sns
    from teeplot import teeplot as tp

    with tp.teed(  # plot is finalized upon leaving context
        sns.boxplot,  # plotter...
        sns.load_dataset("planets"),  # ...forwarded arg & kwargs
        x="distance", y="method", hue="method", palette="vlag",
        whis=[0, 100], width=.6,  # ... and then teeplot options
        teeplot_callback=True, teeplot_postprocess="teed.set_xscale('log')"
    ) as ax:
        ax.xaxis.grid(True)  # now some tweaks
        ax.set(ylabel="")
        sns.despine()
        plt.gcf().set_size_inches(10, 4)

..

    ..

        .. code-block::

            teeplots/hue=method+palette=vlag+post=teed-set-xscale-log+viz=boxplot+x=distance+y=method+ext=.pdf
            teeplots/hue=method+palette=vlag+post=teed-set-xscale-log+viz=boxplot+x=distance+y=method+ext=.png

    .. image:: docs/assets/hue=method+palette=vlag+post=teed-set-xscale-log+viz=boxplot+x=distance+y=method+ext=_padded.png

----

Example 3
^^^^^^^^^

Example with matplotlib, showing alternate ``teeplot_callback`` kwarg interface.
We've also used the global configuration option ``save`` to change default output format.

.. code-block:: python

    # adapted from https://matplotlib.org/stable/tutorials/pyplot.html
    from matplotlib import pyplot as plt
    import numpy as np; from teeplot import teeplot as tp
    tp.save = {".eps": True}  # make default output only .eps

    data = {'a': np.arange(50), 'c': np.random.randint(0, 50, 50),
            'd': np.random.randn(50)}
    data['b'], data['d'] = data['a'] + 10 * np.random.randn(50), np.abs(data['d']) * 100

    saveit, __ = tp.tee(  # create a callback object to finalize plot
        plt.scatter,  # plotter...
        data=data, x='a', y='b', c='c', s='d',  # ...forwarded kwargs
        teeplot_callback=True)  # teeplot options
    plt.xlabel('entry a')  # now some tweaks
    plt.ylabel('entry b')
    plt.gcf().set_size_inches(5, 3)
    saveit()  # dispatch output callback

..

    ..

        .. code-block::

            teeplots/c=c+s=d+viz=scatter+x=a+y=b+ext=.eps

    .. image:: docs/assets/c=c+s=d+viz=scatter+x=a+y=b+ext=_padded.png

----

Example 4
^^^^^^^^^

Example with *seaborn* ``FacetGrid`` demonstrating use of ``exec``'ed ``teeplot_postprocess`` that adds a ``map_dataframe`` step over the ``teed`` result value and also results in additional semantic information being added to plot filenames (under the "``post=``" key).

.. code-block:: python

    # adapted from https://seaborn.pydata.org/generated/seaborn.FacetGrid.html#seaborn.FacetGrid
    import seaborn as sns
    from teeplot import teeplot as tp

    tp.tee(
        sns.FacetGrid,  # plotter...
        sns.load_dataset("tips"),  # ...forwarded args & kwwargs
        col="time", hue="sex", aspect=1.5,
        teeplot_postprocess="teed.map_dataframe(sns.scatterplot, x='total_bill', y='tip')")

..

    ..

        .. code-block::

            teeplots/col=time+hue=sex+post=teed-map-dataframe-sns-scatterplot-x-total-bill-y-tip+viz=facetgrid+ext=.pdf
            teeplots/col=time+hue=sex+post=teed-map-dataframe-sns-scatterplot-x-total-bill-y-tip+viz=facetgrid+ext=.png

    .. image:: docs/assets/col=time+hue=sex+post=teed-map-dataframe-sns-scatterplot-x-total-bill-y-tip+viz=facetgrid+ext=_padded.png

----

Example 5
^^^^^^^^^

Demonstration of teeplot use with a custom function.
Note the function name automatically used as "``viz=``" key in output filenames.

.. code-block:: python

    # adapted from https://seaborn.pydata.org/examples/pairgrid_dotplot.html
    import seaborn as sns; from teeplot import teeplot as tp
    df = sns.load_dataset("car_crashes")

    def dot_plot(data, x_vars, y_vars):  # custom plotter
        g = sns.PairGrid(data.sort_values("total", ascending=False),
                        x_vars=x_vars, y_vars=y_vars,
                        height=5, aspect=0.66)
        g.map(sns.stripplot, size=10, orient="h", jitter=False,
            palette="flare_r", linewidth=1, edgecolor="w")
        for ax in g.axes.flat:
            ax.xaxis.grid(False)
            ax.yaxis.grid(True)


    tp.tee(
        dot_plot,  # plotter, then forwarded args/kwargs
        df[df["abbrev"].str.contains("A")], x_vars=df.columns[:-3], y_vars=["abbrev"],
        teeplot_outinclude=["x_vars", "y_vars"], teeplot_save={".eps", ".png"})

..

    ..

        .. code-block::

            teeplots/viz=dot-plot+x-vars=index-total-speeding-alcohol-not-distracted-no-previous-dtype-object+y-vars=abbrev+ext=.eps
            teeplots/viz=dot-plot+x-vars=index-total-speeding-alcohol-not-distracted-no-previous-dtype-object+y-vars=abbrev+ext=.png


    .. image:: docs/assets/viz=dot-plot+x-vars=index-total-speeding-alcohol-not-distracted-no-previous-dtype-object+y-vars=abbrev+ext=_padded.png

----

Further Examples
^^^^^^^^^^^^^^^^

Find more examples and use cases `on medium <https://medium.com/towards-data-science/an-easier-way-to-wrangle-jupyter-notebook-visualizations-620a86cd9279>`_.


API
---

``teeplot.tee()``
^^^^^^^^^^^^^^^^^

Executes a plotting function and saves the resulting plot to specified formats using a descriptive filename automatically generated from plotting function arguments.


+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Parameter                  | Description                                                                                                                                                                                                                              |
+============================+==========================================================================================================================================================================================================================================+
| ``plotter``                | The plotting function to be executed. *Required.*                                                                                                                                                                                        |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| *Additional args & kwargs* | Forwarded to the plotting function and used to build the output filename.                                                                                                                                                                |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_callback``       | If True, returns a tuple with a callback to dispatch plot save instead of immediately saving the plot after running the plotter. Default is False.                                                                                       |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_dpi``            | Resolution for rasterized components of saved plots, default is publication-quality 300 dpi.                                                                                                                                             |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_oncollision``    | Strategy for handling filename collisions: "error", "fix", "ignore", or "warn", default "warn"; inferred from environment if not specified.                                                                                              |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_outattrs``       | Dict with additional key-value attributes to include in the output filename.                                                                                                                                                             |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_outdir``         | Base directory for saving plots, default "teeplots".                                                                                                                                                                                     |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_outinclude``     | Attribute keys to always include, if present, in the output filename.                                                                                                                                                                    |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_outexclude``     | Attribute keys to always exclude, if present, from the output filename.                                                                                                                                                                  |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_postprocess``    | Actions to perform after plotting but before saving. Can be a string of code to ``exec`` or a callable function. If a string, it's executed with access to ``plt`` and ``sns`` (if installed), and the plotter return value as ``teed``. |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_save``           | File formats to save the plots in. Defaults to global settings if ``True``, all output suppressed if ``False``. Default global setting is ``{" .png", ".pdf"}``. Supported: ".eps", ".png", ".pdf", ".ps", ".svg".                       |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_show``           | Dictates whether ``plt.show()`` should be called after plot is saved. If True, the plot is displayed using ``plt.show()``. Default behavior is to display if an interactive environment is detected (e.g., a notebook).                  |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_subdir``         | Optionally, subdirectory within the main output directory for plot organization.                                                                                                                                                         |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_transparent``    | Option to save the plot with a transparent background, default True.                                                                                                                                                                     |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``teeplot_verbose``        | Toggles printing of saved filenames, default True.                                                                                                                                                                                       |
+----------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Return Value**: returned result from plotter call if ``teeplot_callback`` is ``False``, otherwise tuple of save-plot callback and result from plotter call.


Module-Level Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^

-  ``teeplot.draftmode``: A boolean indicating whether to suppress output to all file formats.
-  ``teeplot.oncollision``: Default strategy for handling filename collisions, options are 'error', 'fix', 'ignore', or 'warn'.
-  ``teeplot.save``: A dictionary mapping file formats (e.g., ".png") to default save behavior as ``True`` (always output), ``False`` (never output), or ``None`` (defer to call kwargs).

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

-  ``TEEPLOT_ONCOLLISION``: Configures the default collision handling strategy. See ``teeplot_oncollision`` kwarg
-  ``TEEPLOT_DRAFTMODE``: If set, enables draft mode globally.
-  ``TEEPLOT_<FORMAT>``: Boolean flags that determine default behavior for each format (e.g., ``EPS``, ``PNG``, ``PDF``, ``PS``, ``SVG``); "defer" defers to call kwargs.

Citing
------

If *teeplot* contributes to a scholarly publication, please cite it as

    Matthew Andres Moreno. (2023). mmore500/teeplot. Zenodo. https://doi.org/10.5281/zenodo.10440670

.. code:: bibtex

    @software{moreno2023teeplot,
      author = {Matthew Andres Moreno},
      title = {mmore500/teeplot},
      month = dec,
      year = 2023,
      publisher = {Zenodo},
      doi = {10.5281/zenodo.10440670},
      url = {https://doi.org/10.5281/zenodo.10440670}
    }

And don't forget to leave a `star on GitHub <https://github.com/mmore500/teeplot/stargazers>`__!

Credits
-------

Output filenames are constructed using the `keyname <https://github.com/mmore500/keyname>`_ package.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

.. |PyPi| image:: https://img.shields.io/pypi/v/teeplot.svg
   :target: https://pypi.python.org/pypi/teeplot
.. |CI| image:: https://github.com/mmore500/teeplot/actions/workflows/CI.yml/badge.svg
   :target: https://github.com/mmore500/teeplot/actions
.. |GitHub stars| image:: https://img.shields.io/github/stars/mmore500/teeplot.svg?style=round-square&logo=github&label=Stars&logoColor=white
   :target: https://github.com/mmore500/teeplot
.. |docs| image:: https://img.shields.io/badge/docs%20-%20readme%20-%20fedcba?logo=github
   :target: https://github.com/mmore500/teeplot/blob/master/README.rst
.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.10440670.svg
   :target: https://doi.org/10.5281/zenodo.10440670
