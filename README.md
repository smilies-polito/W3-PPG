# W3-PPG: A Synchronized Multimodal Dataset of PPG and Inertial Signals from Multiple Wearable Devices

## 1. Overview

W3-PPG is a multimodal wearable-sensor dataset collected from 48 healthy adult participants to support the development and evaluation of methods for physiological signal processing, physical activity recognition, and wearable sensing.

The dataset comprises synchronized recordings acquired using three wearable devices: a prototype device (Persimmon), a consumer device (Polar), and a research-grade device (Shimmer). The devices are equipped with photoplethysmography (PPG) and inertial measurement sensors, with two devices positioned on the forearm and one PPG sensor positioned on the earlobe.

In addition to the physiological and inertial recordings, demographic and anthropometric information was collected, including age, sex, skin phototype, height, weight, arm length, and forearm circumference.

All recordings from the different devices were temporally aligned, enabling joint analysis of physiological and inertial signals acquired at different body locations. Participants performed a standardized sequence of activities representative of common activities of daily living, including sitting, standing, walking, drinking, writing on a computer, using a telephone, and postural transitions. The activities were manually annotated using a synchronized reference video.

The resulting dataset provides a multimodal resource for:

- Investigating motion-related artifacts in PPG signals and developing artifact-removal methods.
- Evaluating PPG-based heart-rate estimation under different movement conditions.
- Assessing the influence of skin phototype and anthropometric characteristics on PPG sensing performance.
- Comparing signal quality and sensing performance across wearable devices and body locations.
- Investigating the relationship between physiological signals and inertial measurements during activities of daily living.

## 2. Study Design

### 2.1. Participants

- **Number of participants:** 48.
- **Sex:** 21 males and 27 females.
- **Age:** Mean age of 41.7 years (range: 23–71 years).
- **Inclusion criteria:** Healthy adults.
- **Exclusion criteria:** Known cardiovascular, neurological, or musculoskeletal conditions, and motor impairments that could affect the quality of the collected data.

### 2.2. Experimental Protocol

Each participant completed a single experimental session in a controlled indoor laboratory environment.

The experimental protocol consisted of a standardized sequence of activities performed in a fixed order:

1. Pre-task.
2. Baseline.
3. Sitting still.
4. Standing still.
5. Using a mobile phone.
6. Using a computer.
7. Drinking water.
8. Walking.
9. Sit-to-stand and stand-to-sit transitions.
10. Final synchronization gestures.

Synchronization gestures were performed at the beginning and end of each recording to support temporal alignment and synchronization assessment.

Each session provided approximately 6–7 minutes of usable recorded data (approximately 360–390 seconds).

## 3. Ethical Compliance and Data Protection

- **Ethics committee:** Ethics Committee for Research of Politecnico di Torino (CER-Polito).
- **Approval ID:** 3441/2026.
- **Informed consent:** Written informed consent was obtained from all participants before data collection.
- **Anonymization:** Participants are identified exclusively through randomly generated six-character alphanumeric codes.
- **Video data:** The reference video used for synchronization and activity annotation is not included in the public dataset.

The dataset is intended exclusively for research purposes. Any attempt to re-identify participants is strictly prohibited.

## 4. Sensor Setup and Data Acquisition

### 4.1. Devices and Sensor Configuration

Three wearable devices were used for physiological and inertial signal acquisition:

| Device | PPG configuration | Inertial sensors | Body location |
|---|---|---|---|
| Persimmon (prototype) | Red, green, and infrared PPG | Accelerometer and gyroscope | Forearm |
| Polar Verity Sense (consumer device) | Green PPG | Accelerometer | Forearm |
| Shimmer GSR+ Unit (research-grade device) | Green PPG | Accelerometer and gyroscope | PPG sensor on the earlobe; inertial sensors on the forearm |

An additional Nordic device, equipped with an accelerometer, was used exclusively to support synchronization with the reference video and activity annotation.

### 4.2. Sampling Rates

The original sampling frequencies were:

