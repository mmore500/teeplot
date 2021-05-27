from keyname import keyname as kn
import matplotlib
import matplotlib.pyplot as plt
import pathlib
from slugify import slugify

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
        **kwargs.get('teeplot_outattrs', {}),
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
