# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
#
# Copyright 2023 The NiPreps Developers <nipreps@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# We support and encourage derived works from this project, please read
# about our expectations at
#
#     https://www.nipreps.org/community/licensing/
#
"""Parser."""
import sys

from fmripost_tedana import config


def _build_parser(**kwargs):
    """Build parser object.

    ``kwargs`` are passed to ``argparse.ArgumentParser`` (mainly useful for debugging).
    """
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
    from functools import partial
    from pathlib import Path

    from packaging.version import Version

    from fmripost_tedana.cli.version import check_latest, is_flagged

    def _path_exists(path, parser):
        """Ensure a given path exists."""
        if path is None or not Path(path).exists():
            raise parser.error(f"Path does not exist: <{path}>.")
        return Path(path).absolute()

    def _is_file(path, parser):
        """Ensure a given path exists and it is a file."""
        path = _path_exists(path, parser)
        if not path.is_file():
            raise parser.error(f"Path should point to a file (or symlink of file): <{path}>.")
        return path

    def _min_one(value, parser):
        """Ensure an argument is not lower than 1."""
        value = int(value)
        if value < 1:
            raise parser.error("Argument can't be less than one.")
        return value

    def _to_gb(value):
        scale = {"G": 1, "T": 10**3, "M": 1e-3, "K": 1e-6, "B": 1e-9}
        digits = "".join([c for c in value if c.isdigit()])
        units = value[len(digits) :] or "M"
        return int(digits) * scale[units[0]]

    def _drop_sub(value):
        return value[4:] if value.startswith("sub-") else value

    def _filter_pybids_none_any(dct):
        import bids

        return {
            k: bids.layout.Query.NONE if v is None else (bids.layout.Query.ANY if v == "*" else v)
            for k, v in dct.items()
        }

    def _bids_filter(value, parser):
        from json import JSONDecodeError, loads

        if value:
            if Path(value).exists():
                try:
                    return loads(Path(value).read_text(), object_hook=_filter_pybids_none_any)
                except JSONDecodeError:
                    raise parser.error(f"JSON syntax error in: <{value}>.")
            else:
                raise parser.error(f"Path does not exist: <{value}>.")

    verstr = f"fMRIPost-tedana v{config.environment.version}"
    currentv = Version(config.environment.version)
    is_release = not any((currentv.is_devrelease, currentv.is_prerelease, currentv.is_postrelease))

    parser = ArgumentParser(
        description=(
            f"fMRIPost-tedana: fMRI POSTprocessing tedana workflow v{config.environment.version}"
        ),
        formatter_class=ArgumentDefaultsHelpFormatter,
        **kwargs,
    )
    PathExists = partial(_path_exists, parser=parser)
    IsFile = partial(_is_file, parser=parser)
    PositiveInt = partial(_min_one, parser=parser)
    BIDSFilter = partial(_bids_filter, parser=parser)

    # Arguments as specified by BIDS-Apps
    # required, positional arguments
    # IMPORTANT: they must go directly with the parser object
    parser.add_argument(
        "bids_dir",
        action="store",
        type=PathExists,
        help=(
            "The root folder of a BIDS valid dataset (sub-XXXXX folders should "
            "be found at the top level in this folder)."
        ),
    )
    parser.add_argument(
        "output_dir",
        action="store",
        type=Path,
        help="The output path for the outcomes of preprocessing and visual reports",
    )
    parser.add_argument(
        "analysis_level",
        choices=["participant"],
        help=(
            "Processing stage to be run, only 'participant' in the case of "
            "fMRIPrep (see BIDS-Apps specification)."
        ),
    )

    g_bids = parser.add_argument_group("Options for filtering BIDS queries")
    g_bids.add_argument(
        "--skip_bids_validation",
        "--skip-bids-validation",
        action="store_true",
        default=False,
        help="Assume the input dataset is BIDS compliant and skip the validation",
    )
    g_bids.add_argument(
        "--participant-label",
        "--participant_label",
        action="store",
        nargs="+",
        type=_drop_sub,
        help="A space delimited list of participant identifiers or a single "
        "identifier (the sub- prefix can be removed)",
    )
    g_bids.add_argument(
        "-t",
        "--task-id",
        action="store",
        help="Select a specific task to be processed",
    )
    g_bids.add_argument(
        "--bids-filter-file",
        dest="bids_filters",
        action="store",
        type=BIDSFilter,
        metavar="FILE",
        help=(
            "A JSON file describing custom BIDS input filters using PyBIDS. "
            "For further details, please check out "
            "https://fmriprep.readthedocs.io/en/"
            f"{currentv.base_version if is_release else 'latest'}/faq.html#"
            "how-do-I-select-only-certain-files-to-be-input-to-fMRIPrep"
        ),
    )
    g_bids.add_argument(
        "-d",
        "--derivatives",
        action="store",
        metavar="PATH",
        type=Path,
        nargs="*",
        help="Search PATH(s) for pre-computed derivatives.",
    )
    g_bids.add_argument(
        "--bids-database-dir",
        metavar="PATH",
        type=Path,
        help=(
            "Path to a PyBIDS database folder, for faster indexing "
            "(especially useful for large datasets). "
            "Will be created if not present."
        ),
    )

    g_perfm = parser.add_argument_group("Options to handle performance")
    g_perfm.add_argument(
        "--nprocs",
        "--nthreads",
        "--n_cpus",
        "--n-cpus",
        dest="nprocs",
        action="store",
        type=PositiveInt,
        help="Maximum number of threads across all processes",
    )
    g_perfm.add_argument(
        "--omp-nthreads",
        action="store",
        type=PositiveInt,
        help="Maximum number of threads per-process",
    )
    g_perfm.add_argument(
        "--mem",
        "--mem_mb",
        "--mem-mb",
        dest="memory_gb",
        action="store",
        type=_to_gb,
        metavar="MEMORY_MB",
        help="Upper bound memory limit for fMRIPrep processes",
    )
    g_perfm.add_argument(
        "--low-mem",
        action="store_true",
        help="Attempt to reduce memory usage (will increase disk usage in working directory)",
    )
    g_perfm.add_argument(
        "--use-plugin",
        "--nipype-plugin-file",
        action="store",
        metavar="FILE",
        type=IsFile,
        help="Nipype plugin configuration file",
    )
    g_perfm.add_argument(
        "--sloppy",
        action="store_true",
        default=False,
        help="Use low-quality tools for speed - TESTING ONLY",
    )

    g_subset = parser.add_argument_group("Options for performing only a subset of the workflow")
    g_subset.add_argument(
        "--boilerplate-only",
        "--boilerplate_only",
        action="store_true",
        default=False,
        help="Generate boilerplate only",
    )
    g_subset.add_argument(
        "--reports-only",
        action="store_true",
        default=False,
        help=(
            "Only generate reports, don't run workflows. "
            "This will only rerun report aggregation, not reportlet generation for specific "
            "nodes."
        ),
    )

    g_conf = parser.add_argument_group("Workflow configuration")
    g_conf.add_argument(
        "--ignore",
        required=False,
        action="store",
        nargs="+",
        default=[],
        choices=["fieldmaps", "slicetiming", "sbref", "t2w", "flair"],
        help=(
            "Ignore selected aspects of the input dataset to disable corresponding "
            "parts of the workflow (a space delimited list)"
        ),
    )
    g_conf.add_argument(
        "--dummy-scans",
        required=False,
        action="store",
        default=None,
        type=int,
        help="Number of nonsteady-state volumes. Overrides automatic detection.",
    )
    g_conf.add_argument(
        "--random-seed",
        dest="_random_seed",
        action="store",
        type=int,
        default=None,
        help="Initialize the random seed for the workflow",
    )

    g_outputs = parser.add_argument_group("Options for modulating outputs")
    g_outputs.add_argument(
        "--md-only-boilerplate",
        action="store_true",
        default=False,
        help="Skip generation of HTML and LaTeX formatted citation with pandoc",
    )

    g_tedana = parser.add_argument_group("Options for running tedana")
    g_tedana.add_argument(
        "--fittype",
        dest="fittype",
        action="store",
        choices=["loglin", "curvefit"],
        help=(
            "Desired T2*/S0 fitting method. "
            '"loglin" means that a linear model is fit '
            "to the log of the data. "
            '"curvefit" means that a more computationally '
            "demanding monoexponential model is fit "
            "to the raw data. "
        ),
        default="loglin",
    )
    g_tedana.add_argument(
        "--combmode",
        dest="combmode",
        action="store",
        choices=["t2s"],
        help="Combination scheme for TEs: t2s (Posse 1999)",
        default="t2s",
    )
    g_tedana.add_argument(
        "--tedpca",
        dest="tedpca",
        type=check_tedpca_value,
        help=(
            "Method with which to select components in TEDPCA. "
            "PCA decomposition with the mdl, kic and aic options "
            "is based on a Moving Average (stationary Gaussian) "
            "process and are ordered from most to least aggressive. "
            "'kundu' or 'kundu-stabilize' are selection methods that "
            "were distributed with MEICA. "
            "Users may also provide a float from 0 to 1, "
            "in which case components will be selected based on the "
            "cumulative variance explained or an integer greater than 1"
            "in which case the specificed number of components will be "
            "selected."
        ),
        default="aic",
    )
    g_tedana.add_argument(
        "--tree",
        dest="tree",
        help=(
            "Decision tree to use. You may use a "
            "packaged tree (kundu, minimal) or supply a JSON "
            "file which matches the decision tree file "
            "specification. Minimal still being tested with more"
            "details in docs"
        ),
        default="kundu",
    )
    g_tedana.add_argument(
        "--maxit",
        dest="maxit",
        metavar="INT",
        type=int,
        help="Maximum number of iterations for ICA.",
        default=500,
    )
    g_tedana.add_argument(
        "--maxrestart",
        dest="maxrestart",
        metavar="INT",
        type=int,
        help=(
            "Maximum number of attempts for ICA. If ICA "
            "fails to converge, the fixed seed will be "
            "updated and ICA will be run again. If "
            "convergence is achieved before maxrestart "
            "attempts, ICA will finish early."
        ),
        default=10,
    )
    g_tedana.add_argument(
        "--tedort",
        dest="tedort",
        action="store_true",
        help="Orthogonalize rejected components w.r.t. accepted components prior to denoising.",
        default=False,
    )
    g_tedana.add_argument(
        "--gscontrol",
        dest="gscontrol",
        required=False,
        action="store",
        nargs="+",
        help=(
            "Perform additional denoising to remove "
            "spatially diffuse noise. "
            "This argument can be single value or a space "
            "delimited list"
        ),
        choices=["mir", "gsr"],
        default="",
    )
    g_tedana.add_argument(
        "--png-cmap",
        dest="png_cmap",
        type=str,
        help="Colormap for figures",
        default="coolwarm",
    )

    g_carbon = parser.add_argument_group("Options for carbon usage tracking")
    g_carbon.add_argument(
        "--track-carbon",
        action="store_true",
        help="Tracks power draws using CodeCarbon package",
    )
    g_carbon.add_argument(
        "--country-code",
        action="store",
        default="CAN",
        type=str,
        help="Country ISO code used by carbon trackers",
    )

    g_other = parser.add_argument_group("Other options")
    g_other.add_argument("--version", action="version", version=verstr)
    g_other.add_argument(
        "-v",
        "--verbose",
        dest="verbose_count",
        action="count",
        default=0,
        help="Increases log verbosity for each occurrence, debug level is -vvv",
    )
    g_other.add_argument(
        "-w",
        "--work-dir",
        action="store",
        type=Path,
        default=Path("work").absolute(),
        help="Path where intermediate results should be stored",
    )
    g_other.add_argument(
        "--clean-workdir",
        action="store_true",
        default=False,
        help="Clears working directory of contents. Use of this flag is not "
        "recommended when running concurrent processes of fMRIPrep.",
    )
    g_other.add_argument(
        "--resource-monitor",
        action="store_true",
        default=False,
        help="Enable Nipype's resource monitoring to keep track of memory and CPU usage",
    )
    g_other.add_argument(
        "--config-file",
        action="store",
        metavar="FILE",
        help="Use pre-generated configuration file. Values in file will be overridden "
        "by command-line arguments.",
    )
    g_other.add_argument(
        "--write-graph",
        action="store_true",
        default=False,
        help="Write workflow graph.",
    )
    g_other.add_argument(
        "--stop-on-first-crash",
        action="store_true",
        default=False,
        help="Force stopping on first crash, even if a work directory was specified.",
    )
    g_other.add_argument(
        "--notrack",
        action="store_true",
        default=False,
        help="Opt-out of sending tracking information of this run to "
        "the FMRIPREP developers. This information helps to "
        "improve FMRIPREP and provides an indicator of real "
        "world usage crucial for obtaining funding.",
    )
    g_other.add_argument(
        "--debug",
        action="store",
        nargs="+",
        choices=config.DEBUG_MODES + ("all",),
        help="Debug mode(s) to enable. 'all' is alias for all available modes.",
    )

    latest = check_latest()
    if latest is not None and currentv < latest:
        print(
            """\
You are using fMRIPrep-%s, and a newer version of fMRIPrep is available: %s.
Please check out our documentation about how and when to upgrade:
https://fmriprep.readthedocs.io/en/latest/faq.html#upgrading"""
            % (currentv, latest),
            file=sys.stderr,
        )

    _blist = is_flagged()
    if _blist[0]:
        _reason = _blist[1] or "unknown"
        print(
            """\
WARNING: Version %s of fMRIPrep (current) has been FLAGGED
(reason: %s).
That means some severe flaw was found in it and we strongly
discourage its usage."""
            % (config.environment.version, _reason),
            file=sys.stderr,
        )

    return parser


