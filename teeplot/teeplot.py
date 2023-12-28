import hashlib
from keyname import keyname as kn
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pathlib
from slugify import slugify


def _is_running_on_ci():
    ci_envs = ['CI', 'TRAVIS', 'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL']
    return any(env in os.environ for env in ci_envs)


def tee(
    plotter,
    *args,
    teeplot_outattrs={},
    teeplot_outdir="teeplots",
    teeplot_save=None,
    teeplot_subdir='.',
    teeplot_transparent=True,
    **kwargs
):

    if teeplot_save is None:
        if "TEEPLOT_DRAFT_MODE" in os.environ:
            teeplot_save = {}
        elif _is_running_on_ci():
            teeplot_save = {".pdf"}
        else:
            teeplot_save = {".pdf", ".png"}
    elif teeplot_save is False:
        teeplot_save = {}
    elif teeplot_save is True:
        if _is_running_on_ci():
            teeplot_save = {".pdf"}
        else:
            teeplot_save = {".pdf", ".png"}

    if "TEEPLOT_PNG" in os.environ:
        teeplot_save += ".png"

    if "TEEPLOT_PDF" in os.environ:
        teeplot_save += ".pdf"

    # enable TrueType fonts
    # see https://gecco-2021.sigevo.org/Paper-Submission-Instructions
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    res = plotter(
        *args,
        **{
            k : v
            for k, v in kwargs.items()
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
        **teeplot_outattrs,
    }
    out_filenamer = lambda ext: kn.pack({
        k : v
        for k, v in attr_maker(ext).items()
        if not k.startswith('_')
    })

    out_folder = f'{teeplot_outdir}/{teeplot_subdir}'
    pathlib.Path(
        out_folder,
    ).mkdir(
        parents=True,
        exist_ok=True,
    )

    for ext, dpi in ('.pdf', 'figure'), ('.png', 300):

        out_path = kn.chop(
            f'{out_folder}/{out_filenamer(ext)}',
            mkdir=True,
        )

        if ext not in teeplot_save:
            print(f"skipping {out_path}")
            continue

        print(out_path)
        plt.savefig(
            out_path,
            bbox_inches='tight',
            transparent=teeplot_transparent,
            dpi=dpi,
        )

    return res
