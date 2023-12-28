import os
import pathlib
import typing

from keyname import keyname as kn
import matplotlib
import matplotlib.pyplot as plt
from slugify import slugify


def _is_running_on_ci() -> bool:
    ci_envs = ['CI', 'TRAVIS', 'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL']
    return any(env in os.environ for env in ci_envs)


def tee(
    plotter: typing.Callable[..., typing.Any],
    *args: typing.Any,
    teeplot_outattrs: typing.Dict[str, str] = {},
    teeplot_outdir: str = "teeplots",
    teeplot_save: typing.Optional[typing.Iterable[str]] = None,
    teeplot_subdir: str = '.',
    teeplot_transparent: bool = True,
    **kwargs: typing.Any
) -> typing.Any:
    """Executes a plotting function and saves the resulting plot to specified
    formats using a descriptive filename automatically generated from plotting
    kwargs.

    Parameters
    ----------
    plotter : Callable[..., Any]
        The plotting function to execute.
    *args : Any
        Positional arguments are forwarded to the plotting function.
    teeplot_outattrs : Dict[str, str], optional
        Additional key-value information to include in the output filename.
    teeplot_outdir : str, default "teeplots"
        The base directory where plots will be saved.
    teeplot_save : Iterable[str], optional
        A set of strings indicating which file formats to save the plots.

        Defaults to `.pdf` and `.png` unless running on CI, where it defaults
        to `.pdf`.
    teeplot_subdir : str, ./
        The subdirectory within `teeplot_outdir` to save plots.
    teeplot_transparent : bool, default True
        Whether to save the plot with a transparent background.
    **kwargs : Any
        Keyword arguments are forwarded to the plotting function.

    Returns
    -------
    Any
        The result from the `plotter` function.

    Notes
    -----
    - The output filename is generated based on the `plotter` function name and the provided attributes.
    - The function will create directories as needed based on the specified output paths.
    """
    if teeplot_save is None:
        if "TEEPLOT_DRAFT_MODE" in os.environ:
            teeplot_save = set()
        elif _is_running_on_ci():
            teeplot_save = {".pdf"}
        else:
            teeplot_save = {".pdf", ".png"}
    elif teeplot_save is False:
        teeplot_save = set()
    elif teeplot_save is True:
        if _is_running_on_ci():
            teeplot_save = {".pdf"}
        else:
            teeplot_save = {".pdf", ".png"}
    else:
        teeplot_save = {*teeplot_save}

    if "TEEPLOT_PNG" in os.environ:
        teeplot_save.add(".png")

    if "TEEPLOT_PDF" in os.environ:
        teeplot_save.add(".pdf")

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

    out_folder = pathlib.Path(teeplot_outdir, teeplot_subdir)
    out_folder.mkdir(parents=True, exist_ok=True)

    for ext, dpi in ('.pdf', 'figure'), ('.png', 300):

        out_path = pathlib.Path(
            kn.chop(
                str(out_folder / out_filenamer(ext)),
                mkdir=True,
            ),
        )

        if ext not in teeplot_save:
            print(f"skipping {out_path}")
            continue

        print(out_path)
        plt.savefig(
            str(out_path),
            bbox_inches='tight',
            transparent=teeplot_transparent,
            dpi=dpi,
        )

    return res
