.. include:: links.rst

===========================
Processing pipeline details
===========================

*fMRIPost-tedana* adapts its pipeline depending on what data and metadata are
available and are used as the input.
For example, slice timing correction will be
performed only if the ``SliceTiming`` metadata field is found for the input
dataset.

A (very) high-level view of the simplest pipeline is presented below:

.. workflow::
    :graph2use: orig
    :simple_form: yes

    from fmripost_tedana.workflows.tests import mock_config
    from fmripost_tedana.workflows.base import init_single_subject_wf

    with mock_config():
        wf = init_single_subject_wf('01')


**********
Input Data
**********

*fMRIPost-tedana* expects minimally preprocessed fMRIPrep derivatives as input.
The fMRIPrep derivatives should include individual preprocessed echoes in BOLD reference space.

Additionally, users can provide the raw dataset in addition to the fMRIPrep derivatives.


***********************
Slice Timing Correction
***********************

*fMRIPost-tedana* will apply slice-timing correction to the magnitude data.


**********************************
Resampling to BOLD Reference Space
**********************************

*fMRIPost-tedana* will resample the individual echoes to the BOLD reference space.


********************
Multi-echo Denoising
********************

*fMRIPost-tedana* will perform multi-echo independent components analysis (ME-ICA)
on the resampled echoes.


*******************
Confound Extraction
*******************
