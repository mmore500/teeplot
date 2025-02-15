#!/usr/bin/env python

'''
`tee` tests for `teeplot` package.
'''

import functools
import os

import numpy as np
import pytest
import seaborn as sns

from teeplot import teeplot as tp


@tp.teewrap(
    teeplot_outattrs={
      'additional' : 'teedmetadata',
      'for' : 'output-filename',
      '_one-for' : 'exclusion',
    },
)
@functools.wraps(sns.lineplot)
def teed_snslineplot_outattrs(*args, **kwargs):
    return sns.lineplot(*args, **kwargs)

def test():

    teed_snslineplot_outattrs(
        x='timepoint',
        y='signal',
        hue='region',
        style='event',
        data=sns.load_dataset('fmri'),
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'additional=teedmetadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext={ext}'),
        )


@pytest.mark.parametrize("format", [".png", ".pdf", ".ps", ".eps", ".svg"])
def test_outformat(format):

    # adapted from https://seaborn.pydata.org/generated/seaborn.lineplot.html
    np.random.seed(1)
    x, y = np.random.normal(size=(2, 5000)).cumsum(axis=1)

    @tp.teewrap(
        teeplot_outattrs={
          'outformat' : 'teedmetadata',
        },
        teeplot_subdir='mydirectory',
        teeplot_save={format},
    )
    @functools.wraps(sns.lineplot)
    def teed_lineplot_outformat(*args, **kwargs):
        return sns.lineplot(*args, **kwargs)

    teed_lineplot_outformat(
        x=x,
        y=y,
        sort=False,
        lw=1,
    )

    assert os.path.exists(
        os.path.join('teeplots', 'mydirectory', f'outformat=teedmetadata+viz=lineplot+ext={format}'),
    )


@tp.teewrap(teeplot_outinclude=['a', 'b'])
@functools.wraps(sns.lineplot)
def teed_snslineplot_extra_args(*args, a, b, **kwargs):
    return sns.lineplot(*args, **kwargs)


@pytest.mark.parametrize('a', [False, 1, 1])
@pytest.mark.parametrize('b', ['asdf', ''])
def test_included_outattrs(a, b):

    teed_snslineplot_extra_args(
        a=a, 
        b=b,
        x='timepoint',
        y='signal',
        hue='region',
        data=sns.load_dataset('fmri'),
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            os.path.join('teeplots', f'a={a}+b={b}+hue=region+viz=lineplot+x=timepoint+y=signal+ext={ext}'.lower()),
        )
