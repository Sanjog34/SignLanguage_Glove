# """
# Gesture Recorder  —  Classifier + JSON Logger
# ==============================================
# Reads raw sensor CSV lines from a serial port, classifies each frame as
# DYNAMIC or STATIC using a sliding gyro-delta buffer, then records all
# dynamic sessions to timestamped JSON files.

# Rules
# -----
# - A session opens the moment the first DYNAMIC frame is detected.
# - Up to MAX_STATIC_TOLERANCE consecutive STATIC frames are tolerated inside
#   a session (they are included in the JSON).
# - When consecutive STATIC frames exceed MAX_STATIC_TOLERANCE the session
#   closes, is saved to disk, and the recorder waits for the next DYNAMIC frame.
# - Ctrl-C saves any open session and exits cleanly.

# CSV row format (14 sensor columns, 0-based):
#   idxUp(0), idxLow(1), midUp(2), midLow(3), ringUp(4), ringLow(5),
#   thumb(6),  pinky(7), ax(8),  ay(9),  az(10), gx(11), gy(12), gz(13)

# Output JSON schema (matches your training data format):
#   {
#     "gesture_label": "dynamic",
#     "sample_count": 33,
#     "samples": [
#       {
#         "timestamp": 1,          ← integer, starts at 1 for first frame
#         "flex": { "index_upper": …, "index_lower": …, "middle_upper": …,
#                   "middle_lower": …, "ring_upper": …, "ring_lower": …,
#                   "thumb": …, "pinky": … },
#         "accel": { "x": …, "y": …, "z": … },
#         "gyro":  { "x": …, "y": …, "z": … }
#       }, …
#     ]
#   }
# """

import sys
import json
import os
import datetime
import serial
from collections import deque

# # ── Serial config ─────────────────────────────────────────────────────────────
# PORT      = '/dev/ttyUSB0'
# BAUD_RATE = 115200

# # ── Classifier config ─────────────────────────────────────────────────────────
# BUFFER_SIZE    = 20   # sliding window for gyro-delta classification
# GYRO_THRESHOLD = 20   # |delta| > this on any gyro axis → DYNAMIC

# GX_IDX = 11           # 0-based column indices of gx, gy, gz
# GY_IDX = 12
# GZ_IDX = 13

# # ── Recorder config ───────────────────────────────────────────────────────────
# MAX_STATIC_TOLERANCE = 7       # max consecutive STATIC frames allowed mid-session
# OUTPUT_DIR           = "gesture_sessions"


# # ══ Classifier ════════════════════════════════════════════════════════════════

# def parse_row(line: str):
#     """Return list of floats, or None if the line is malformed / too short."""
#     try:
#         values = [float(x) for x in line.strip().split(',')]
#         return values if len(values) >= 14 else None
#     except ValueError:
#         return None


# def classify(buffer: deque) -> str:
#     """'dynamic' if any gyro axis changed beyond threshold, else 'static'."""
#     if len(buffer) < BUFFER_SIZE:
#         return 'static'
#     oldest, newest = buffer[0], buffer[-1]
#     if (abs(newest[GX_IDX] - oldest[GX_IDX]) > GYRO_THRESHOLD or
#             abs(newest[GY_IDX] - oldest[GY_IDX]) > GYRO_THRESHOLD or
#             abs(newest[GZ_IDX] - oldest[GZ_IDX]) > GYRO_THRESHOLD):
#         return 'dynamic'
#     return 'static'


# # ══ Recorder ══════════════════════════════════════════════════════════════════

# def new_session() -> dict:
#     now = datetime.datetime.now()
#     return {
#         # internal fields (stripped before save)
#         "_filename":    "gesture_day.json",
#         "_frame_index": 0,
#         "_dyn_count":   0,
#         # output fields
#         "gesture_label": "day",
#         "sample_count":  0,
#         "samples":       [],
#     }


# def add_frame(session: dict, gesture_type: str, row: list):
#     session["_frame_index"] += 1
#     if gesture_type == "dynamic":
#         session["_dyn_count"] += 1

