# import json
# import copy
# import random

# # ─────────────────────────────────────────────────────────────
# # CONFIG
# # ─────────────────────────────────────────────────────────────

# INPUT_JSON = "../JSON_DYNAMIC_DATA/gesture_dataset_naam_20k.json"
# OUTPUT_JSON = "../JSON_AUGMENTED_20K/gestures_augmented_naam_20k.json"

# TARGET_TOTAL_SAMPLES = 1500

# FLEX_STD  = 2.0
# ACCEL_STD = 0.02
# GYRO_STD  = 0.5


# # ─────────────────────────────────────────────────────────────
# # AUGMENTATION
# # ─────────────────────────────────────────────────────────────

# def augment_sample(sample):

#     augmented = copy.deepcopy(sample)

#     for frame in augmented["samples"]:

#         # FLEX
#         for k in frame["flex"]:
#             frame["flex"][k] += random.gauss(0, FLEX_STD)

#         # ACCEL
#         for k in frame["accel"]:
#             frame["accel"][k] += random.gauss(0, ACCEL_STD)

#         # GYRO
#         for k in frame["gyro"]:
#             frame["gyro"][k] += random.gauss(0, GYRO_STD)

#     return augmented


# # ─────────────────────────────────────────────────────────────
# # LOAD DATA
# # ─────────────────────────────────────────────────────────────

# with open(INPUT_JSON, "r") as f:
#     original_data = json.load(f)

# combined_dataset = copy.deepcopy(original_data)

# original_count = len(original_data)

# print(f"Original samples: {original_count}")


# # ─────────────────────────────────────────────────────────────
# # GENERATE UNTIL TARGET REACHED
# # ─────────────────────────────────────────────────────────────

# while len(combined_dataset) < TARGET_TOTAL_SAMPLES:

#     # randomly pick one original sample
#     source_sample = random.choice(original_data)

#     augmented = augment_sample(source_sample)

#     combined_dataset.append(augmented)


# # ─────────────────────────────────────────────────────────────
# # SAVE
# # ─────────────────────────────────────────────────────────────

# with open(OUTPUT_JSON, "w") as f:
#     json.dump(combined_dataset, f, indent=2)

# print(f"Final dataset size: {len(combined_dataset)}")
# print(f"Saved to: {OUTPUT_JSON}")


import json
import copy
import random

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
LABEL= "ho"
INPUT_JSON = f"../JSON_AUGMENTED_20K/JSON_DYNAMIC_DATA/gesture_dataset_{LABEL}_20k.json"
OUTPUT_JSON = f"../JSON_AUGMENTED_20K/test_train/gestures_augmented_{LABEL}_20k_test.json"

TARGET_TOTAL_SAMPLES = 1500

# MAX NOISE LIMITS
FLEX_NOISE_MAX  = 20.0
ACCEL_NOISE_MAX = 0.3
GYRO_NOISE_MAX  = 10.0

# OPTIONAL SENSOR LIMITS
FLEX_MIN, FLEX_MAX = 0, 300
ACCEL_MIN, ACCEL_MAX = -4, 4
GYRO_MIN, GYRO_MAX = -500, 500


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def clamp(value, vmin, vmax):
    return max(vmin, min(value, vmax))


def add_noise(value, max_noise, vmin=None, vmax=None):

    # uniform random noise
    noisy = value + random.uniform(-max_noise, max_noise)

    # clamp if limits provided
    if vmin is not None and vmax is not None:
        noisy = clamp(noisy, vmin, vmax)

    # keep only 2 decimal places
    return round(noisy, 2)


# ─────────────────────────────────────────────────────────────
# AUGMENTATION
# ─────────────────────────────────────────────────────────────

def augment_sample(sample):

    augmented = copy.deepcopy(sample)

    for frame in augmented["samples"]:

        # FLEX
        for k in frame["flex"]:
            frame["flex"][k] = add_noise(
                frame["flex"][k],
                FLEX_NOISE_MAX,
                FLEX_MIN,
                FLEX_MAX
            )

        # ACCEL
        for k in frame["accel"]:
            frame["accel"][k] = add_noise(
                frame["accel"][k],
                ACCEL_NOISE_MAX,
                ACCEL_MIN,
                ACCEL_MAX
            )

        # GYRO
        for k in frame["gyro"]:
            frame["gyro"][k] = add_noise(
                frame["gyro"][k],
                GYRO_NOISE_MAX,
                GYRO_MIN,
                GYRO_MAX
            )

        # OPTIONAL: slightly vary timestamp
        frame["timestamp"] = int(
            frame["timestamp"] + random.uniform(-5, 5)
        )

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