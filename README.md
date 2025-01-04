# fMRIPost-tedana

A BIDS App for the tedana workflow

## Overview

fMRIPost-tedana post-processes multi-echo fMRI data that have been
minimally preprocessed with fMRIPrep.
In addition to the basic multi-echo independent components analysis (ME-ICA) performed by tedana,
fMRIPost-tedana will leverage fMRIPrep derivatives,
like extracted confounds and high-resolution tissue masks,
to improve the multi-echo denoising performance.

## Workflow

1.  A BIDS data grabber to collect the first echo from each run.
2.  A BIDS data grabber to grab the other echoes, brain mask, echo times, and potentially confounds.
3.  Drop dummy volumes as requested.
4.  Run tedana.
    -   Limit to the brain mask.
    -   Extract echo times from metadata.
    -   Include fMRIPrep confounds as external regressors.
    -   Incorporate tissue type masks in decision tree?
5.  Supplement ME-ICA with other component classification algorithms.
    -   AROMA?
    -   CTLP?
6.  Reorganize tedana outputs into BIDS format.
7.  Denoise optimally combined data in target spaces.
8.  Generate figures summarizing the denoising results.
    -   Carpet plots of denoised data
    -   T2* map
    -   S0 map
    -   Component weight maps, time series, periodograms, and classifications
    -   Components-by-confound correlation heat map
9.  Generate nireports HTML report.
