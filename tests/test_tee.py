#!/usr/bin/env python

'''
`tee` tests for `teeplot` package.
'''

import numpy as np
from keyname import keyname as kn
import os
import pytest
import seaborn as sns

from teeplot import teeplot as tp

def test():

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
          '_one-for' : 'exclusion',
        },
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'additional=metadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext={ext}'),
        )


def test_ndarray():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    tp.tee(
        sns.lineplot,
        x=x,
        y=y,
        sort=False,
        lw=1,
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'viz=lineplot+ext={ext}'),
        )

def test_datafordigest():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    tp.tee(
        sns.lineplot,
        x=x,
        y=y,
        sort=False,
        lw=1,
        teeplot_outattrs={
          'additional' : 'metadata',
          '_datafordigest' : x,
        },
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'additional=metadata+viz=lineplot+ext={ext}'),
        )


def test_outpath():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    tp.tee(
        sns.lineplot,
        x=x,
        y=y,
        sort=False,
        lw=1,
        teeplot_outattrs={
          'additional' : 'metadata',
        },
        teeplot_subdir='mydirectory',
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', 'mydirectory', f'additional=metadata+viz=lineplot+ext={ext}'),
        )

def test_longname():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    tp.tee(
        sns.lineplot,
        x=x,
        y=y,
        sort=False,
        lw=1,
        teeplot_outattrs={
          f'additional{i}' : 'metadata'
          for i in range(30)
        },
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            kn.chop(
                os.path.join('teeplots', kn.pack({
                      f'additional{i}' : 'metadata'
                      for i in range(30)
                    }) + f'+viz=lineplot+ext={ext}'),
            )
        )

@pytest.mark.parametrize("oncollision", ["warn", "ignore"])
def test_oncollision_warn_ignore(oncollision: str):

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    for i in range(2):
        tp.tee(
            sns.lineplot,
            x=x,
            y=y,
            sort=False,
            lw=i+1,
            teeplot_oncollision=oncollision,
            teeplot_outattrs={
            'additional' : 'metadata',
            },
            teeplot_subdir='mydirectory',
        )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', 'mydirectory', f'additional=metadata+viz=lineplot+ext={ext}'),
        )


def test_oncollision_error():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    with pytest.raises(RuntimeError):
        for i in range(2):
            tp.tee(
                sns.lineplot,
                x=x,
                y=y,
                sort=False,
                lw=i+1,
                teeplot_oncollision="error",
                teeplot_outattrs={
                'additional' : 'metadata',
                },
                teeplot_subdir='mydirectory',
            )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', 'mydirectory', f'additional=metadata+viz=lineplot+ext={ext}'),
        )


def test_oncollision_fix():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    for i in range(2):
        tp.tee(
            sns.lineplot,
            x=x,
            y=y,
            sort=False,
            lw=i+1,
            teeplot_oncollision="fix",
            teeplot_outattrs={
            'additional' : 'metadata__',
            },
            teeplot_subdir='mydirectory',
        )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', 'mydirectory', f'additional=metadata__+viz=lineplot+#=1+ext={ext}'),
        )
