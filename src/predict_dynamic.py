# """
# Gesture Inference — Serial Port Reader
# =======================================
# Reads raw sensor CSV from serial port, classifies dynamic/static frames,
# segments gestures, and runs prediction using the trained LSTM model.

# Requirements:
#     pip install pyserial numpy scipy scikit-learn tensorflow

# Usage:
#     python gesture_inference.py
#     python gesture_inference.py --port COM3 --baud 115200
#     python gesture_inference.py --port /dev/ttyUSB0 --model gesture_model.h5
# """

# import sys
# import json
# import pickle
# import argparse
# import numpy as np
# from collections import deque
# from scipy.interpolate import interp1d

# # ── CLI args ───────────────────────────────────────────────────────────────────
# parser = argparse.ArgumentParser(description="Gesture Inference via Serial Port")
# parser.add_argument("--port",    default="/dev/ttyUSB0", help="Serial port")
# parser.add_argument("--baud",    default=115200, type=int, help="Baud rate")
# parser.add_argument("--model",   default="gesture_model.h5", help="Path to .h5 model")
# parser.add_argument("--scaler",  default="scaler.pkl",        help="Path to scaler pickle")
# parser.add_argument("--encoder", default="label_encoder.pkl", help="Path to label encoder pickle")
# parser.add_argument("--target-length", default=50, type=int,  help="Resample timesteps")
# args = parser.parse_args()

# # ── Classifier config (mirrors recorder.py) ────────────────────────────────────
# BUFFER_SIZE          = 20
# GYRO_THRESHOLD       = 20
# MAX_STATIC_TOLERANCE = 7
# GX_IDX, GY_IDX, GZ_IDX = 11, 12, 13

# # ── Load model + artifacts ─────────────────────────────────────────────────────
# print("Loading model and artifacts...")

# try:
#     import serial
# except ImportError:
#     sys.exit("pyserial not installed. Run: pip install pyserial")

# try:
#     import tensorflow as tf
#     model = tf.keras.models.load_model(args.model)
#     print(f"  ✔ Model loaded       : {args.model}")
# except Exception as e:
#     sys.exit(f"Failed to load model: {e}")

# try:
#     with open(args.scaler, "rb") as f:
#         scaler = pickle.load(f)
#     print(f"   Scaler loaded      : {args.scaler}")
# except Exception as e:
#     sys.exit(f"Failed to load scaler: {e}")

# try:
#     with open(args.encoder, "rb") as f:
#         label_encoder = pickle.load(f)
#     print(f"   Label encoder loaded: {args.encoder}")
#     print(f"   Classes            : {list(label_encoder.classes_)}")
# except Exception as e:
#     sys.exit(f"Failed to load label encoder: {e}")


# # ── Feature extraction (mirrors training script) ───────────────────────────────
# def extract_features(samples: list[dict]) -> np.ndarray:
#     """Convert list of sample dicts → (T, 14) numpy array."""
#     rows = []
#     for s in samples:
#         rows.append([
#             s["flex"]["index_upper"],
#             s["flex"]["index_lower"],
#             s["flex"]["middle_upper"],
#             s["flex"]["middle_lower"],
#             s["flex"]["ring_upper"],
#             s["flex"]["ring_lower"],
#             s["flex"]["thumb"],
#             s["flex"]["pinky"],
#             s["accel"]["x"],
#             s["accel"]["y"],
#             s["accel"]["z"],
#             s["gyro"]["x"],
#             s["gyro"]["y"],
#             s["gyro"]["z"],
#         ])
#     return np.array(rows)


# def resample_sequence(seq: np.ndarray, target: int) -> np.ndarray:
#     """Resample (T, F) → (target, F) using linear interpolation."""
#     T, F = seq.shape
#     if T == target:
#         return seq
#     x_old = np.linspace(0, 1, T)
#     x_new = np.linspace(0, 1, target)
#     out = np.zeros((target, F))
#     for f in range(F):
#         out[:, f] = interp1d(x_old, seq[:, f], kind="linear")(x_new)
#     return out


