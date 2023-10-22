# fMRIPost-tedana

A BIDS App for the tedana workflow

## Overview

1.  A BIDS data grabber to collect the first echo from each run.
2.  A BIDS data grabber to grab the other echoes, brain mask, echo times, and potentially confounds.
3.  Drop dummy volumes as requested.
4.  Run tedana.
5.  Reorganize tedana outputs into BIDS format.
6.  Generate nireports HTML report.
