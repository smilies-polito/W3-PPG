""" Signal processing pipeline to estimate Heart Rate (HR) from green-LED PPG.
    The procedure stays the same on all devices.

 1. DC offset removed using the first 5 s; the first 5 s of the filtered signal are discarded (filter settling).

 2. Causal linear-phase FIR band-pass, 0.5-3.5 Hz (513 taps, Hamming); the 2-s group delay is compensated.

 3. Systolic peaks: Elgendi et al. (2013) two-moving-average detector (0.111 s and 0.667 s), adaptive offset = 2 % of the
    mean squared signal over the preceding 2 s, blocks shorter than 0.111 s rejected, peak = maximum of the block.

 4. HR in 12-s windows moved in 2-s steps: median of 60/IBI over IBIs in the 30-210 bpm range, >= 3 valid IBIs required.

The sampling rate is taken from the common time grid of the dataset (128 Hz).
"""

# Copyright (c) 2026 SMILIES Group, Politecnico di Torino, Italy. 
# Authors: Sofia Escobar Londono, Danna Valentina Barrientos Garcia, Irene Rechichi, Gianluca Amprimo, Gabriella Olmo, and Luigi Borzì

# Licensed under the MIT License (see LICENSE file in the repository root).

import numpy as np
from scipy.signal import firwin, lfilter

FS = 128.0
NTAP = 513
B = firwin(NTAP, [0.5, 3.5], pass_zero=False, window='hamming', fs=FS)
GD = (NTAP - 1) // 2                 # group delay, samples (= 2 s)
SETTLE_S = 5.0
WIN_S, STEP_S = 12.0, 2.0
HR_MIN, HR_MAX, MIN_IBI = 30.0, 210.0, 3

def bandpass(x):
    x = np.asarray(x, float)
    x = x - x[: int(SETTLE_S * FS)].mean()
    return lfilter(B, [1.0], np.concatenate([x, np.zeros(GD)]))[GD:]

def _moving_average(x, n):
    n = max(int(round(n)), 1)
    return np.convolve(x, np.ones(n) / n, mode='same')

def detect_peaks(y):
    z = np.clip(y, 0, None) ** 2
    ma_peak, ma_beat = _moving_average(z, 0.111 * FS), _moving_average(z, 0.667 * FS)
    w = int(2 * FS); cs = np.cumsum(np.insert(z, 0, 0.0)); idx = np.arange(1, len(z) + 1)
    trailing = (cs[idx] - cs[np.maximum(idx - w, 0)]) / (idx - np.maximum(idx - w, 0))
    flag = ma_peak > (ma_beat + 0.02 * trailing)
    d = np.diff(np.concatenate([[0], flag.astype(int), [0]]))
    starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
    min_len = int(round(0.111 * FS))
    peaks = np.array([s + int(np.argmax(y[s:e])) for s, e in zip(starts, ends) if e - s >= min_len], int)
    return peaks[peaks >= int(SETTLE_S * FS)]

def window_hr(peaks, duration_s):
    """
    Window start times and window-level HR (NaN if fewer than 3 valid IBIs).
    """

    t0 = np.arange(0, duration_s - WIN_S + 1e-9, STEP_S); pt = peaks / FS; hr = []
    for t in t0:
        p = pt[(pt >= t) & (pt < t + WIN_S)]; ibi = np.diff(p); ibi = ibi[ibi > 0]
        h = 60.0 / ibi; h = h[(h >= HR_MIN) & (h <= HR_MAX)]
        hr.append(np.median(h) if len(h) >= MIN_IBI else np.nan)
    return t0, np.array(hr)