# def preprocess(samples: list[dict]) -> np.ndarray:
#     """Extract → resample → scale → add batch dim → (1, target_length, 14)."""
#     features  = extract_features(samples)                         # (T, 14)
#     resampled = resample_sequence(features, args.target_length)   # (50, 14)
#     N, F      = resampled.shape
#     scaled    = scaler.transform(resampled.reshape(-1, F)).reshape(N, F)
#     return scaled[np.newaxis, ...]                                # (1, 50, 14)


# # ── Inference ──────────────────────────────────────────────────────────────────
# def predict(samples: list[dict]) -> tuple[str, float, list[tuple]]:
#     """
#     Returns:
#         label       : predicted gesture string
#         confidence  : float 0-1
#         all_probs   : [(label, prob), ...] sorted descending
#     """
#     X          = preprocess(samples)
#     probs      = model.predict(X, verbose=0)[0]           # (num_classes,)
#     best_idx   = int(np.argmax(probs))
#     label      = label_encoder.classes_[best_idx]
#     confidence = float(probs[best_idx])
#     all_probs  = sorted(
#         [(label_encoder.classes_[i], float(p)) for i, p in enumerate(probs)],
#         key=lambda x: x[1], reverse=True
#     )
#     return label, confidence, all_probs


# # ── CSV / frame helpers ────────────────────────────────────────────────────────
# def parse_row(line: str) -> list[float] | None:
#     try:
#         vals = [float(x) for x in line.strip().split(",")]
#         return vals if len(vals) >= 14 else None
#     except ValueError:
#         return None


# def row_to_sample(row: list[float], frame_index: int) -> dict:
#     return {
#         "timestamp": frame_index * 51,
#         "flex": {
#             "index_upper":  row[0], "index_lower":  row[1],
#             "middle_upper": row[2], "middle_lower": row[3],
#             "ring_upper":   row[4], "ring_lower":   row[5],
#             "thumb":        row[6], "pinky":        row[7],
#         },
#         "accel": {"x": row[8],  "y": row[9],  "z": row[10]},
#         "gyro":  {"x": row[11], "y": row[12], "z": row[13]},
#     }


# def classify_frame(buffer: deque) -> str:
#     if len(buffer) < BUFFER_SIZE:
#         return "static"
#     oldest, newest = buffer[0], buffer[-1]
#     if (abs(newest[GX_IDX] - oldest[GX_IDX]) > GYRO_THRESHOLD or
#             abs(newest[GY_IDX] - oldest[GY_IDX]) > GYRO_THRESHOLD or
#             abs(newest[GZ_IDX] - oldest[GZ_IDX]) > GYRO_THRESHOLD):
#         return "dynamic"
#     return "static"


# # ── Pretty print ───────────────────────────────────────────────────────────────
# def print_result(label: str, confidence: float, all_probs: list[tuple], n_frames: int):
#     bar_width = 30
#     print("\n" + "═" * 62)
#     print(f"  Gesture detected   : {label.upper()}")
#     print(f"  Confidence         : {confidence * 100:.1f}%  ({n_frames} frames)")
#     print("  ─" * 31)
#     for lbl, prob in all_probs[:5]:
#         filled = int(prob * bar_width)
#         bar = "█" * filled + "░" * (bar_width - filled)
#         marker = " ◄" if lbl == label else ""
#         print(f"  {lbl:<18} {bar}  {prob*100:5.1f}%{marker}")
#     print("═" * 62 + "\n")


# # ── Main loop ──────────────────────────────────────────────────────────────────
# def main():
#     print("\n" + "═" * 62)
#     print("  Gesture Inference  |  Ctrl-C to exit")
#     print(f"  Port       : {args.port}  @  {args.baud} baud")
#     print(f"  Model      : {args.model}")
#     print(f"  Classes    : {list(label_encoder.classes_)}")
#     print("═" * 62)
#     print("  Waiting for gesture...\n")

#     gyro_buffer        = deque(maxlen=BUFFER_SIZE)
#     session_samples    = []
#     frame_index        = 0
#     consecutive_static = 0
#     in_session         = False

