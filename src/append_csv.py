import os
import pandas as pd

# === SETTINGS ===
FOLDER_PATH = "../datasets/20K"
OUTPUT_FILE = "../datasets/20K/merged_dataset_01.csv"

# get all csv files
csv_files = [f for f in os.listdir(FOLDER_PATH) if f.endswith(".csv")]

all_dfs = []

for i, file in enumerate(csv_files):
    path = os.path.join(FOLDER_PATH, file)

    if i == 0:
        # first file → keep header
        df = pd.read_csv(path)
    else:
        # other files → skip header automatically handled by pandas
        df = pd.read_csv(path, skiprows=1, header=None)
        df.columns = all_dfs[0].columns  # assign correct columns

    all_dfs.append(df)

# merge all
final_df = pd.concat(all_dfs, ignore_index=True)

# save
final_df.to_csv(OUTPUT_FILE, index=False)

print(f"Merged {len(csv_files)} files into {OUTPUT_FILE}")