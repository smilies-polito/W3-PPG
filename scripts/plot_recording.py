"""
Time-series plot of the window-level HR estimated by
Persimmon, Polar and Shimmer for a selected recording.

The script applies the same PPG processing pipeline, device exclusion
criteria and analysed-period selection as compute_windows.py.
Activity intervals are shaded and labelled to provide context for
the comparison between devices.

Plot characteristics:
    - HR estimates are displayed at the end of each 12-s analysis window.
    - Activity intervals are represented by coloured background shading.
    - Excluded devices are omitted from the plot.
    - The HR axis limits are automatically expanded when necessary
      to include all available measurements.

Usage:
    python plot_recording.py

    python plot_recording.py --data-dir <dataset_folder> 
                             --recording <recording_code>
                             [--out <output_file>]

Input:
    Per-subject CSV file containing timestamps, activity annotations
    and the green-LED PPG channels of the three devices.

Output:
    A figure showing the window-level HR time series and annotated
    activity intervals for the selected recording.

The recording identifier, dataset paths, output directory and default
settings are defined in config.py.
"""

# Copyright (c) 2026 SMILIES Group, Politecnico di Torino, Italy. 
# Authors: Sofia Escobar Londono, Danna Valentina Barrientos Garcia, Irene Rechichi, Gianluca Amprimo, Gabriella Olmo, and Luigi Borzì

# Licensed under the MIT License (see LICENSE file in the repository root).

import argparse, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))   # work from any current folder
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import hrpipe as H
import config
from compute_windows import load_recording, exclusions_from_file, DEVICES, FLAT_MIN_DISTINCT

plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica', 'TeX Gyre Heros', 'Arial', 'Liberation Sans', 'DejaVu Sans'],
                     'pdf.fonttype': 42, 'axes.linewidth': 0.8})
BAND = {
    'still': '#bfe7fb',
        'using the phone': '#f2d2f2',
        'drinking water': '#fddcbf',
        'using the computer': '#d4d4f3',
        'still (standing)': '#d8d1f4',
        'stand up': '#e9f6b4',
        'sit down': '#c9d5f6',
        'walking': '#fbd0e0'
        }   # edit colour HEX to change the background colours for the plot (Activities)


LINE = {
    'persimmon': '#1b6fd0',
        'polar': '#f4622a',
        'shimmer': '#2fa84c'
        }   # edit colour HEX to change the line colours for the plot (Devices)

