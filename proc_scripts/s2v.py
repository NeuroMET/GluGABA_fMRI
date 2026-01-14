import numpy as np
import nibabel as nib 
import os
import sys

src_dir = os.path.dirname(os.path.abspath(__file__))

metab = sys.argv[1]  # one of 'glu', 'gaba', 'glu_gaba'
n_jobs = int(sys.argv[2]) if len(sys.argv) > 2 else 5

# Base derivatives directory; set DERIV_ROOT to anonymize local paths.
DERIV_ROOT = os.environ.get('DERIV_ROOT', '/path/to/NeuroMET/derivatives')


# Load covariates (expects fMRI_dataset.csv in the working directory)
import pandas as pd
covariates = pd.read_csv('fMRI_dataset.csv').drop(columns=['Unnamed: 0'])

import re
# Extract sid and ses from 'BIDS MRI session' column
covariates['sid'] = covariates['BIDS MRI session'].apply(lambda x: re.match(r'(sub-NeuroMET\d+)', str(x)).group(1) if pd.notnull(x) and re.match(r'(sub-NeuroMET\d+)', str(x)) else None)
covariates['ses'] = covariates['BIDS MRI session'].apply(lambda x: re.match(r'sub-NeuroMET\d+(\d{2})', str(x)).group(1) if pd.notnull(x) and re.match(r'sub-NeuroMET\d+(\d{2})', str(x)) else None)


# Analysis 1: included 
covariates = covariates[(covariates['included'] == 1) & (covariates['diagnose_group'].notna())]
covariates = covariates[['BIDS MRI session', 'sid', 'age', 'sex', 'diagnose_group', 'glu', 'gaba', 'glu_gaba']]


sub_m = os.path.join(
    DERIV_ROOT,
    'MRSVOI-to-Voxel',
    '{sid}',
    'func',
    '{sid}_task-rest_space-MNI152NLin2009cAsym_desc-MRSVOI-to-Voxel-masked_bold.nii.gz'
)
mrs2voxel_masked_sids2 = [sub_m.format(sid=sid) for sid in covariates['BIDS MRI session'].values]

stacked_conns = np.stack([nib.load(conn).get_fdata().squeeze() for conn in mrs2voxel_masked_sids2], axis=-1)

from statsmodels.formula.api import mixedlm
from joblib import Parallel, delayed

n_coeffs = 8
zs = np.zeros((101, 125, 107, n_coeffs))
coeffs = np.zeros((101, 125, 107, n_coeffs))
ps = np.zeros((101, 125, 107, n_coeffs))

def process_voxel(x, y, z):
    global stacked_conns
    global covariates
    df = covariates.copy()
    df['voxel'] = stacked_conns[x, y, z, :]
    model = mixedlm(f'voxel ~ {metab} + diagnose_group + age + sex', df, groups=df['sid'])
    result = model.fit()
    return x, y, z, result.tvalues.values, result.params.values, result.pvalues.values

results = Parallel(n_jobs=n_jobs)(delayed(process_voxel)(x, y, z) for x in range(101) for y in range(125) for z in range(107))

for x, y, z, tvalues, params, pvalues in results:
    zs[x, y, z, :] = tvalues
    coeffs[x, y, z, :] = params
    ps[x, y, z, :] = pvalues


np.save(f'{metab}_zs.npy', zs)
np.save(f'{metab}_coeffs.npy', coeffs)
np.save(f'{metab}_ps.npy', ps)
