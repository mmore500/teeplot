#!/usr/bin/env python

'''
`tee` tests for `teeplot` package.
'''

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
