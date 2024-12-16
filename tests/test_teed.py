#!/usr/bin/env python

'''
`tee` tests for `teeplot` package.
'''

from matplotlib import pyplot as plt
import numpy as np
from keyname import keyname as kn
import os
import pytest
import seaborn as sns

from teeplot import teeplot as tp

def test():

    with tp.teed(
        sns.lineplot,
        x='timepoint',
        y='signal',
        hue='region',
        style='event',
        data=sns.load_dataset('fmri'),
        teeplot_outattrs={
          'additional' : 'teedmetadata',
          'for' : 'output-filename',
          '_one-for' : 'exclusion',
        },
    ):
        pass

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'additional=teedmetadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext={ext}'),
        )


@pytest.mark.parametrize("format", [".png", ".pdf", ".ps", ".eps", ".svg"])
def test_outformat(format):

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    with tp.teed(
        sns.lineplot,
        x=x,
        y=y,
        sort=False,
        lw=1,
        teeplot_outattrs={
          'outformat' : 'teedmetadata',
        },
        teeplot_subdir='mydirectory',
        teeplot_save={format},
    ):
        pass

    assert os.path.exists(
        os.path.join('teeplots', 'mydirectory', f'outformat=teedmetadata+viz=lineplot+ext={format}'),
    )

def test_postprocess_callable():

    with tp.teed(
        sns.lineplot,
        x='signal',
        y='timepoint',
        hue='region',
        style='event',
        data=sns.load_dataset('fmri'),
    ) as teed:
        plt.viridis()

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'hue=region+style=event+viz=lineplot+x=signal+y=timepoint+ext={ext}'),
        )


def test_callback():

    with tp.teed(
        sns.lineplot,
        x='timepoint',
        y='signal',
        hue='region',
        data=sns.load_dataset('fmri'),
    ) as ax:
        ax.set_yscale('log')

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'hue=region+viz=lineplot+x=timepoint+y=signal+ext={ext}'),
        )