#     sample = {
#         "timestamp": session["_frame_index"],   # 1, 2, 3 … resets each session
#         "flex": {
#             "index_upper":  row[0],
#             "index_lower":  row[1],
#             "middle_upper": row[2],
#             "middle_lower": row[3],
#             "ring_upper":   row[4],
#             "ring_lower":   row[5],
#             "thumb":        row[6],
#             "pinky":        row[7],
#         },
#         "accel": {"x": row[8],  "y": row[9],  "z": row[10]},
#         "gyro":  {"x": row[11], "y": row[12], "z": row[13]},
#     }
#     session["samples"].append(sample)
#     session["sample_count"] = session["_frame_index"]


# def save_session(session: dict):
#     os.makedirs(OUTPUT_DIR, exist_ok=True)
#     filename   = session.pop("_filename")
#     dyn_count  = session.pop("_dyn_count")
#     session.pop("_frame_index")

#     path = os.path.join(OUTPUT_DIR, filename)
#     with open(path, "w") as f:
#         json.dump(session, f, indent=2)
#     print(f"\n  ✔  Saved → {path}  "
#           f"({dyn_count} dynamic / {session['sample_count']} total samples)\n")


# # ══ Main ══════════════════════════════════════════════════════════════════════

# def main():
#     print("═" * 62)
#     print("  Gesture Recorder   |   Ctrl-C to exit")
#     print(f"  Port         : {PORT}  @  {BAUD_RATE} baud")
#     print(f"  Buffer size  : {BUFFER_SIZE}  |  Gyro threshold : ±{GYRO_THRESHOLD}")
#     print(f"  Static tol.  : {MAX_STATIC_TOLERANCE} consecutive frames")
#     print(f"  Output dir   : {os.path.abspath(OUTPUT_DIR)}")
#     print("═" * 62)
#     print("  Waiting for first DYNAMIC gesture …\n")

#     gyro_buffer        = deque(maxlen=BUFFER_SIZE)
#     session            = None
#     consecutive_static = 0

#     try:
#         with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
#             while True:
#                 raw_line = ser.readline().decode('utf-8', errors='ignore')
#                 if not raw_line.strip():
#                     continue

#                 row = parse_row(raw_line)
#                 if row is None:
#                     print(f"  [SKIP] malformed: {raw_line.strip()}")
#                     continue

#                 # ── 1. Update classifier buffer ──────────────────────────────
#                 gyro_buffer.append(row)

#                 if len(gyro_buffer) < BUFFER_SIZE:
#                     print(f"  [BUFFERING] {len(gyro_buffer)}/{BUFFER_SIZE}", end="\r")
#                     continue

#                 # ── 2. Classify current frame ────────────────────────────────
#                 gesture_type = classify(gyro_buffer)

#                 oldest, newest = gyro_buffer[0], gyro_buffer[-1]
#                 dgx = newest[GX_IDX] - oldest[GX_IDX]
#                 dgy = newest[GY_IDX] - oldest[GY_IDX]
#                 dgz = newest[GZ_IDX] - oldest[GZ_IDX]
#                 print(f"  [{gesture_type.upper():7s}]  "
#                       f"ΔGx={dgx:+6.0f}  ΔGy={dgy:+6.0f}  ΔGz={dgz:+6.0f}",
#                       end="")

#                 # ── 3. Recorder state machine ────────────────────────────────
#                 if session is None:
#                     # IDLE — waiting for first dynamic frame
#                     if gesture_type == "dynamic":
#                         session = new_session()
#                         consecutive_static = 0
#                         add_frame(session, gesture_type, row)
#                         print(f"  ← session opened [{session['_filename']}]", end="")
#                     print()

#                 else:
#                     # RECORDING
#                     if gesture_type == "dynamic":
#                         consecutive_static = 0
#                         add_frame(session, gesture_type, row)
#                         print()

#                     else:  # static frame inside an active session
#                         consecutive_static += 1
#                         add_frame(session, gesture_type, row)
#                         print(f"  (static {consecutive_static}/{MAX_STATIC_TOLERANCE})")