#     try:
#         import serial as pyserial
#         with pyserial.Serial(args.port, args.baud, timeout=1) as ser:
#             while True:
#                 raw = ser.readline().decode("utf-8", errors="ignore")
#                 if not raw.strip():
#                     continue

#                 row = parse_row(raw)
#                 if row is None:
#                     print(f"  [SKIP] malformed: {raw.strip()[:60]}")
#                     continue

#                 gyro_buffer.append(row)

#                 if len(gyro_buffer) < BUFFER_SIZE:
#                     print(f"  [BUFFERING] {len(gyro_buffer)}/{BUFFER_SIZE}", end="\r")
#                     continue

#                 gesture_type = classify_frame(gyro_buffer)

#                 oldest, newest = gyro_buffer[0], gyro_buffer[-1]
#                 dgx = newest[GX_IDX] - oldest[GX_IDX]
#                 dgy = newest[GY_IDX] - oldest[GY_IDX]
#                 dgz = newest[GZ_IDX] - oldest[GZ_IDX]

#                 print(f"  [{gesture_type.upper():7s}]  "
#                       f"ΔGx={dgx:+6.0f}  ΔGy={dgy:+6.0f}  ΔGz={dgz:+6.0f}",
#                       end="")

#                 # ── State machine ───────────────────────────────────────────
#                 if not in_session:
#                     if gesture_type == "dynamic":
#                         in_session         = True
#                         frame_index        = 1
#                         consecutive_static = 0
#                         session_samples    = [row_to_sample(row, frame_index)]
#                         print("  ← session opened", end="")
#                     print()

#                 else:
#                     if gesture_type == "dynamic":
#                         consecutive_static = 0
#                         frame_index       += 1
#                         session_samples.append(row_to_sample(row, frame_index))
#                         print()

#                     else:
#                         consecutive_static += 1
#                         frame_index        += 1
#                         session_samples.append(row_to_sample(row, frame_index))
#                         print(f"  (static {consecutive_static}/{MAX_STATIC_TOLERANCE})")

#                         if consecutive_static > MAX_STATIC_TOLERANCE:
#                             # ── Run inference ──────────────────────────────
#                             n = len(session_samples)
#                             print(f"\n  Running inference on {n} frames...")
#                             try:
#                                 label, conf, all_probs = predict(session_samples)
#                                 print_result(label, conf, all_probs, n)
#                             except Exception as e:
#                                 print(f"\n  [ERROR] Inference failed: {e}\n")

#                             # reset
#                             in_session         = False
#                             session_samples    = []
#                             frame_index        = 0
#                             consecutive_static = 0
#                             print("  Waiting for next gesture...\n")

#     except KeyboardInterrupt:
#         print("\n\n  Interrupt received.")
#         if in_session and len(session_samples) >= 5:
#             print(f"  Running inference on open session ({len(session_samples)} frames)...")
#             try:
#                 label, conf, all_probs = predict(session_samples)
#                 print_result(label, conf, all_probs, len(session_samples))
#             except Exception as e:
#                 print(f"  [ERROR] {e}")
#         print("  Goodbye.\n")
#         sys.exit(0)


# if __name__ == "__main__":
#     main()

"""
Gesture Inference — Serial Port Reader
=======================================
Reads raw sensor CSV from serial port, classifies dynamic/static frames,
segments gestures, and runs prediction using the trained LSTM model.

Requirements:
    pip install pyserial numpy scipy scikit-learn tensorflow

Usage:
    python gesture_inference.py
    python gesture_inference.py --port COM3 --baud 115200
    python gesture_inference.py --port /dev/ttyUSB0 --model gesture_model.h5
"""

import sys
import pickle
import argparse
import numpy as np
import pandas as pd
from collections import deque
from scipy.interpolate import interp1d
import dictate_dynamic
import dictate
import joblib

STATIC_MODEL_PATH = "../models(joblib)/Gesture_Model_20K.joblib"

try:
    static_model = joblib.load(STATIC_MODEL_PATH)
    print(f"   Static model loaded : {STATIC_MODEL_PATH}")
except Exception as e:
    sys.exit(f"Failed to load static model: {e}")

