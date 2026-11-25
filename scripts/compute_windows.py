"""
Compute window-level heart rate (HR) for Persimmon device, Polar and Shimmer
across all recordings in the dataset.

The script processes each recording independently, applies PPG-based
peak detection and HR estimation, and generates a window-level dataset.

Processing parameters:
    - Window duration: 12 s
    - Window step: 2 s
    - Sampling frequency: 128 Hz
    - Device exclusion: manual exclusions and flat-signal detection

Usage:
    python compute_windows.py

    python compute_windows.py --data-dir <dataset_folder> --out <output_file>

Input:
    Per-subject CSV files containing timestamps, activity annotations
    and the green-LED PPG channel of each device.

Output:
    A CSV file containing one row per analysed window, with:
        - Recording identifier (subject ID)
        - Window start time (s)
        - Activity label
        - Window-level HR for each device (NaN if unavailable or excluded)

    A second CSV file (devices_excluded_log.csv) records the devices
    excluded from each recording.

Dataset paths, output directories and default settings are defined
in config.py.

"""

# Copyright (c) 2026 SMILIES Group, Politecnico di Torino, Italy. 
# Authors: Sofia Escobar Londono, Danna Valentina Barrientos Garcia, Irene Rechichi, Gianluca Amprimo, Gabriella Olmo, and Luigi Borzì

# Licensed under the MIT License (see LICENSE file in the repository root).

import argparse, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))   # work from any current folder
import numpy as np, pandas as pd
import hrpipe as H
import config

DEVICES = ['persimmon', 'polar', 'shimmer']
FLAT_MIN_DISTINCT = 50     # a device whose PPG channel has fewer distinct values is treated as flat / not recorded

def load_recording(path):
    """
    Load and validate a single recording.

    Reads the timestamp, activity annotation and green PPG channels
    of Persimmon device, Polar, and Shimmer from a per-subject CSV file.

    Validates the presence of the required columns, that the time axis is
    complete and strictly increasing, and that the sampling rate matches
    the one expected by the pipeline (hrpipe.FS, 128 Hz, tolerance 0.5 Hz).

    Args:
        path (str or os.PathLike): Path to the recording CSV file.

    Returns:
        pandas.DataFrame: Recording data containing the columns:
        ``time``, ``activity``, ``persimmon_ppg_green``, ``polar_ppg_green``
        and ``shimmer_ppg_green``.
        Missing activity labels are kept as NaN.

    Raises:
        ValueError: If required columns are missing, the time column has
            missing or non-increasing values, or the sampling rate differs
            from the expected one.
        FileNotFoundError: If the file does not exist.
    """
    cols = ['time', 'activity'] + [f'{d}_ppg_green' for d in DEVICES]
    header = pd.read_csv(path, nrows=0).columns
    missing = [c for c in cols if c not in header]
    if missing: raise ValueError(f'{os.path.basename(path)}: missing column(s) {missing}')
    df = pd.read_csv(path, usecols=cols, dtype={'activity': str})
    if df.time.isna().any() or not np.all(np.diff(df.time.values) > 0):
        raise ValueError(f'{os.path.basename(path)}: time column must be complete and strictly increasing')
    fs = 1.0 / np.median(np.diff(df.time.values))
    if abs(fs - H.FS) > 0.5: raise ValueError(f'{os.path.basename(path)}: sampling rate is {fs:.1f} Hz, the pipeline expects {H.FS:.0f} Hz')
    return df

def exclusions_from_file(path):
    """
    Load device exclusions from a CSV file.

    The file must contain 'recording' and 'device' columns.
    Each entry identifies a device to be excluded from a specific
    recording.

    Args:
        path (str or os.PathLike): Path to the exclusions CSV file.

    Returns:
        set: Set of (recording, device) pairs to exclude.
             Returns an empty set if the file is not available.
    """
    if not path or not os.path.exists(path): return set()

    e = pd.read_csv(path); return {(r.recording, r.device) for r in e.itertuples()}

