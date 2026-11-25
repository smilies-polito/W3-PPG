"""Settings shared by all scripts and dataset folder.

The dataset is expected as in the repository:
    1. For subject-level data: dataset/<code>.csv 
    2. For subject metadata: dataset/subject_data.csv

Scripts should be stored inside the repository (in a `scripts/` folder).

To use a dataset stored elsewhere, do one of the following:
    - set DATA_DIR below to the dataset folder;
    - set the environment variable HR_DATASET_DIR;
    - pass --data-dir to the script.

Results are written to OUT_DIR (default: `results/` next to the scripts).
"""

# Copyright (c) 2026 SMILIES Group, Politecnico di Torino, Italy. 
# Authors: Sofia Escobar Londono, Danna Valentina Barrientos Garcia, Irene Rechichi, Gianluca Amprimo, Gabriella Olmo, and Luigi Borzì

# Licensed under the MIT License (see LICENSE file in the repository root).


import os, re
from pathlib import Path
try:    HERE = Path(__file__).resolve().parent
except NameError: HERE = Path.cwd()                        # e.g. when pasted into a notebook

DATA_DIR   = None                  # None = find the dataset folder automatically; or write your own path, e.g. Path(r'C:\data\dataset')
OUT_DIR    = HERE / 'results'      # all outputs are written here
EXCLUSIONS = HERE / 'device_exclusions.csv'
BOOTSTRAP  = 1000                  # bootstrap resamples for the confidence intervals
SEED       = 7
RECORDING  = None                  # recording to plot, e.g. 'z1l4d6'; None = the first one found

_CODE = re.compile(r'(^|[^a-z0-9])[a-z0-9]{6}\.csv$')      # <code>.csv  or  <prefix>-<code>.csv

def recording_files(folder):
    """The per-subject CSV files of a folder (six-character code), without subject_data.csv, in a fixed order."""
    return sorted(p for p in Path(folder).glob('*.csv') if _CODE.search(p.name) and 'subject_data' not in p.name)

def _is_dataset(folder):
    return folder.is_dir() and ((folder / 'subject_data.csv').exists() or len(recording_files(folder)) > 0)

def find_dataset(explicit=None):
    """Return the dataset folder. Order: explicit argument, DATA_DIR, environment variable HR_DATASET_DIR, then a folder named
    `dataset` (or `data`) in the scripts' folder, in its parent folders (up to 3 levels), or in the current working folder."""
    for c in (explicit, DATA_DIR, os.environ.get('HR_DATASET_DIR')):
        if c:
            p = Path(c).expanduser()
            if not p.is_dir(): raise SystemExit(f'Data folder not found: {p}')
            return p
    bases = [HERE, *list(HERE.parents)[:3], Path.cwd(), *list(Path.cwd().parents)[:2]]; tried = []
    for b in bases:
        for name in ('dataset', 'data', ''):
            p = b / name if name else b
            if p in tried: continue
            tried.append(p)
            if _is_dataset(p): return p
    raise SystemExit('Dataset folder not found. Looked in:\n  ' + '\n  '.join(str(t) for t in tried) +
                     '\nSet DATA_DIR in config.py, the environment variable HR_DATASET_DIR, or use --data-dir.')