def main(data_dir=None, recording=None, out=None, ylim=(50, 130), exclusions=None):
    """
    Plot an HR comparison plot for a selected recording.

    Loads and validates the selected recording, estimates window-level
    HR for each available device, and generates a time-series plot
    with activity intervals shaded and labelled.

    The processing pipeline, device exclusion criteria and analysed
    period are consistent with compute_windows.py.

    Args:
        data_dir (str, optional): Dataset directory. If None, the
            default directory or automatic dataset discovery defined
            in config.py is used.
        recording (str, optional): Six-character recording identifier.
            If None, config.RECORDING is used; otherwise, the first
            available recording is selected.
        out (str, optional): Output figure path. The file format is
            determined by its extension. Defaults to
            recording_<code>.png in config.OUT_DIR.
        ylim (tuple, optional): Initial lower and upper limits of the
            HR axis (bpm). The limits are automatically expanded
            if necessary to include all available measurements.
        exclusions (str, optional): Path to the manual device
            exclusions CSV file. If None, config.EXCLUSIONS is used.

    Returns:
        str: Path to the generated figure.
    """

    data_dir = config.find_dataset(data_dir); exclusions = exclusions or config.EXCLUSIONS
    files = [os.fspath(p) for p in config.recording_files(data_dir)]
    recording = recording or config.RECORDING or (os.path.splitext(os.path.basename(files[0]))[0][-6:] if files else None)
    path = [f for f in files if os.path.splitext(os.path.basename(f))[0].endswith(str(recording))]
    if len(path) != 1: raise SystemExit(f'recording {recording}: expected one file in {data_dir}, found {len(path)}')
    out = os.fspath(out or os.path.join(config.OUT_DIR, f'recording_{recording}.png')); os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    df = load_recording(path[0]); t = df.time.values; manual = exclusions_from_file(exclusions)
    act = df.activity.fillna('unknown').astype(str).values; labelled = len(set(act)) > 1
    start, end = 0.0, t[-1]                                            # analysed period, as in compute_windows.py
    if labelled:
        pre = np.where(act == 'pre-task')[0]; fin = np.where(np.isin(act, ['end of task', 'final sync']))[0]
        if len(pre): start = t[pre[-1]]
        if len(fin): end = t[fin[0]]
    fig, ax = plt.subplots(figsize=(7.4, 3.4)); lo, hi = ylim
    series = {}
    for d in DEVICES:
        if (recording, d) in manual or df[f'{d}_ppg_green'].nunique() < FLAT_MIN_DISTINCT: continue
        t0, hr = H.window_hr(H.detect_peaks(H.bandpass(df[f'{d}_ppg_green'].values.astype(float))), t[-1])
        keep = (t0 >= start) & (t0 + H.WIN_S <= end); series[d] = (t0[keep] + H.WIN_S, hr[keep])
    x_min = min(x[0] for x, _ in series.values()); x_max = max(x[-1] for x, _ in series.values())
    vals = np.concatenate([h for _, h in series.values()]); lo, hi = min(lo, np.nanmin(vals) - 2), max(hi, np.nanmax(vals) + 2)
    if labelled:                                                       # shaded, labelled activity intervals
        idx = np.where((t >= x_min) & (t <= x_max))[0]
        seg = idx[np.r_[0, np.where(act[idx][1:] != act[idx][:-1])[0] + 1]]
        edges = np.r_[seg, idx[-1]]
        for s, e in zip(edges[:-1], edges[1:]):
            lab = act[s]; x0, x1 = t[s], t[e] if e != edges[-1] else t[idx[-1]]
            if lab not in BAND: continue
            ax.axvspan(x0, x1, color=BAND[lab], lw=0, zorder=0)
            w = x1 - x0; ymid = hi - 0.2 * (hi - lo)
            if w >= 3: ax.text((x0 + x1) / 2, ymid, lab.replace('using the ', 'using the\n') if (w > 14 and ' ' in lab and w < 40 and lab.startswith('using')) else lab,
                               ha='center', va='center', fontsize=7 if w > 12 else 5.5, rotation=0 if w > 12 else 90, linespacing=0.95, zorder=2)
    for d, (x, y) in series.items():
        ax.plot(x, y, '-o', color=LINE[d], lw=1.2, ms=2.4, label=d.capitalize(), zorder=3)
    ax.set_xlim(x_min, x_max); ax.set_ylim(lo, hi); ax.set_xlabel('Time (s)', fontsize=11); ax.set_ylabel('HR (bpm)', fontsize=11)
    ax.tick_params(labelsize=9); ax.spines[['top', 'right']].set_visible(False)
    ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), frameon=True, edgecolor='#333333', fancybox=False, fontsize=9)
    fig.tight_layout(); fig.savefig(out, dpi=200); print('saved', out)
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(
        description='Plot the window-level HR of the three devices over one recording, with the activity intervals shaded and labelled. '
                    'All options are optional: the defaults are set in config.py.')
    ap.add_argument('--data-dir', help='Folder with the per-subject CSV files. Default: DATA_DIR in config.py, '
                                       'otherwise the folder named "dataset" is searched automatically.')
    ap.add_argument('--recording', help='Six-character code of the recording to plot (the file name without .csv). '
                                        'Default: RECORDING in config.py, otherwise the first recording found.')
    ap.add_argument('--out', help='Output figure; the format follows the extension (.png, .pdf, ...). Default: results/recording_<code>.png.')
    ap.add_argument('--exclusions', help='CSV file (recording, device, reason) listing devices to exclude. Default: device_exclusions.csv.')
    ap.add_argument('--ylim', type=float, nargs=2, default=[50, 130], metavar=('LOW', 'HIGH'),
                    help='Limits of the HR axis in bpm. The axis widens automatically if the data fall outside. Default: 50 130.')
    args = ap.parse_known_args()[0]       # unknown arguments (injected by some IDEs / notebooks) are ignored
    main(args.data_dir, args.recording, args.out, tuple(args.ylim), args.exclusions)
