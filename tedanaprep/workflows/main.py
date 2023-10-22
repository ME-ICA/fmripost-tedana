"""Base workflows for the tedana BIDS App."""
from niworkflows.engine.workflows import LiterateWorkflow as Workflow


def init_tedana_wf():
    """Identify subjects in dataset."""
    ...


def init_single_subject_wf():
    """Identify runs for a given subject."""
    ...


def init_denoise_run_wf():
    """Run tedana on a single run.

    Steps
    -----
    1.  A BIDS data grabber to collect the first echo from each run.
    2.  A BIDS data grabber to grab the other echoes, brain mask, echo times,
        and potentially confounds.
    3.  Drop dummy volumes as requested.
    4.  Run tedana.
    5.  Reorganize tedana outputs into BIDS format.
    6.  Generate nireports HTML report.
    """
    from tedanaprep.interfaces.bids import BIDSDataGrabber
    from tedanaprep.interfaces.misc import RemoveNonSteadyStateVolumes
    from tedanaprep.interfaces.nilearn import LoadConfounds
    from tedanaprep.interfaces.tedana import Tedana
    ...