def process(path, manual_excl):
    """
    Process a single recording and estimate window-level HR.

    Band-pass filters the green PPG signal of Persimmon, Polar and Shimmer,
    detects systolic peaks and estimates HR in 12-s windows with a 2-s step.
    Devices listed in ``manual_excl`` and devices with a flat PPG signal
    (fewer than FLAT_MIN_DISTINCT distinct values) are not processed.

    For annotated recordings, only windows lying entirely between the
    pre-task synchronisation and the final synchronisation gesture are kept,
    and each window is assigned the activity label covering most of its
    samples. For recordings without annotations, the whole recording is
    used and every window is labelled ``unlabelled``.

    Args:
        path (str or os.PathLike): Path to the recording CSV file.
        manual_excl (set): Set of (recording, device) pairs identifying
            devices excluded manually, e.g. ``('w4z1l6', 'persimmon')``.

    Returns:
        tuple:
            - str: Recording identifier (six-character code from the file
              name, i.e. the subject ID).
            - list of str: Devices excluded from the recording.
            - list of dict: One dictionary per window with the keys
              ``recording``, ``t0`` (window start, s), ``activity`` and one
              HR value (bpm) per device. HR is NaN for excluded devices
              and for windows with fewer than three valid IBIs.

    Raises:
        ValueError: If the recording fails the checks of ``load_recording``.
    """

    rec = os.path.splitext(os.path.basename(path))[0][-6:]       # six-character code of the recording
    df = load_recording(path); t = df.time.values; T = t[-1]
    act = df.activity.fillna('unknown').astype(str).values; labelled = len(set(act)) > 1
    excl = {d for d in DEVICES if (rec, d) in manual_excl or df[f'{d}_ppg_green'].nunique() < FLAT_MIN_DISTINCT}
    t0 = np.arange(0, T - H.WIN_S + 1e-9, H.STEP_S); hr = {}
    for d in DEVICES:
        if d in excl: hr[d] = None; continue
        hr[d] = H.window_hr(H.detect_peaks(H.bandpass(df[f'{d}_ppg_green'].values.astype(float))), T)[1]
    # analysed period: after the pre-task synchronisation, before the closing (end-of-task) gesture
    start, end = 0.0, T
    if labelled:
        pre = np.where(act == 'pre-task')[0]; fin = np.where(np.isin(act, ['end of task', 'final sync']))[0]
        if len(pre): start = t[pre[-1]]
        if len(fin): end = t[fin[0]]
    rows = []
    for j, s0 in enumerate(t0):
        if not (s0 >= start and s0 + H.WIN_S <= end): continue
        a, b = int(round(s0 * H.FS)), int(round((s0 + H.WIN_S) * H.FS))
        label = 'unlabelled'
        if labelled:
            v, c = np.unique(act[a:b], return_counts=True); label = v[c.argmax()]
        rows.append(dict(recording=rec, t0=s0, activity=label,
                         **{d: (np.nan if hr[d] is None else hr[d][j]) for d in DEVICES}))
    return rec, sorted(excl), rows

def main(data_dir=None, out=None, exclusions=None):
    """
    Process the subjects data and create the window-level HR dataset.

    Iterates over all recording files (<code>.csv, without
    subject_data.csv), processes each recording, collects the
    window-level results and saves the final table together with
    a log of the devices excluded from each recording.

    Recordings that cannot be processed are skipped and reported on the
    standard error stream.

    Args:
        data_dir (str or os.PathLike, optional): Dataset directory. If None,
            it is taken from DATA_DIR in config.py, from the environment
            variable HR_DATASET_DIR, or found automatically (see
            config.find_dataset).
        out (str or os.PathLike, optional): Path of the output CSV file. If
            None, ``windows.csv`` in config.OUT_DIR is used. The exclusion
            log ``devices_excluded_log.csv`` is saved in the same folder.
        exclusions (str or os.PathLike, optional): Path of the CSV file
            listing the manually excluded devices. If None,
            config.EXCLUSIONS is used; if the file does not exist, no device
            is excluded manually.

    Returns:
        pandas.DataFrame: Window-level HR results with the columns
            ``recording``, ``t0``, ``activity``, ``persimmon``, ``polar``
            and ``shimmer``, sorted by recording and window start.

    Raises:
        SystemExit: If the dataset folder contains no recording files or
            no recording could be processed.
    """
    data_dir = config.find_dataset(data_dir); exclusions = exclusions or config.EXCLUSIONS
    out = os.fspath(out or os.path.join(config.OUT_DIR, 'windows.csv'))
    files = [os.fspath(p) for p in config.recording_files(data_dir)]
    if not files: sys.exit(f'No recording files (<code>.csv) found in {data_dir}')
    print(f'Dataset folder: {data_dir} ({len(files)} recordings)')
    manual = exclusions_from_file(exclusions); allrows = []; excl_log = {}
    for f in files:
        try: rec, ex, rows = process(f, manual)
        except Exception as e: print(f'SKIPPED {os.path.basename(f)}: {e}', file=sys.stderr); continue
        allrows += rows; excl_log[rec] = ex; print(f'{rec}: {len(rows)} windows, excluded devices: {ex or "none"}')
    if not allrows: sys.exit('no recording could be processed (see the messages above)')
    W = pd.DataFrame(allrows).sort_values(['recording', 't0']).reset_index(drop=True)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); W.to_csv(out, index=False)
    pd.Series({k: ';'.join(v) for k, v in excl_log.items() if v}, name='excluded_devices').rename_axis('recording').to_csv(
        os.path.join(os.path.dirname(os.path.abspath(out)), 'devices_excluded_log.csv'))
    print(f'\n{W.recording.nunique()} recordings, {len(W)} windows -> {out}')
    return W

if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Compute the window-level HR of Persimmon, Polar and Shimmer for every recording of the dataset '
                    '(12-s windows, 2-s step) and save one table with the activity label of each window. '
                    'All options are optional: the defaults are set in config.py.')
    ap.add_argument('--data-dir', help='Folder with the per-subject CSV files. Default: DATA_DIR in config.py, '
                                       'otherwise the folder named "dataset" is searched automatically.')
    ap.add_argument('--out', help='Output CSV file with the window-level table. Default: results/windows.csv next to the scripts.')
    ap.add_argument('--exclusions', help='CSV file (recording, device, reason) listing devices to exclude from specific recordings. '
                                         'Default: device_exclusions.csv next to the scripts.')
    a = ap.parse_known_args()[0]          # unknown arguments are ignored
    main(a.data_dir, a.out, a.exclusions)
