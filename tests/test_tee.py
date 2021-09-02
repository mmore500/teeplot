#!/usr/bin/env python

'''
`tee` tests for `teeplot` package.
'''

import numpy as np
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
        },
    )

    assert os.path.exists(
        'teeplots/additional=metadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext=.pdf',
    )

    assert os.path.exists(
        'teeplots/additional=metadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext=.png',
    )

def test_ndarray():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    tp.tee(
        sns.lineplot,
        x=x,
        y=y,
        sort=False,
        lw=1,
    )

    assert os.path.exists(
        'teeplots/viz=lineplot+ext=.pdf',
    )

    assert os.path.exists(
        'teeplots/viz=lineplot+ext=.png',
    )

def test_datafordigest():

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
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

    assert os.path.exists(
        'teeplots/additional=metadata+viz=lineplot+ext=.pdf',
    )

    assert os.path.exists(
        'teeplots/additional=metadata+viz=lineplot+ext=.png',
    )
