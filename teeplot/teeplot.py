import hashlib
from keyname import keyname as kn
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib
from slugify import slugify

def _digest(data):

    # also considered https://newbedev.com/how-to-generate-a-hash-or-checksum-value-on-python-dataframe-created-from-a-fixed-width-file
    # which is slower
    if isinstance(data, pd.DataFrame):
        # adapted from https://stackoverflow.com/a/47800021
        return hashlib.sha256(
            pd.util.hash_pandas_object(data, index=True).values
        ).hexdigest()
    elif isinstance(data, pd.core.series.Series):
        # adapted from https://stackoverflow.com/a/47800021
        return hashlib.sha256(
            pd.util.hash_pandas_object(data, index=True).values
        ).hexdigest()
    elif isinstance(data, np.ndarray):
        # adapted from https://stackoverflow.com/a/806342
        view = data.view(np.uint8)
        return hashlib.sha256(view).hexdigest()
    else:
        return hashlib.sha256( data ).hexdigest()


def tee(plotter, *args, **kwargs):

    # enable TrueType fonts
    # see https://gecco-2021.sigevo.org/Paper-Submission-Instructions
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    res = plotter(
        *args,
        **{
            k : v
            for k, v in kwargs.items()
            if k != 'teeplot_outattrs'
        }
    )

    attr_maker = lambda ext: {
        **{
            slugify(k) : slugify(v)
            for k, v in kwargs.items()
            if isinstance(v, str)
        },
        **{
            'viz' : slugify(plotter.__name__),
            'ext' : ext,
        },
        **{
            k : v
            for k, v in kwargs.get('teeplot_outattrs', {}).items()
            if k != '_datafordigest'
        },
        **(
            {'_datadigest' : _digest( kwargs['data'] )[:16]}
            if 'data' in kwargs
            else {'_datadigest' : _digest(
                kwargs['teeplot_outattrs']['_datafordigest']
            )[:16]}
            if '_datafordigest' in kwargs.get('teeplot_outattrs', {})
            else {'_datadigest' : _digest( np.concatenate([
                kwargs.get('x', []),
                kwargs.get('y', []),
                kwargs.get('hue', []),
                kwargs.get('size', []),
                kwargs.get('style', []),
            ]) )[:16]}
            if any(q in kwargs for q in ['x', 'y', 'hue', 'size', 'style'])
            else {}
        ),

    }
    out_filenamer = lambda ext: kn.pack({
        k : v
        for k, v in attr_maker(ext).items()
        if not k.startswith('_')
    })
    out_metamaker = lambda ext: kn.pack({
        k : v
        for k, v in attr_maker(ext).items()
        if k.startswith('_')
    })

    out_folder = 'teeplots'
    pathlib.Path(
        out_folder,
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    for ext, dpi in ('.pdf', 'figure'), ('.png', 300):

        out_path = f'teeplots/{out_filenamer(ext)}'
        print(out_path)
        plt.savefig(
            out_path,
            bbox_inches='tight',
            transparent=True,
            dpi=dpi,
        )

        with open(f'teeplots/{out_filenamer(ext)}.meta', 'w') as file:
            file.write( out_metamaker(ext) )

    return res