| Device | Signal | Original sampling frequency |
|---|---|---:|
| Persimmon | PPG | 128 Hz |
| Persimmon | Accelerometer | 128 Hz |
| Persimmon | Gyroscope | 128 Hz |
| Polar | PPG | 130 Hz |
| Polar | Accelerometer | 55 Hz |
| Shimmer | PPG | 128 Hz |
| Shimmer | Accelerometer | 128 Hz |
| Shimmer | Gyroscope | 128 Hz |
| Nordic | Accelerometer | 64 Hz |

All signals were interpolated onto a common 128 Hz time grid before release.

Consequently, the sampling frequency of the released synchronized recordings is 128 Hz for all signal channels.

### 4.3. Data Synchronization

The synchronization procedure was based on simultaneous arm movements performed at the beginning of each recording. The corresponding acceleration peaks were used as temporal reference events to align the signals acquired by the different devices.

The Nordic accelerometer provided the reference timeline for synchronization with the video recordings. Activity annotations were subsequently obtained through manual review of the synchronized reference video.

After temporal alignment, all signals were interpolated onto a common 128 Hz time grid.

The released files contain a relative time variable (`time`), expressed in seconds and set to zero at the synchronization reference point. This time variable does not represent Unix time or an absolute timestamp.

The residual synchronization error between devices was:

- Median and interquartile range (IQR): 72 ms (47–94 ms).
- 80% of the measured values were below 100 ms.

## 5. Dataset Structure and File Formats

### 5.1. File Organization

The dataset consists of:

- One CSV file per participant containing synchronized physiological signals, inertial measurements, and activity annotations.
- One additional CSV file containing demographic and anthropometric information for all participants.

The dataset directory is organized as follows:

```text
dataset/
├── 3wz5r7.csv
├── 6fj9p2.csv
├── a2r7m6.csv
├── a7k2m9.csv
├── ...
└── subject_data.csv
```

The six-character alphanumeric filename identifies the corresponding participant.

### 5.2. Synchronized Sensor Data

Each participant's sensor file is provided in CSV format, with a single header row.

The following columns are included:

| Column | Description |
|---|---|
| `time` | Relative time in seconds |
| `persimmon_acc_x` | Persimmon accelerometer, X-axis |
| `persimmon_acc_y` | Persimmon accelerometer, Y-axis |
| `persimmon_acc_z` | Persimmon accelerometer, Z-axis |
| `persimmon_gyr_x` | Persimmon gyroscope, X-axis |
| `persimmon_gyr_y` | Persimmon gyroscope, Y-axis |
| `persimmon_gyr_z` | Persimmon gyroscope, Z-axis |
| `persimmon_ppg_red` | Persimmon red PPG |
| `persimmon_ppg_green` | Persimmon green PPG |
| `persimmon_ppg_infrared` | Persimmon infrared PPG |
| `shimmer_acc_x` | Shimmer accelerometer, X-axis |
| `shimmer_acc_y` | Shimmer accelerometer, Y-axis |
| `shimmer_acc_z` | Shimmer accelerometer, Z-axis |
| `shimmer_gyr_x` | Shimmer gyroscope, X-axis |
| `shimmer_gyr_y` | Shimmer gyroscope, Y-axis |
| `shimmer_gyr_z` | Shimmer gyroscope, Z-axis |
| `shimmer_ppg_green` | Shimmer green PPG |
| `nordic_acc_x` | Nordic accelerometer, X-axis |
| `nordic_acc_y` | Nordic accelerometer, Y-axis |
| `nordic_acc_z` | Nordic accelerometer, Z-axis |
| `polar_acc_x` | Polar accelerometer, X-axis |
| `polar_acc_y` | Polar accelerometer, Y-axis |
| `polar_acc_z` | Polar accelerometer, Z-axis |
| `polar_ppg_green` | Polar green PPG |
| `activity` | Activity/task annotation |

**Signal units:**

- **Time:** Seconds, relative to the synchronization reference point.
- **PPG:** Raw sensor units (device-dependent, dimensionless).
- **Accelerometer:** g.
- **Gyroscope:** degrees per second (°/s).
- **Activity:** Categorical text label.

