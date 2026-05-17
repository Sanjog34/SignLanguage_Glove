# Sign Language Glove — Nepali Sign Language to Speech

A wearable glove system that translates **Nepali Sign Language (NSL)** gestures into spoken audio in real time. Built as a final year engineering project, the system combines embedded hardware, machine learning, and audio playback into a seamless end-to-end pipeline.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Microcontroller | ESP32 (OneHorse 32 Dev Board) |
| Firmware | C++ via PlatformIO + Arduino framework |
| Sensors | Flex sensors (finger bend) + MPU-6050 (gyroscope/accelerometer) |
| ML Training | Python, Jupyter Notebook, scikit-learn |
| Model Format | joblib (serialized sklearn models) |
| Filesystem | LittleFS (on-device file storage) |
| Audio Output | Pre-recorded `.wav` sound files |
| Data Format | JSON (raw + augmented datasets) |

---

## Repository Structure

```
SignLanguage_Glove/
├── src/                  # C++ firmware (ESP32 main logic)
├── include/              # Header files
├── lib/                  # External libraries
├── PCB/                  # PCB design files for custom glove board
├── data/                 # Raw sensor recordings
├── datasets/             # Processed datasets for training
├── JSON_DYNAMIC_DATA/    # Live sensor readings in JSON format
├── JSON_AUGMENTED/       # Augmented training data (JSON)
├── jupyter/              # Jupyter notebooks for model training & evaluation
├── models(joblib)/       # Trained ML models serialized with joblib
├── sounds/               # Audio files (.wav) for each sign/word
├── gyro sym/             # Gyroscope symbol/simulation files
├── test/                 # Test scripts
└── platformio.ini        # PlatformIO build configuration
```

---

## Data Flow (End-to-End)

### 1. Sensor Acquisition (Hardware → ESP32)
Flex sensors on each finger and an MPU-6050 IMU on the back of the glove continuously sample:
- **Flex sensor ADC values** — measure finger bend angles (0–4095 raw ADC)
- **Gyroscope (X, Y, Z)** — captures wrist rotation and orientation
- **Accelerometer (X, Y, Z)** — captures hand tilt and movement

These readings are collected at a fixed sampling rate inside the ESP32 firmware (`src/main.cpp`).

### 2. Feature Extraction & Buffering (ESP32 Firmware)
The firmware aggregates multiple raw samples into a single gesture window:
- Applies simple averaging or windowing to reduce noise
- Composes a **feature vector**: `[flex1, flex2, flex3, flex4, flex5, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z]`
- Serializes the vector to **JSON** and writes it to LittleFS or streams it over Serial/BLE

### 3. Offline Training Pipeline (PC — Jupyter + Python)
During the data collection phase:
1. Raw gesture recordings are saved as JSON files → `JSON_DYNAMIC_DATA/`
2. Data is **augmented** (noise injection, scaling, rotation) → `JSON_AUGMENTED/`
3. Jupyter notebooks in `jupyter/` preprocess and label the data → `datasets/`
4. A **scikit-learn classifier** (e.g., Random Forest or SVM) is trained on the feature vectors
5. The trained model is serialized with **joblib** → `models(joblib)/`
6. The model (or its decision rules) is embedded into the ESP32 firmware as lookup tables or a lightweight inference engine

### 4. On-Device Inference (ESP32)
At runtime, the ESP32:
1. Reads the live feature vector from sensors
2. Runs the classification logic (ported from the trained model)
3. Produces a **predicted gesture label** (e.g., letter, word, or phrase in NSL)

### 5. Audio Output (ESP32 → Speaker)
Once a gesture is classified:
1. The predicted label maps to a pre-recorded `.wav` file stored in `sounds/`
2. The ESP32 reads the audio file from LittleFS
3. The audio is played through a DAC or I2S-connected speaker/amplifier

```
[Flex Sensors]──┐
                ├──► ESP32 ADC ──► Feature Vector ──► Classifier ──► Label ──► .wav ──► Speaker
[MPU-6050 IMU]──┘
```

---

## Setup & Build

### Prerequisites
- [PlatformIO](https://platformio.org/) (VS Code extension or CLI)
- Python 3.x with `scikit-learn`, `numpy`, `pandas`, `joblib`
- Jupyter Notebook

### Build Firmware
```bash
# Clone the repository
git clone https://github.com/Sanjog34/SignLanguage_Glove.git
cd SignLanguage_Glove

# Build and upload with PlatformIO
pio run --target upload

# Upload filesystem (sounds + model data)
pio run --target uploadfs
```

### Train the Model
```bash
cd jupyter/
jupyter notebook
# Open and run the training notebook
```

---

## ML Pipeline Summary

1. **Data Collection** — Perform each NSL sign repeatedly while the glove logs sensor readings to JSON
2. **Augmentation** — Synthetically expand the dataset to improve robustness
3. **Training** — Train a classifier in the Jupyter notebook; evaluate accuracy
4. **Deployment** — Serialize the model and integrate decision logic into firmware

---

## Contributors

This project was developed as a final year academic project focused on accessibility and assistive technology for the Nepali deaf community.

---

## 📄 License

This project is open-source. See the repository for details.
