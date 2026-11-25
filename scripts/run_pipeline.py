"""
Main processing script.

Runs the complete analysis pipeline (either from
the command line or directly from an IDE).

Execution steps:
    1. Compute window-level heart rate.
    2. Calculate agreement statistics.
    3. Plot an example recording figure.
    4. (Optional) Cross-check the agreement statistics against independent implementations.

Input folders and analysis settings can be defined in config.py.
"""

# Copyright (c) 2026 SMILIES Group, Politecnico di Torino, Italy. 
# Authors: Sofia Escobar Londono, Danna Valentina Barrientos Garcia, Irene Rechichi, Gianluca Amprimo, Gabriella Olmo, and Luigi Borzì

# Licensed under the MIT License (see LICENSE file in the repository root).

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))   # work from any current folder
import compute_windows, agreement_stats, plot_recording, check_statistics

if __name__ == '__main__':
    compute_windows.main()
    agreement_stats.main()
    plot_recording.main()

    # Uncomment next line to cross-check the CCC / ICC calculations against independent implementations
    # check_statistics.main()