The Polar PPG signal was scaled by a factor of 2000 during preprocessing to improve the consistency of signal representation across devices. This scaling does not imply that the PPG signals from different devices are calibrated or directly comparable in absolute amplitude. However, this ensures comparable signal amplitude ranges across devices when considering band-pass-filtered signals (0.5–3.5 Hz).

### 5.3. Activity Labels and Annotations

Each sample is associated with an `activity` label indicating the activity performed by the participant at that time.

The annotations include the following activity categories:

- Pre-task.
- Baseline.
- Sitting still.
- Standing still.
- Using a mobile phone.
- Using a computer.
- Drinking water.
- Walking.
- Sit-to-stand transition.
- Stand-to-sit transition.
- Final synchronization.

Activity annotations were manually assigned through frame-by-frame review of the synchronized reference video.

Samples outside annotated activity intervals are left empty.

Recordings for which reliable synchronization with the reference video could not be established do not contain reliable activity annotations.

### 5.4. Demographic and Anthropometric Data

Participant demographic and anthropometric information is provided in the additional CSV file `subject_data.csv`.

The file contains one row per participant and the following variables:

| Column | Description |
|---|---|
| `subject_id` | Six-character alphanumeric participant identifier corresponding to the sensor-data filename |
| `age` | Age in years (range: 23–71) |
| `sex` | Participant's sex (M/F); 21 M and 27 F |
| `height` | Height in cm (range: 155–185 cm) |
| `weight` | Body weight in kg (range: 43–90 kg) |
| `bmi` | Body mass index in kg/m² (range: 16.9–33.6) |
| `skin_phototype` | Fitzpatrick skin phototype (Types I–VI) |
| `arm_length` | Arm length in cm (range: 46–61 cm) |
| `forearm_circumference` | Forearm circumference in cm (range: 20–31 cm) |
| `fitness_level` | Self-reported or assessed physical activity level: Sedentary, Light active, Moderately active, or Very active |

## 6. Data Quality and Limitations

All recordings were inspected to identify acquisition-related issues, missing sensor data, and inconsistencies affecting synchronization or activity annotation.

The following recording-specific issues were identified:

- **Recording `b8v5y2`:** The Shimmer PPG signal is considered unreliable due to incorrect positioning of the earlobe probe during acquisition.
- **Recording `y5m9b4`:** Incorrect positioning of the Polar sensor resulted in an abnormal noise pattern in the recorded PPG signal.
- **Recording `w4z1l6`:** The Persimmon strap was visibly loose throughout the session.
- **Recording `d5m2r7`:** The Polar PPG signal was acquired during the session but was not successfully stored by the mobile logging application. Consequently, this signal is missing from the released data.
- **Recording `v9p1h5`:** Saturation of the Shimmer accelerometer prevented reliable synchronization of this device with the other sensors. Therefore, Shimmer data are not provided for this recording.
- **Recordings `y8k4p1`, `r6v9a3`, `x1j5g8`, `g7n2t4`, `w3b6z9`, and `j4f8c2`:** Nordic accelerometer data are unavailable. Since these data were required to establish reliable temporal alignment between the reference video and the physiological recordings, reliable activity annotations could not be assigned. These recordings may nevertheless be used for analyses that do not require activity-specific labels, provided that the available physiological signals pass the corresponding quality checks.

**Overall data availability:**

| Device/data | Availability |
|---|---:|
| Persimmon | 48/48 recordings |
| Polar | 47/48 recordings |
| Shimmer | 47/48 recordings |
| Nordic | 42/48 recordings |
| Reliable activity annotations | 42/48 recordings |

The availability figures refer to the presence of data, not necessarily to their signal quality. Some recordings contain sensor data that are available but affected by acquisition-related issues described above.

In the released CSV files, unavailable sensor channels are represented by zeros. Activity labels in recordings without reliable annotations are also filled with zeros.

**Important:** Users should consult the recording-specific limitations above before selecting recordings for analysis. In particular, zero-filled channels must not be interpreted as valid physiological or inertial measurements.

## 7. Usage Guidelines

