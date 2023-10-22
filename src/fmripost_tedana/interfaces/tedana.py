"""Pydra interfaces for tedana workflows."""
import numpy as np
from pydra import mark
from typing import List
from tedana.workflows import t2smap_workflow, tedana_workflow

tedana_workflow_mark = mark.annotate(
    {
        "data": list,
        "tes": np.array,
        "out_dir": str,
        "mask": List(None, str),
        "convention": str,
        "prefix": str,
        "fittype": str,
        "combmode": str,
        "tree": str,
        "tedpca": str,
        "fixed_seed": int,
        "maxit": int,
        "maxrestart": int,
        "tedort": bool,
        "gscontrol": List(None, list),
        "no_reports": bool,
        "png_cmap": str,
        "verbose": bool,
        "low_mem": bool,
        "debug": bool,
        "quiet": bool,
        "overwrite": bool,
        "t2smap": List(None, str),
        "mixm": List(None, str),
        "tedana_command": List(None, str),
    },
)(tedana_workflow)

t2smap_workflow_mark = mark.annotate(
    {
        "data": list,
        "tes": np.array,
        "out_dir": str,
        "mask": List(None, str),
        "convention": str,
        "prefix": str,
        "fittype": str,
        "fitmode": str,
        "combmode": str,
        "debug": bool,
        "quiet": bool,
    }
)