# ── CLI args ───────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Gesture Inference via Serial Port")
parser.add_argument("--port",          default="/dev/ttyUSB1", help="Serial port")
parser.add_argument("--baud",          default=115200, type=int, help="Baud rate")
parser.add_argument("--model",         default="../jupyter/gesture_model.h5", help="Path to .h5 model")
parser.add_argument("--scaler",        default="../jupyter/scaler.pkl",        help="Path to scaler pickle")
parser.add_argument("--encoder",       default="../jupyter/label_encoder.pkl", help="Path to label encoder pickle")
parser.add_argument("--target-length", default=50, type=int,        help="Resample timesteps")
args = parser.parse_args()

# ── Classifier config (mirrors recorder.py) ────────────────────────────────────
BUFFER_SIZE          = 20
GYRO_THRESHOLD       = 20
MAX_STATIC_TOLERANCE = 7
GX_IDX, GY_IDX, GZ_IDX = 11, 12, 13

# ── Load model + artifacts ─────────────────────────────────────────────────────
print("Loading model and artifacts...")

try:
    import serial
except ImportError:
    sys.exit("pyserial not installed. Run: pip install pyserial")

try:
    import tensorflow as tf
    model = tf.keras.models.load_model(args.model)
    print(f"   Model loaded        : {args.model}")
except Exception as e:
    sys.exit(f"Failed to load model: {e}")

try:
    with open(args.scaler, "rb") as f:
        scaler = pickle.load(f)
    print(f"   Scaler loaded       : {args.scaler}")
except Exception as e:
    sys.exit(f"Failed to load scaler: {e}")

try:
    with open(args.encoder, "rb") as f:
        label_encoder = pickle.load(f)
    print(f"   Label encoder loaded: {args.encoder}")
    print(f"   Classes             : {list(label_encoder.classes_)}")
except Exception as e:
    sys.exit(f"Failed to load label encoder: {e}")
    
    
def extract_static_features(row: list[float]) -> np.ndarray:
    return np.array(row).reshape(1, -1)

# ── Feature extraction (mirrors training script) ───────────────────────────────
def extract_features(samples: list[dict]) -> np.ndarray:
    """
    Convert list of sample dicts → (T, 15) numpy array.

    15 features: 8 flex + 3 accel + 3 gyro + 1 normalized timestamp.
    Timestamp is normalized to [0.0, 1.0] across the session so the model
    sees timing shape, not raw millisecond values — identical to training.
    """
    timestamps = [s["timestamp"] for s in samples]
    t_min   = min(timestamps)
    t_max   = max(timestamps)
    t_range = t_max - t_min

    rows = []
    for i, (s, t) in enumerate(zip(samples, timestamps)):
        t_norm = (
            (t - t_min) / t_range
            if t_range > 0
            else i / max(len(samples) - 1, 1)
        )
        rows.append([
            s["flex"]["index_upper"],
            s["flex"]["index_lower"],
            s["flex"]["middle_upper"],
            s["flex"]["middle_lower"],
            s["flex"]["ring_upper"],
            s["flex"]["ring_lower"],
            s["flex"]["thumb"],
            s["flex"]["pinky"],
            s["accel"]["x"],
            s["accel"]["y"],
            s["accel"]["z"],
            s["gyro"]["x"],
            s["gyro"]["y"],
            s["gyro"]["z"],
            t_norm,           # ← 15th feature: normalized timestamp
        ])
    return np.array(rows)   # (T, 15)


def resample_sequence(seq: np.ndarray, target: int) -> np.ndarray:
    """Resample (T, F) → (target, F) using linear interpolation."""
    T, F = seq.shape
    if T == target:
        return seq
    x_old = np.linspace(0, 1, T)
    x_new = np.linspace(0, 1, target)
    out = np.zeros((target, F))
    for f in range(F):
        out[:, f] = interp1d(x_old, seq[:, f], kind="linear")(x_new)
    return out


def preprocess(samples: list[dict]) -> np.ndarray:
    """Extract → resample → scale → add batch dim → (1, target_length, 15)."""
    features  = extract_features(samples)                        # (T, 15)
    resampled = resample_sequence(features, args.target_length)  # (50, 15)
    N, F      = resampled.shape
    scaled    = scaler.transform(resampled.reshape(-1, F)).reshape(N, F)
    return scaled[np.newaxis, ...]                               # (1, 50, 15)


