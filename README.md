# Processing of resting state functional connectivity measurements
This is the code repository which was created for the paper “Longitudinal 7T MRS Study of Glutamate and GABA Dynamics in Alzheimer's Disease Progression: From hyper- to hypoexcitation”, Göschel L, 2026.

## 1. Preprocessing (fMRIPrep; see slurm_scripts/fmriprep_sbatch for the command)
Preprocessing was carried out using fMRIPrep v20.1.1 (Esteban et al., 2019). For details about the pipeline, please refer to the official fMRIPrep documentation.

## 2. Seed Definition (see notebooks/coreg_mrs_voxel_masks.ipynb)
Subject-specific MRS voxel masks were coregistered to template space (MNI152NLin2009cAsym) using an ANTs- and FSL-based workflow.

## 3. Seed-to-Voxel Functional Connectivity Analysis (see proc_scripts/seed_to_voxel_sid.py)
Seed and whole-brain time series were extracted. A denoising pipeline using confounds from fMRIPrep was applied. The denoising pipeline comprised 6-mm FWHM spatial smoothing, z-scoring, and band-pass filtering (0.01–0.1 Hz). Whole-brain seed-to-voxel functional connectivities (FC) were obtained as Pearson correlation between the signal of the seed (individual MRS voxel mask coregistered to template) and each brain voxel’s time series.

## 4. Statistical Analysis on the Seed-to-Voxel Functional Connectivity Maps (see proc_scripts/s2v.py)
On the seed-to-voxel FC maps, a second-level GLM analysis was applied using mixed-effects modeling with the following formula:
$$
\mathrm{FC} \sim \text{metabolite} + \text{group} + \text{age} + \text{sex} + (1\mid\text{subject})
$$

## 5. Conversion of the Statistical Analysis Data to NIfTI Files (see notebooks/npy2niftis.ipynb)
The statistical analysis outputs were converted to NIfTI files for visualization and further analysis.

## 6. Slurm Batch Scripts (see slurm_scripts/)
- fmriprep_sbatch: SLURM job script for running fMRIPrep.
- sbatch_seed_to_voxel: SLURM job script for the seed-to-voxel analysis.
- sbatch_s2v: SLURM job script for second-level GLM on FC maps.


## Please Cite
ToDo.