#                         if consecutive_static > MAX_STATIC_TOLERANCE:
#                             save_session(session)
#                             session            = None
#                             consecutive_static = 0
#                             print("  Waiting for next DYNAMIC gesture …\n")

#     except KeyboardInterrupt:
#         print("\n\n  Interrupt received.")
#         if session and session.get("_dyn_count", 0) > 0:
#             print("  Saving open session …")
#             save_session(session)
#         else:
#             print("  No active session to save.")
#         print("  Goodbye.\n")
#         sys.exit(0)


# if __name__ == "__main__":
#     main()


"""
Gesture Recorder  —  Classifier + JSON Dataset Logger
=====================================================

Reads raw sensor CSV lines from a serial port, classifies each frame as
DYNAMIC or STATIC using a sliding gyro-delta buffer, then records all
dynamic sessions into a SINGLE JSON dataset file.

Dataset format:
[
  {
    "gesture_label": "today",
    "sample_count": 21,
    "samples": [...]
  },
  {
    "gesture_label": "hello",
    "sample_count": 18,
    "samples": [...]
  }
]

Rules
-----
- A session opens when first DYNAMIC frame is detected
- STATIC frames are tolerated inside active session
- Session closes after too many consecutive STATIC frames
- Closed session is appended into dataset JSON file
- Ctrl-C safely saves open session before exit
"""

import sys
import json
import os
import serial
from collections import deque

# ── Serial config ─────────────────────────────────────────────────────────────
PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

# ── Classifier config ─────────────────────────────────────────────────────────
BUFFER_SIZE = 20
GYRO_THRESHOLD = 20

GX_IDX = 11
GY_IDX = 12
GZ_IDX = 13

# ── Recorder config ───────────────────────────────────────────────────────────
MAX_STATIC_TOLERANCE = 15
OUTPUT_FILE = "../JSON_DYNAMIC_DATA/gesture_dataset_naam_20k.json"

# gesture label
GESTURE_LABEL = "naam"


# ══ Classifier ════════════════════════════════════════════════════════════════

def parse_row(line: str):
    """Convert CSV line to float list."""

    try:
        values = [float(x) for x in line.strip().split(',')]
        return values if len(values) >= 14 else None

    except ValueError:
        return None


def classify(buffer: deque) -> str:

    if len(buffer) < BUFFER_SIZE:
        return 'static'

    oldest = buffer[0]
    newest = buffer[-1]

    if (
        abs(newest[GX_IDX] - oldest[GX_IDX]) > GYRO_THRESHOLD+30 or
        abs(newest[GY_IDX] - oldest[GY_IDX]) > GYRO_THRESHOLD+30 or
        abs(newest[GZ_IDX] - oldest[GZ_IDX]) > GYRO_THRESHOLD
    ):
        return 'dynamic'

    return 'static'


# ══ Recorder ══════════════════════════════════════════════════════════════════

def new_session() -> dict:
    """
    Create new gesture session.
    """

    return {
        "_frame_index": 0,
        "_dyn_count": 0,

        "gesture_label": GESTURE_LABEL,
        "sample_count": 0,
        "samples": []
    }


def add_frame(session: dict, gesture_type: str, row: list):
    """
    Add one frame into current session.
    """

    session["_frame_index"] += 1

    if gesture_type == "dynamic":
        session["_dyn_count"] += 1

    sample = {
        # simulated timestamp
        "timestamp": session["_frame_index"] * 51,

        "flex": {
            "index_upper": row[0],
            "index_lower": row[1],
            "middle_upper": row[2],
            "middle_lower": row[3],
            "ring_upper": row[4],
            "ring_lower": row[5],
            "thumb": row[6],
            "pinky": row[7]
        },

        "accel": {
            "x": row[8],
            "y": row[9],
            "z": row[10]
        },

        "gyro": {
            "x": row[11],
            "y": row[12],
            "z": row[13]
        }
    }

    session["samples"].append(sample)
    session["sample_count"] = len(session["samples"])


