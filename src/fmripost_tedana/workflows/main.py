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
    from fmripost_tedana.interfaces.bids import collect_run_data
    from fmripost_tedana.interfaces.misc import RemoveNonSteadyStateVolumes
    from fmripost_tedana.interfaces.nilearn import LoadConfounds
    from fmripost_tedana.interfaces.tedana import t2smap_workflow_mark, tedana_workflow_mark

    # creating workflow with two input fields
    wf = Workflow(
        name="denoise_run_wf",
        input_spec=["first_echo"],
    )
    # adding a task and connecting task's input to the workflow input
    wf.add(collect_run_data(name="collect_run_data"))
    # adding another task and connecting
    # task's input to the "mult" task's output
    wf.add(tedana_workflow_mark(name="tedana", x=wf.collect_run_data.lzout.out))
    # setting workflow output
    wf.set_output([("out", wf.add.lzout.out)])