def parse_args(args=None, namespace=None):
    """Parse args and run further checks on the command line."""
    import logging

    parser = _build_parser()
    opts = parser.parse_args(args, namespace)

    if opts.config_file:
        skip = {} if opts.reports_only else {"execution": ("run_uuid",)}
        config.load(opts.config_file, skip=skip, init=False)
        config.loggers.cli.info(f"Loaded previous configuration file {opts.config_file}")

    config.execution.log_level = int(max(25 - 5 * opts.verbose_count, logging.DEBUG))
    config.from_dict(vars(opts), init=["nipype"])

    if not config.execution.notrack:
        import pkgutil

        if pkgutil.find_loader("sentry_sdk") is None:
            config.execution.notrack = True
            config.loggers.cli.warning("Telemetry disabled because sentry_sdk is not installed.")
        else:
            config.loggers.cli.info(
                "Telemetry system to collect crashes and errors is enabled "
                "- thanks for your feedback!. Use option ``--notrack`` to opt out."
            )

    # Retrieve logging level
    build_log = config.loggers.cli

    # Load base plugin_settings from file if --use-plugin
    if opts.use_plugin is not None:
        import yaml

        with open(opts.use_plugin) as f:
            plugin_settings = yaml.load(f, Loader=yaml.FullLoader)
        _plugin = plugin_settings.get("plugin")
        if _plugin:
            config.nipype.plugin = _plugin
            config.nipype.plugin_args = plugin_settings.get("plugin_args", {})
            config.nipype.nprocs = opts.nprocs or config.nipype.plugin_args.get(
                "n_procs", config.nipype.nprocs
            )

    # Resource management options
    # Note that we're making strong assumptions about valid plugin args
    # This may need to be revisited if people try to use batch plugins
    if 1 < config.nipype.nprocs < config.nipype.omp_nthreads:
        build_log.warning(
            f"Per-process threads (--omp-nthreads={config.nipype.omp_nthreads}) exceed "
            f"total threads (--nthreads/--n_cpus={config.nipype.nprocs})"
        )

    bids_dir = config.execution.bids_dir
    output_dir = config.execution.output_dir
    work_dir = config.execution.work_dir
    version = config.environment.version

    # Wipe out existing work_dir
    if opts.clean_workdir and work_dir.exists():
        from niworkflows.utils.misc import clean_directory

        build_log.info(f"Clearing previous fMRIPrep working directory: {work_dir}")
        if not clean_directory(work_dir):
            build_log.warning(f"Could not clear all contents of working directory: {work_dir}")

    # Update the config with an empty dict to trigger initialization of all config
    # sections (we used `init=False` above).
    # This must be done after cleaning the work directory, or we could delete an
    # open SQLite database
    config.from_dict({})

    # Ensure input and output folders are not the same
    if output_dir == bids_dir:
        parser.error(
            "The selected output folder is the same as the input BIDS folder. "
            "Please modify the output path "
            f"(suggestion: {bids_dir / 'derivatives' / 'fmriprep-' + version.split('+')[0]}."
        )

    if bids_dir in work_dir.parents:
        parser.error(
            "The selected working directory is a subdirectory of the input BIDS folder. "
            "Please modify the output path."
        )

    # Validate inputs
    if not opts.skip_bids_validation:
        from fmripost_tedana.utils.bids import validate_input_dir

        build_log.info(
            "Making sure the input data is BIDS compliant "
            "(warnings can be ignored in most cases)."
        )
        validate_input_dir(config.environment.exec_env, opts.bids_dir, opts.participant_label)

    # Setup directories
    config.execution.log_dir = config.execution.fmriprep_dir / "logs"
    # Check and create output and working directories
    config.execution.log_dir.mkdir(exist_ok=True, parents=True)
    work_dir.mkdir(exist_ok=True, parents=True)

    # Force initialization of the BIDSLayout
    config.execution.init()
    all_subjects = config.execution.layout.get_subjects()
    if config.execution.participant_label is None:
        config.execution.participant_label = all_subjects

    participant_label = set(config.execution.participant_label)
    missing_subjects = participant_label - set(all_subjects)
    if missing_subjects:
        parser.error(
            "One or more participant labels were not found in the BIDS directory: "
            f"{', '.join(missing_subjects)}."
        )

    config.execution.participant_label = sorted(participant_label)
