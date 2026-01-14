import os
from nilearn.maskers import NiftiMasker
from nilearn.interfaces.fmriprep import load_confounds
from nilearn.maskers import NiftiLabelsMasker
import sys 
import numpy as np


ex_sid = sys.argv[1]

# 1. Resolve input files for the subject ID
# Use environment variable to avoid personal paths; set BIDS_ROOT accordingly.
bids_root = os.environ.get('BIDS_ROOT', '/path/to/NeuroMET')
fmriprep_der = os.path.join(bids_root, 'derivatives/fmriprep')
mrs_masks_dir = os.path.join(bids_root, 'derivatives/coreg_mrs_masks')


bold = os.path.join(fmriprep_der, '{sid}', 'func', '{sid}_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
confounds = os.path.join(fmriprep_der,'{sid}', 'func', '{sid}_task-rest_desc-confounds_timeseries.tsv')
mrs_mask = os.path.join(mrs_masks_dir, '{sid}', 'anat', '{sid}_space-MNI152NLin2009cAsym_desc-pcc-voxel_mask.nii.gz')
brain_mask = os.path.join(fmriprep_der, '{sid}', 'anat', '{sid}_acq-UNIbrainDENskull_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz')

bold_sid = bold.format(sid=ex_sid)
confounds_sid = confounds.format(sid=ex_sid)
mrs_mask_sid = mrs_mask.format(sid=ex_sid)
brain_mask_sid = brain_mask.format(sid=ex_sid)

# Minimal input validation
for path in (bold_sid, confounds_sid, mrs_mask_sid, brain_mask_sid):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing input: {path}")

# 2. Load fMRIprep confounds
print("Loading confounds for", ex_sid)
confounds_simple, sample_mask = load_confounds(
    bold_sid,
    strategy=['motion', 'compcor', 'scrub', 'high_pass'],
    motion='full',
    scrub=0.5,  # or omit entirely if not doing scrubbing
    compcor='anat_separated',
    n_compcor=5,
    fd_threshold=0.5,
    std_dvars_threshold=3.0,
)

# 3. Load the seed  masks and extract time series
print("Extracting seed time series for", ex_sid)
seed_masker = NiftiLabelsMasker(
    labels_img=mrs_mask_sid,
    standardize="zscore_sample",
    verbose=5,
    resampling_target='data',
    smoothing_fwhm=6,
    detrend=True,
    high_pass=0.01,
    t_r=2.0,
    low_pass=0.1,
    memory='nilearn_cache',
    memory_level=1)

seed_timeseries = seed_masker.fit_transform(bold_sid, 
                                            confounds=confounds_simple,
                                            sample_mask=sample_mask)

# 4. Load the brain mask and extract time series
print("Extracting brain time series for", ex_sid)
brain_masker = NiftiMasker(
    mask_img=brain_mask_sid,
    standardize="zscore_sample",
    verbose=5,
    resampling_target='data',
    smoothing_fwhm=6,
    detrend=True,       
    high_pass=0.01,
    t_r=2.0,
    low_pass=0.1,
    memory='nilearn_cache',
    memory_level=1)

brain_timeseries = brain_masker.fit_transform(bold_sid, 
                                              confounds=confounds_simple,
                                              sample_mask=sample_mask)


# 5 Compute correlations 
print("Computing seed-to-voxel correlations for", ex_sid)
seed_to_voxel_correlations = (
    np.dot(brain_timeseries.T, seed_timeseries) / seed_timeseries.shape[0]
)

# 6 Reshape and save the results

print("Reshaping and saving results for", ex_sid)

seed_to_voxel_2d = seed_to_voxel_correlations.reshape(1, -1)  # shape (1, 1350875)

seed_to_voxel_img = brain_masker.inverse_transform(seed_to_voxel_2d)

def s2v_dest_path(bold_sid):
    return bold_sid.replace("preproc", "MRSVOI-to-Voxel").replace('fmriprep', 'MRSVOI-to-Voxel')

dest_name = s2v_dest_path(bold_sid)

if not os.path.exists(os.path.dirname(dest_name)):
    os.makedirs(os.path.dirname(dest_name))

seed_to_voxel_img.to_filename(dest_name)