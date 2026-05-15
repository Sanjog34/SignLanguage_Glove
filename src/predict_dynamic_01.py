"""
Gesture Inference — Serial Port Reader
=======================================
Reads raw sensor CSV from serial port, classifies dynamic/static frames
automatically using gyroscope data, segments gestures, and runs prediction
using either the trained LSTM model (dynamic) or Random Forest (static).

Requirements:
    pip install pyserial numpy scipy scikit-learn tensorflow joblib

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

# ── Static model ───────────────────────────────────────────────────────────────
STATIC_MODEL_PATH = "../models(joblib)/Gesture_Model.joblib"

try:
    static_model = joblib.load(STATIC_MODEL_PATH)
    print(f"   Static model loaded : {STATIC_MODEL_PATH}")
except Exception as e:
    sys.exit(f"Failed to load static model: {e}")

# ── CLI args ───────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Gesture Inference via Serial Port")
parser.add_argument("--port",          default="/dev/ttyUSB2", help="Serial port")
parser.add_argument("--baud",          default=115200, type=int, help="Baud rate")
parser.add_argument("--model",         default="../jupyter/gesture_model.h5",  help="Path to .h5 model")
parser.add_argument("--scaler",        default="../jupyter/scaler.pkl",         help="Path to scaler pickle")
parser.add_argument("--encoder",       default="../jupyter/label_encoder.pkl",  help="Path to label encoder pickle")
parser.add_argument("--target-length", default=50, type=int,                    help="Resample timesteps")
args = parser.parse_args()

# ── Classifier config ──────────────────────────────────────────────────────────
BUFFER_SIZE          = 20
GYRO_THRESHOLD       = 50
MAX_STATIC_TOLERANCE = 7
GX_IDX, GY_IDX, GZ_IDX = 11, 12, 13

FEATURE_COLS = [
    'idxUp', 'idxLow', 'midUp', 'midLow',
    'ringUp', 'ringLow', 'thumb', 'pinky',
    'ax', 'ay', 'az', 'gx', 'gy', 'gz'
]

# ── Load LSTM model + artifacts ────────────────────────────────────────────────
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


# ── Feature extraction ─────────────────────────────────────────────────────────
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


# ── LSTM Inference ─────────────────────────────────────────────────────────────
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
    """Parse a CSV line of exactly 14 numeric sensor values."""
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
    """
    Compare oldest vs newest frame in the gyro buffer.
    Returns 'dynamic' if any gyro axis delta exceeds GYRO_THRESHOLD,
    otherwise 'static'.
    """
    if len(buffer) < BUFFER_SIZE:
        return "static"
    oldest, newest = buffer[0], buffer[-1]
    if (abs(newest[GX_IDX] - oldest[GX_IDX]) > GYRO_THRESHOLD or
            abs(newest[GY_IDX] - oldest[GY_IDX]) > GYRO_THRESHOLD or
            abs(newest[GZ_IDX] - oldest[GZ_IDX]) > GYRO_THRESHOLD):
        return "dynamic"
    return "static"


# ── Pretty print ───────────────────────────────────────────────────────────────
def print_result(label: str, confidence: float, all_probs: list[tuple], n_frames: int) -> str:
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


# ── Static prediction helper ───────────────────────────────────────────────────
def run_static_prediction(row: list[float], static_playing: bool) -> bool:
    print(row, end="")
    row=row[:14]
    print("predict part:static_play "+str(static_playing), end = "")
    """
    
    Pass a single frame to the Random Forest static model and play result.

    Accepts the current playback state, forwards it to dictate.play_sound(),
    and returns the updated playback state so main() can track it correctly.
    No globals — state flows in and out explicitly.
    """
    try:
        X_static = pd.DataFrame([row[:14]], columns=FEATURE_COLS)
        pred     = static_model.predict(X_static)[0]
        print(f"  [STATIC] {pred}", end ="")
        return( dictate.play_sound(
           dictate.CONSONANT_DIR + "/" + str(pred) + ".mp3",
            static_playing))
    except Exception as e:
        print(f"  [STATIC ERROR] {e}")
        return static_playing   # preserve existing state on error


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
    static_playing     = 0     # ← single source of truth, owned by main()

    try:
        import serial as pyserial

        with pyserial.Serial(args.port, args.baud, timeout=1) as ser:
            while True:

                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                # print(raw)
                if raw.startswith("D,") or raw.startswith("S,"):
                    raw = raw[2:]
                # raw=raw[1:]
                if not raw.strip():
                    continue

                # ── Parse 14 raw sensor values (no status prefix) ──────────
                row = parse_row(raw)
                if row is None:
                    print(f"  [SKIP] malformed: {raw.strip()[:60]}")
                    continue

                # ── Always buffer for gyro-based classification ────────────
                gyro_buffer.append(row)

                if len(gyro_buffer) < BUFFER_SIZE:
                    print(f"  [BUFFERING] {len(gyro_buffer)}/{BUFFER_SIZE}", end="\r")
                    continue

                # ── Classify frame using gyroscope delta ───────────────────
                gesture_type = classify_frame(gyro_buffer)

                oldest, newest = gyro_buffer[0], gyro_buffer[-1]
                dgx = newest[GX_IDX] - oldest[GX_IDX]
                dgy = newest[GY_IDX] - oldest[GY_IDX]
                dgz = newest[GZ_IDX] - oldest[GZ_IDX]

                # ══════════════════════════════════════════════════════════
                # CASE 1 — NOT in a session
                # ══════════════════════════════════════════════════════════
                if not in_session:

                    if gesture_type == "static":
                        # No active gesture — pass directly to Random Forest
                        print(
                            f"  [STATIC  ]  "
                            f"ΔGx={dgx:+6.0f}  ΔGy={dgy:+6.0f}  ΔGzz={dgz:+6.0f}",
                            end=""
                        )
                        # Updated state returned and stored correctly here
                        static_playing=run_static_prediction(row, static_playing)

                    else:
                        # Dynamic motion detected — open a new LSTM session
                        # Reset playback state so static audio stops
                        static_playing     = 0
                        in_session         = True
                        frame_index        = 1
                        consecutive_static = 0
                        session_samples    = [row_to_sample(row, frame_index)]
                        print(
                            f"  [DYNAMIC ]  "
                            f"ΔGx={dgx:+6.0f}  ΔGy={dgy:+6.0f}  ΔGz={dgz:+6.0f}"
                            f"   ← session opened"
                        )

                # ══════════════════════════════════════════════════════════
                # CASE 2 — Inside an active session
                # ══════════════════════════════════════════════════════════
                else:

                    print(
                        f"  [{gesture_type.upper():7s}]  "
                        f"ΔGx={dgx:+6.0f}  ΔGy={dgy:+6.0f}  ΔGz={dgz:+6.0f}",
                        end=""
                    )

                    if gesture_type == "dynamic":
                        # Still moving — keep collecting frames
                        consecutive_static  = 0
                        frame_index        += 1
                        session_samples.append(row_to_sample(row, frame_index))
                        print()

                    else:
                        # Static frame inside session — count toward tolerance
                        consecutive_static += 1
                        frame_index        += 1
                        session_samples.append(row_to_sample(row, frame_index))
                        print(f"  (static {consecutive_static}/{MAX_STATIC_TOLERANCE})")

                        if consecutive_static > MAX_STATIC_TOLERANCE:
                            # ── Session ended — run LSTM inference ──────────
                            n = len(session_samples)
                            print(f"\n  session ended with {n} frames...")

                            if n < 30:
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

                            # ── Reset session state ──────────────────────────
                            in_session         = False
                            session_samples    = []
                            frame_index        = 0
                            consecutive_static = 0
                            print("  Waiting for next gesture...\n")

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