# ── Inference ──────────────────────────────────────────────────────────────────
def predict(samples: list[dict]) -> tuple[str, float, list[tuple]]:
    """
    Returns:
        label      : predicted gesture string
        confidence : float 0-1
        all_probs  : [(label, prob), ...] sorted descending
    """
    X          = preprocess(samples)
    probs      = model.predict(X, verbose=0)[0]
    best_idx   = int(np.argmax(probs))
    label      = label_encoder.classes_[best_idx]
    confidence = float(probs[best_idx])
    all_probs  = sorted(
        [(label_encoder.classes_[i], float(p)) for i, p in enumerate(probs)],
        key=lambda x: x[1], reverse=True
    )
    return label, confidence, all_probs


# ── CSV / frame helpers ────────────────────────────────────────────────────────
def parse_row(line: str) -> list[float] | None:
    try:
        vals = [float(x) for x in line.strip().split(",")]
        return vals if len(vals) >= 14 else None
    except ValueError:
        return None


def row_to_sample(row: list[float], frame_index: int) -> dict:
    """
    Convert a raw CSV row to a sample dict.
    Timestamp = frame_index * 51 to match the recorder's simulated cadence.
    Normalization to [0, 1] happens later in extract_features() across
    the full completed session, exactly as it does during training.
    """
    return {
        "timestamp": frame_index * 51,
        "flex": {
            "index_upper":  row[0], "index_lower":  row[1],
            "middle_upper": row[2], "middle_lower": row[3],
            "ring_upper":   row[4], "ring_lower":   row[5],
            "thumb":        row[6], "pinky":        row[7],
        },
        "accel": {"x": row[8],  "y": row[9],  "z": row[10]},
        "gyro":  {"x": row[11], "y": row[12], "z": row[13]},
    }


def classify_frame(buffer: deque) -> str:
    if len(buffer) < BUFFER_SIZE:
        return "static"
    oldest, newest = buffer[0], buffer[-1]
    if (abs(newest[GX_IDX] - oldest[GX_IDX]) > GYRO_THRESHOLD or
            abs(newest[GY_IDX] - oldest[GY_IDX]) > GYRO_THRESHOLD or
            abs(newest[GZ_IDX] - oldest[GZ_IDX]) > GYRO_THRESHOLD):
        return "dynamic"
    return "static"


# ── Pretty print ───────────────────────────────────────────────────────────────
def print_result(label: str, confidence: float, all_probs: list[tuple], n_frames: int):
    bar_width = 30
    print("\n" + "═" * 62)
    print(f"  Gesture detected   : {label.upper()}")
    print(f"  Confidence         : {confidence * 100:.1f}%  ({n_frames} frames)")
    print("  ─" * 31)
    for lbl, prob in all_probs[:5]:
        filled = int(prob * bar_width)
        bar    = "█" * filled + "░" * (bar_width - filled)
        marker = " ◄" if lbl == label else ""
        print(f"  {lbl:<18} {bar}  {prob*100:5.1f}%{marker}")
    print("═" * 62 + "\n")
    return label


