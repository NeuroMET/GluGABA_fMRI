# Processing of resting state functional connectivity measurements
This is the code repository which was created for the paper “Longitudinal 7T MRS Study of Glutamate and GABA Dynamics in Alzheimer's Disease Progression: From hyper- to hypoexcitation”, Göschel L, 2026.

## 1. Preprocessing (fMRIprep, see fmri/fmriprepcmd for the command and fmriprep/example_fmriprep.html for the preoprocessing description)
Preprocessing was carried out using fMRIPrep v20.1.1 (Esteban et al., 2019). An example fMRIprep output file can be found under example_fmriprep.html. The pipeline is described in the method section of this file.

## 2. Denoising, matrix extraction and averaging across networks (see notebooks/Functional_connectivities.ipynb)
Our denoising strategy involved the selection from fmriprep confounds of 24 motion parameters, four global signal parameters, the white matter (WM) and cerebrospinal fluid (CSF) components from the anatomical component-based correction (aCompCor, two components) and the noise independent components from ICA-AROMA. Additionally, a smoothing with full-width half-maximum of 6 mm and a filter with passband between 0.008 Hz and 0.1 Hz pass was applied. The denoising pipeline was implemented with NiLearn (Abraham et al., 2014).

## 3. (see notebooks/Functional_connectivities.ipynb)
Subject-specific MRS voxel masks were coregistered to the MNI152NLin2009cAsym template, and seed time series were extracted using a standardized workflow comprising 6-mm FWHM spatial smoothing, z-scoring, and band-pass filtering (0.01–0.1 Hz). Whole-brain seed-to-voxel functional connectivitites (FC) were obtained as Pearson correlation between the signal of the seed (individual MRS voxel) and each voxel’s time series.

## Please Cite
-) Dell'Orco, A., & Göschel, L. (2026). GluGaba - fMRi pipeline (0.1). Zenodo. https://doi.org/...