def save_session(session: dict):
    """
    Append session into dataset JSON file.
    """

    # remove internal fields
    session.pop("_frame_index", None)
    dyn_count = session.pop("_dyn_count", 0)

    # load existing dataset
    if os.path.exists(OUTPUT_FILE):

        try:
            with open(OUTPUT_FILE, "r") as f:
                dataset = json.load(f)

            if not isinstance(dataset, list):
                dataset = []

        except Exception:
            dataset = []

    else:
        dataset = []

    # append new gesture session
    dataset.append(session)

    # save back
    with open(OUTPUT_FILE, "w") as f:
        json.dump(dataset, f, indent=2)

    print(
        f"\nSaved gesture to {OUTPUT_FILE} "
        f"({dyn_count} dynamic / {session['sample_count']} total samples)\n"
    )


# ══ Main ══════════════════════════════════════════════════════════════════════

def main():

    print("═" * 70)
    print(" Gesture Recorder  |  Ctrl-C to exit")
    print(f" Port              : {PORT}")
    print(f" Baud              : {BAUD_RATE}")
    print(f" Buffer Size       : {BUFFER_SIZE}")
    print(f" Gyro Threshold    : ±{GYRO_THRESHOLD}")
    print(f" Static Tolerance  : {MAX_STATIC_TOLERANCE}")
    print(f" Output File       : {os.path.abspath(OUTPUT_FILE)}")
    print(f" Gesture Label     : {GESTURE_LABEL}")
    print("═" * 70)
    print("Waiting for gesture...\n")

    gyro_buffer = deque(maxlen=BUFFER_SIZE)

    session = None
    consecutive_static = 0

    try:

        with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:

            while True:

                raw_line = ser.readline().decode(
                    'utf-8',
                    errors='ignore'
                )

                if not raw_line.strip():
                    continue

                row = parse_row(raw_line)

                if row is None:
                    print(f"[SKIP] malformed: {raw_line.strip()}")
                    continue

                # ── Update buffer ────────────────────────────────────────────
                gyro_buffer.append(row)

                if len(gyro_buffer) < BUFFER_SIZE:
                    print(
                        f"[BUFFERING] "
                        f"{len(gyro_buffer)}/{BUFFER_SIZE}",
                        end="\r"
                    )
                    continue

                # ── Classify ────────────────────────────────────────────────
                gesture_type = classify(gyro_buffer)

                oldest = gyro_buffer[0]
                newest = gyro_buffer[-1]

                dgx = newest[GX_IDX] - oldest[GX_IDX]
                dgy = newest[GY_IDX] - oldest[GY_IDX]
                dgz = newest[GZ_IDX] - oldest[GZ_IDX]

                print(
                    f"[{gesture_type.upper():7s}] "
                    f"ΔGx={dgx:+6.0f} "
                    f"ΔGy={dgy:+6.0f} "
                    f"ΔGz={dgz:+6.0f}",
                    end=""
                )

                # ── State Machine ───────────────────────────────────────────
                if session is None:

                    # waiting for dynamic gesture
                    if gesture_type == "dynamic":

                        session = new_session()
                        consecutive_static = 0

                        add_frame(session, gesture_type, row)

                        print("   session opened", end="")

                    print()

                else:

                    # active recording
                    if gesture_type == "dynamic":

                        consecutive_static = 0

                        add_frame(session, gesture_type, row)

                        print()

                    else:

                        consecutive_static += 1

                        add_frame(session, gesture_type, row)

                        print(
                            f"  (static "
                            f"{consecutive_static}/"
                            f"{MAX_STATIC_TOLERANCE})"
                        )

                        # close session
                        if consecutive_static > MAX_STATIC_TOLERANCE:

                            save_session(session)

                            session = None
                            consecutive_static = 0

                            print("Waiting for next gesture...\n")

    except KeyboardInterrupt:

        print("\n\nInterrupt received.")

        if session and session.get("_dyn_count", 0) > 0:

            print("Saving open session...")
            save_session(session)

        else:
            print("No active session.")
        sys.exit(0)


if __name__ == "__main__":
    main()