# ── Main loop ──────────────────────────────────────────────────────────────────
def main():
    print("\n" + "═" * 62)
    print("  Gesture Inference  |  Ctrl-C to exit")
    print(f"  Port       : {args.port}  @  {args.baud} baud")
    print(f"  Model      : {args.model}")
    print(f"  Classes    : {list(label_encoder.classes_)}")
    print("═" * 62)
    print("  Waiting for gesture...\n")

    gyro_buffer        = deque(maxlen=BUFFER_SIZE)
    session_samples    = []
    frame_index        = 0
    consecutive_static = 0
    in_session         = False

    FEATURE_COLS = [
        'idxUp','idxLow','midUp','midLow',
        'ringUp','ringLow','thumb','pinky',
        'ax','ay','az','gx','gy','gz'
    ]

    try:
        import serial as pyserial

        with pyserial.Serial(args.port, args.baud, timeout=1) as ser:
            while True:

                raw = ser.readline().decode("utf-8", errors="ignore")
                if not raw.strip():
                    continue

                parts = raw.strip().split(",")

                if len(parts) < 15:
                    print(f"  [SKIP] malformed: {raw.strip()[:60]}")
                    continue

                status = parts[0].strip()

                try:
                    row = [float(x) for x in parts[1:15]]
                except ValueError:
                    print(f"  [SKIP] bad numeric data")
                    continue

                # ─────────────────────────────────────────────
                # STATIC PIPELINE (S)
                # ─────────────────────────────────────────────
                if status == "S":
                    try:
                        X_static = pd.DataFrame([row], columns=FEATURE_COLS)

                        pred = static_model.predict(X_static)[0]

                        print(f"  [STATIC] {pred}")

                        dictate.play_sound(
                            dictate.CONSONANT_DIR + "/" + str(pred) + ".mp3"
                        )

                    except Exception as e:
                        print(f"  [STATIC ERROR] {e}")

                    continue

                # ─────────────────────────────────────────────
                # DYNAMIC PIPELINE (D)
                # ─────────────────────────────────────────────
                if status == "D":

                    gyro_buffer.append(row)

                    if len(gyro_buffer) < BUFFER_SIZE:
                        print(f"  [BUFFERING] {len(gyro_buffer)}/{BUFFER_SIZE}", end="\r")
                        continue

                    gesture_type = classify_frame(gyro_buffer)

                    oldest, newest = gyro_buffer[0], gyro_buffer[-1]
                    dgx = newest[GX_IDX] - oldest[GX_IDX]
                    dgy = newest[GY_IDX] - oldest[GY_IDX]
                    dgz = newest[GZ_IDX] - oldest[GZ_IDX]

                    print(
                        f"  [{gesture_type.upper():7s}]  "
                        f"ΔGx={dgx:+6.0f}  ΔGy={dgy:+6.0f}  ΔGz={dgz:+6.0f}",
                        end=""
                    )

                    # ── STATE MACHINE ──
                    if not in_session:
                        if gesture_type == "dynamic":
                            in_session = True
                            frame_index = 1
                            consecutive_static = 0
                            session_samples = [row_to_sample(row, frame_index)]
                            print("   session opened", end="")
                        print()

                    else:
                        if gesture_type == "dynamic":
                            consecutive_static = 0
                            frame_index += 1
                            session_samples.append(row_to_sample(row, frame_index))
                            print()

                        else:
                            consecutive_static += 1
                            frame_index += 1
                            session_samples.append(row_to_sample(row, frame_index))

                            print(
                                f"  (static {consecutive_static}/{MAX_STATIC_TOLERANCE})"
                            )

                            if consecutive_static > MAX_STATIC_TOLERANCE:
                                n = len(session_samples)

                                print(f"\n  session ended with {n} frames...")

                                if n < 20:
                                    print("  [DROP] Session discarded (< 20 frames)\n")

                                else:
                                    print("  Running inference...")

                                    try:
                                        label, conf, all_probs = predict(session_samples)

                                        top_label = print_result(label, conf, all_probs, n)

                                        dictate_dynamic.play_sound(
                                            dictate_dynamic.WORD_DIR + "/" + top_label + ".mp3"
                                        )

                                    except Exception as e:
                                        print(f"\n  [ERROR] Inference failed: {e}\n")

                                in_session = False
                                session_samples = []
                                frame_index = 0
                                consecutive_static = 0

                                print("  Waiting for next gesture...\n")

                    continue

                # ─────────────────────────────────────────────
                # UNKNOWN STATUS
                # ─────────────────────────────────────────────
                print(f"  [UNKNOWN STATUS] {status}")
                continue

    except KeyboardInterrupt:
        print("\n\n  Interrupt received.")

        if in_session and len(session_samples) >= 5:
            print(f"  Running inference on open session ({len(session_samples)} frames)...")

            try:
                label, conf, all_probs = predict(session_samples)
                print_result(label, conf, all_probs, len(session_samples))

            except Exception as e:
                print(f"  [ERROR] {e}")

        print("  Goodbye.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()