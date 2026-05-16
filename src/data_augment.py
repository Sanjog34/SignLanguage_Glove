import json
import copy
import random

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────

INPUT_JSON = "../JSON_DYNAMIC_DATA/gesture_dataset_ho_20k.json"
OUTPUT_JSON = "../JSON_AUGMENTED_20K/gestures_augmented_ho_20k.json"

TARGET_TOTAL_SAMPLES = 1500

FLEX_STD  = 2.0
ACCEL_STD = 0.02
GYRO_STD  = 0.5


# ─────────────────────────────────────────────────────────────
# AUGMENTATION
# ─────────────────────────────────────────────────────────────

def augment_sample(sample):

    augmented = copy.deepcopy(sample)

    for frame in augmented["samples"]:

        # FLEX
        for k in frame["flex"]:
            frame["flex"][k] += random.gauss(0, FLEX_STD)

        # ACCEL
        for k in frame["accel"]:
            frame["accel"][k] += random.gauss(0, ACCEL_STD)

        # GYRO
        for k in frame["gyro"]:
            frame["gyro"][k] += random.gauss(0, GYRO_STD)

    return augmented


# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────

with open(INPUT_JSON, "r") as f:
    original_data = json.load(f)

combined_dataset = copy.deepcopy(original_data)

original_count = len(original_data)

print(f"Original samples: {original_count}")


# ─────────────────────────────────────────────────────────────
# GENERATE UNTIL TARGET REACHED
# ─────────────────────────────────────────────────────────────

while len(combined_dataset) < TARGET_TOTAL_SAMPLES:

    # randomly pick one original sample
    source_sample = random.choice(original_data)

    augmented = augment_sample(source_sample)

    combined_dataset.append(augmented)


# ─────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────

with open(OUTPUT_JSON, "w") as f:
    json.dump(combined_dataset, f, indent=2)

print(f"Final dataset size: {len(combined_dataset)}")
print(f"Saved to: {OUTPUT_JSON}")