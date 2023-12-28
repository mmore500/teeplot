from collections import abc, Counter
import copy
import os
import pathlib
import typing
import warnings

from keyname import keyname as kn
import matplotlib
import matplotlib.pyplot as plt
from slugify import slugify
from strtobool import strtobool


def _is_running_on_ci() -> bool:
    ci_envs = ['CI', 'TRAVIS', 'GITHUB_ACTIONS', 'GITLAB_CI', 'JENKINS_URL']
    return any(env in os.environ for env in ci_envs)

draft_mode: bool = False

oncollision: typing.Literal["error", "fix", "ignore", "warn"] = os.environ.get("TEEPLOT_ONCOLLISION", "warn").lower()
if not oncollision in ("error", "fix", "ignore", "warn"):
    raise RuntimeError(
        f"invalid env var value TEEPLOT_ONCOLLISION={oncollision}",
    )

save = {
    ".pdf": True,
    ".png": True if not _is_running_on_ci() else None,
}
"""Global format output defaults.

True enables format globally and False disables.
None defers to teeplot_save kwarg."""

_history = Counter()

def tee(
    plotter: typing.Callable[..., typing.Any],
    *args: typing.Any,
    teeplot_oncollision: typing.Optional[
        typing.Literal["error", "fix", "ignore", "warn"]] = None,
    teeplot_outattrs: typing.Dict[str, str] = {},
    teeplot_outdir: str = "teeplots",
    teeplot_save: typing.Optional[typing.Iterable[str]] = None,
    teeplot_subdir: str = '',
    teeplot_transparent: bool = True,
    teeplot_verbose: bool = True,
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
        to `.pdf`. Only supported formats are `.pdf` and `.png`.
    teeplot_subdir : str, default ""
        The subdirectory within `teeplot_outdir` to save plots.
    teeplot_transparent : bool, default True
        Whether to save the plot with a transparent background.
    teeplot_verbose : bool, default True
        Should filenames of saved visualizations be printed?
    **kwargs : Any
        Keyword arguments are forwarded to the plotting function.

    Returns
    -------
    Any
        The result from the `plotter` function.

    Notes
    -----
    - The output filename is generated based on the `plotter` function name and
      the provided attributes.
    - The function will create directories as needed based on the specified
      output paths.
    """
    formats = copy.copy(save)

    # incorporate environment variable settings
    for format in [*formats]:
        format_env_var = f"TEEPLOT_{format[1:].upper()}"
        if format_env_var in os.environ:  # strip leading .
            format_env_value = os.environ[format_env_var]
            if format_env_value.lower() in ("none", "defer"):
                formats[format] = None
            else:
                formats[format] = strtobool(format_env_value)

    if teeplot_save is None or teeplot_save is True:
        # default formats
        teeplot_save = set(filter(formats.__getitem__, formats))
    elif (
        teeplot_save is False
        or "TEEPLOT_DRAFT_MODE" in os.environ
        or draft_mode
    ):
        # remove all outputs
        teeplot_save = set()
    elif isinstance(teeplot_save, abc.Iterable):
        if not {*teeplot_save} <= {*formats}:
            raise ValueError(
                f"only {[*formats]} save formats are supported, "
                f"not {list({*teeplot_save} - {*formats})}",
            )
        # remove explicitly disabled outputs
        teeplot_save = (
            set(teeplot_save) - set(k for k, v in formats.items() if v is False)
        )
    else:
        raise TypeError(
            "teeplot_save kwarg must be None, bool, or iterable, "
            f"not {type(teeplot_save)} {teeplot_save}",
        )

    if teeplot_oncollision is None:
        teeplot_oncollision = oncollision

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

        if out_path in _history:
            if teeplot_oncollision == "error":
                raise RuntimeError(f"teeplot already created file {out_path}")
            elif teeplot_oncollision == "fix":
                count = _history[out_path]
                suffix = f"ext={ext}"
                assert str(out_path).endswith(suffix)
                out_path = str(out_path)[:-len(suffix)] + f"#={count}+" + suffix
            elif teeplot_oncollision == "ignore":
                pass
            elif teeplot_oncollision == "warn":
                warnings.warn(
                    f"teeplot already created file {out_path}, overwriting it",
                )
            else:
                raise ValueError(
                    "teeplot_oncollision must be one of 'error', 'fix', "
                    f"'ignore', or 'warn', not {teeplot_oncollision}",
                )
        _history[out_path] += 1

        if ext not in teeplot_save:
            if teeplot_verbose:
                print(f"skipping {out_path}")
            continue

        if teeplot_verbose:
            print(out_path)
        plt.savefig(
            str(out_path),
            bbox_inches='tight',
            transparent=teeplot_transparent,
            dpi=dpi,
        )

    return res
