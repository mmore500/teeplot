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
          '_one-for' : 'the-meta',
        },
    )

    for ext in '.pdf', '.png':
        assert os.path.exists(
            f'teeplots/additional=metadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext={ext}',
        )
        with open(
            f'teeplots/additional=metadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext={ext}.meta',
            'r',
        ) as file:
            assert '_one-for=the-meta' in file.read()
        # don't assert the exact digest,
        # because the fmri dataset appears to vary between versions?
        with open(
            f'teeplots/additional=metadata+for=output-filename+hue=region+style=event+viz=lineplot+x=timepoint+y=signal+ext={ext}.meta',
            'r',
        ) as file:
            assert '_datadigest=' in file.read()


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
            f'teeplots/viz=lineplot+ext={ext}',
        )
        with open(
            f'teeplots/viz=lineplot+ext={ext}.meta',
            'r',
        ) as file:
            assert '_datadigest=011789ddade2f359' in file.read()

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
            f'teeplots/additional=metadata+viz=lineplot+ext={ext}',
        )

        with open(
            f'teeplots/additional=metadata+viz=lineplot+ext={ext}.meta',
            'r',
        ) as file:
            assert '_datadigest=1053487e16d654f6' in file.read()
