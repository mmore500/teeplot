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

draftmode: bool = False

oncollision: typing.Literal["error", "fix", "ignore", "warn"] = os.environ.get("TEEPLOT_ONCOLLISION", "warn").lower()
if not oncollision in ("error", "fix", "ignore", "warn"):
    raise RuntimeError(
        f"invalid env var value TEEPLOT_ONCOLLISION={oncollision}",
    )

save = {
    ".eps": None,
    ".pdf": True,
    ".png": True if not _is_running_on_ci() else None,
    ".ps": None,
    ".svg": None,
}
"""Global format output defaults.

True enables format globally and False disables.
None defers to teeplot_save kwarg."""

_history = Counter()


# enable TrueType fonts
# see https://gecco-2021.sigevo.org/Paper-Submission-Instructions
@matplotlib.rc_context(
    {
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
    },
)
def tee(
    plotter: typing.Callable[..., typing.Any],
    *args: typing.Any,
    teeplot_dpi: int = 300,
    teeplot_oncollision: typing.Optional[
        typing.Literal["error", "fix", "ignore", "warn"]] = None,
    teeplot_outattrs: typing.Dict[str, str] = {},
    teeplot_outdir: str = "teeplots",
    teeplot_outinclude: typing.Iterable[str] = tuple(),
    teeplot_outexclude: typing.Iterable[str] = tuple(),
    teeplot_postprocess: typing.Union[str, typing.Callable] = "",
    teeplot_save: typing.Union[typing.Iterable[str], bool] = True,
    teeplot_subdir: str = '',
    teeplot_transparent: bool = True,
    teeplot_verbose: bool = True,
    **kwargs: typing.Any
) -> typing.Any:
    """Executes a plotting function and saves the resulting plot to specified
    formats using a descriptive filename automatically generated from plotting
    function arguments.

    Parameters
    ----------
    plotter : Callable[..., Any]
        The plotting function to execute.
    *args : Any
        Positional arguments forwarded to the plotting function.
    teeplot_dpi : int, default 300
        Resolution for rasterized components of the saved plot in dots per inch.

        Default is publication-quality 300 dpi.
    teeplot_oncollision : Literal["error", "fix", "ignore", "warn"], optional
        Strategy for handling collisions between generated filenames.
    teeplot_outattrs : Dict[str, str], optional
        Additional attributes to include in the output filename.
    teeplot_outdir : str, default "teeplots"
        Base directory for saving plots.
    teeplot_outexcl : Iterable[str], default tuple()
        Attributes to always exclude, if present, from the output filename.

        Under default settings, all kwargs with string values are included in
        the output filename.
    teeplot_outincl : Iterable[str], default tuple()
        Attributes to always include, if present, in the output filename.

        Under default settings, all kwargs with string values are included in
        the output filename.
    teeplot_postprocess : Union[str, Callable], default ""
        Actions to perform on plot result before saving.

        A `str` kwarg will be `exec`'ed, with `plt` and `sns` (if installed)
        available, as well as the plotter return value as `teed`. If `str` value
        ends with ';', the postprocess step will not be included in output filename.

        A Callable kwarg will have invocation attempted first with the plotter
        return value as the `teed` kwarg, second with the plotter return value
        as  the `ax` kwarg, third with no args, and last with the plotter
        return value as a positional arg.
    teeplot_save : Union[str, Iterable[str], bool], default True
        File formats to save the plots in.

        If `True`, defaults to global settings. If `False`, suppresses output
        to all file formats.
    teeplot_subdir : str, default ""
        Subdirectory within `teeplot_outdir` to save plots.
    teeplot_transparent : bool, default True
        Save the plot with a transparent background.
    teeplot_verbose : bool, default True
        Print saved filenames if True.
    **kwargs : Any
        Additional keyword arguments forwarded to the plotting function.

    Returns
    -------
    Any
        The result from the `plotter` function.

    Raises
    ------
    RuntimeError
        If a file collision occurs and `teeplot_oncollision` is "error".
    ValueError
        For invalid format or `teeplot_oncollision` settings.

    Notes
    -----
    - The output filename is generated based on the `plotter` function name and
      provided attributes.
    - Directories are created as needed based on specified output paths.
    - Enforces TrueType fonts for PDF and PS formats.
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
        or strtobool(os.environ.get("TEEPLOT_DRAFTMODE", "F"))
        or draftmode
    ):
        # remove all outputs
        teeplot_save = set()
    elif isinstance(teeplot_save, str):
        if not teeplot_save in formats:
            raise ValueError(
                f"only {[*formats]} save formats are supported, "
                f"not {teeplot_save}",
            )
        # remove explicitly disabled outputs
        blacklist = set(k for k, v in formats.items() if v is False)
        exclusions =  {teeplot_save} | blacklist
        if teeplot_verbose and exclusions:
            print(f"skipping {exclusions}")
        teeplot_save = {teeplot_save} - exclusions

    elif isinstance(teeplot_save, abc.Iterable):
        if not {*teeplot_save} <= {*formats}:
            raise ValueError(
                f"only {[*formats]} save formats are supported, "
                f"not {list({*teeplot_save} - {*formats})}",
            )
        # remove explicitly disabled outputs
        blacklist = set(k for k, v in formats.items() if v is False)
        exclusions =  set(teeplot_save) | blacklist
        if teeplot_verbose and exclusions:
            print(f"skipping {exclusions}")
        teeplot_save = set(teeplot_save) - exclusions
    else:
        raise TypeError(
            "teeplot_save kwarg must be None, bool, or iterable, "
            f"not {type(teeplot_save)} {teeplot_save}",
        )

    if teeplot_oncollision is None:
        teeplot_oncollision = oncollision

    # ----- end argument parsing
    # ----- begin plotting

    teed = plotter(*args, **{k: v for k, v in kwargs.items()})

    if isinstance(teeplot_postprocess, abc.Callable):
        while "make breakable":
            try:
                teeplot_postprocess(teed=teed)  # first attempt
                break
            except TypeError:
                pass
            try:
                teeplot_postprocess(ax=teed)  # second attempt
                break
            except TypeError:
                pass
            try:
                teeplot_postprocess()  # third attempt
                break
            except TypeError:
                pass
            try:
                teeplot_postprocess(teed)  # fourth attempt
                break
            except TypeError:
                pass
            raise TypeError(  # give up
                f"teeplot_postprocess={teeplot_postprocess} threw TypeError "
                "or call signature incompatible with attempted invocations",
            )
    elif teeplot_postprocess:
        if not isinstance(teeplot_postprocess, str):
            raise TypeError(
                "teeplot_postprocess must be str or Callable, "
                f"not {type(teeplot_postprocess)} {teeplot_postprocess}"
            )
        try:
            import seaborn as sns
            import seaborn
        except ModuleNotFoundError:
            pass
        exec(teeplot_postprocess)

    incl = [*teeplot_outinclude]
    attr_maker = lambda ext: {
        **{
            slugify(k) : slugify(str(v))
            for k, v in kwargs.items()
            if isinstance(v, str) or k in incl
        },
        **{
            'viz' : slugify(plotter.__name__),
            'ext' : ext,
        },
        **(
            {"post": teeplot_postprocess.__name__}
            if teeplot_postprocess and isinstance(teeplot_postprocess, abc.Callable)
            else {"post": slugify(teeplot_postprocess)}
            if teeplot_postprocess and not teeplot_postprocess.endswith(";")
            else {}
        ),
        **teeplot_outattrs,
    }
    excl = [*teeplot_outexclude]
    out_filenamer = lambda ext: kn.pack({
        k : v
        for k, v in attr_maker(ext).items()
        if not k.startswith('_') and not k in excl
    })

    out_folder = pathlib.Path(teeplot_outdir, teeplot_subdir)
    out_folder.mkdir(parents=True, exist_ok=True)

    for ext in save:

        if ext not in teeplot_save:
            if teeplot_verbose > 1:
                print(f"skipping {out_path}")
            continue

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

        if teeplot_verbose:
            print(out_path)
        plt.savefig(
            str(out_path),
            bbox_inches='tight',
            transparent=teeplot_transparent,
            dpi=teeplot_dpi,
        )

    return teed