The dataset is intended primarily for scientific and methodological research.

**Permitted uses:**

- Academic and non-commercial research.
- Development and evaluation of physiological signal-processing methods.
- Development and benchmarking of activity-recognition algorithms.
- Research on wearable sensing, motion artifacts, and PPG signal quality.
- Comparative studies of wearable devices and sensing locations.

**Restricted uses:**

- Clinical decision-making or direct clinical diagnosis.
- Commercial use without an appropriate license or authorization.
- Any attempt to identify or re-identify individual participants.

Users should acknowledge the dataset in any publication or scientific work making use of it.

## 8. Code and Reproducibility

The `scripts/` folder contains the code used to compute the descriptive statistics of the dataset paper: window-level heart rate (HR) from the green-LED PPG of the three devices, and agreement between the devices.

### 8.1. File layout
```text
├── dataset/
│   ├── 3wz5r7.csv               # one file per participant (six-character code)
│   ├── 6fj9p2.csv
│   ├── ...
│   └── subject_data.csv         # demographic and anthropometric data
├── scripts/
│   ├── config.py                # settings:  input/output folder, bootstrap, seed
│   ├── hrpipe.py                # HR pipeline: filter, peak detection, windowed HR
│   ├── compute_windows.py       # step 1: window-level HR from the raw signals
│   ├── agreement_stats.py       # step 2: agreement metrics between devices
│   ├── plot_recording.py        # step 3: plot activity time series
│   ├── check_statistics.py      # optional: cross-check CCC/ICC with modules
│   ├── run_pipeline.py          # runs the steps in order
│   ├── device_exclusions.csv    # devices excluded from specific recordings
│   └── requirements.txt         # Python dependencies
├── .gitignore                   # ignores scripts/results/, __pycache__/, .DS_Store
├── LICENSE                      # MIT licence of the code
└── README.md
```

### 8.2 Usage Notes

pip install -r scripts/requirements.txt
python scripts/run_pipeline.py

The dataset folder is found automatically if the scripts are inside the repository. To use data stored elsewhere, set `DATA_DIR` in `config.py`, set the environment variable `HR_DATASET_DIR`, or pass `--data-dir`. Every script can also be run alone and has `--help`. Outputs are written to `scripts/results/`.

The `scripts/results/` subfolder is created on the first run. 

For reference, the input/outputs are:

| Step | Script | Input | Output (in `scripts/results/`) |
|---|---|---|---|
| 1 | `compute_windows.py` | `dataset/<code>.csv`, `device_exclusions.csv` | `windows.csv`, `devices_excluded_log.csv` |
| 2 | `agreement_stats.py` | `windows.csv` | `agreement_overall.csv`, `agreement_by_activity.csv` |
| 3 | `plot_recording.py` | `dataset/<code>.csv` | `recording_<code>.png` |
| 4 (optional) | `check_statistics.py` | `windows.csv` | printed OK/MISMATCH report (exit status 0 or 1) |

### 8.3 Processing Pipeline Summary
- PPG: first 5 s used for the DC offset and then discarded; causal 513-tap FIR band-pass 0.5-3.5 Hz with the 2-s group delay compensated.
- Peaks: Elgendi et al. (2013) two-moving-average detector.
- HR: median of 60/IBI in 12-s windows moved in 2-s steps (30-210 bpm, at least 3 valid IBIs).
- Agreement (per device pair): MAE, RMSE, bias, 95% limits of agreement, Pearson r, % within 5 and 10 bpm, MAPE and Lin's CCC; ICC(A,1) for the three devices. 95% CIs by participant-level cluster bootstrap (1000 resamples, seed 7). Results overall and by activity.

## 9. Citation and License

If you use this dataset in your research, please cite it as follows:

[Insert recommended dataset citation and DOI]

Data: CC BY-NC 4.0.
Code: MIT (see `LICENSE`).

## 10. Contact Information

For questions regarding the dataset, acquisition protocol, or data interpretation, please contact:

- **Contact person:** Luigi Borzì
- **Institution:** Politecnico di Torino
- **Email:** Luigi.borzi@polito.it
