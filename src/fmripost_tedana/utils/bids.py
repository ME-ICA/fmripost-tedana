"""BIDS-related functions for fmripost_tedana."""
import yaml
from bids.layout import Query

from fmripost_tedana import config


def collect_data():
    """Collect first echo's preprocessed file for all requested runs."""
    layout = config.layout
    bids_filters = config.bids_filters or {}
    participant_label = config.participant_label

    query = {
        "echo": 1,
        "space": ["boldref", Query.NONE],
        "suffix": "bold",
        "extension": [".nii", ".nii.gz"],
    }

    # Apply filters. These may override anything.
    if "echo_files" in bids_filters.keys():
        for acq, entities in bids_filters["echo_files"].items():
            query[acq].update(entities)

    echo1_files = layout.get(return_type="file", subject=participant_label, **query)

    return echo1_files


def collect_run_data(echo1_file):
    """Use pybids to retrieve the input data for a given participant."""
    layout = config.layout
    bids_filters = config.bids_filters or {}

    queries = {
        "echo_files": {
            "echo": Query.ANY,
        },
        "mask": {
            "echo": Query.NONE,
            "desc": "brain",
            "suffix": "mask",
        },
        "confounds": {
            "echo": Query.NONE,
            "desc": "confounds",
            "suffix": "timeseries",
            "extension": ".tsv",
        },
    }

    bids_file = layout.get_file(echo1_file)
    # Apply filters. These may override anything.
    for acq, entities in bids_filters.items():
        if acq in queries.keys():
            queries[acq].update(entities)

    run_data = {
        dtype: layout.get_nearest(
            bids_file.path,
            return_type="file",
            strict=True,
            **query,
        )
        for dtype, query in queries.items()
    }
    # Add metadata to dictionary now.
    run_data["EchoTimes"] = [layout.get_EchoTime(f) for f in run_data["echo_files"]]

    config.loggers.workflow.info(
        (
            f"Collected run data for {echo1_file}:\n"
            f"{yaml.dump(run_data, default_flow_style=False, indent=4)}"
        ),
    )

    return run_data
