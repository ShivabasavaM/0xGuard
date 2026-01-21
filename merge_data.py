import pandas as pd
import glob
import os

# CONFIGURATION
# This script looks for ALL CSV files inside the 'data' folder
DATA_FOLDER = "data"
OUTPUT_FILE = "data/master_normal_traffic.csv"

def merge_datasets():
    print(f"🔍 Looking for CSV files in '{DATA_FOLDER}/'...")
    
    # Get list of all CSVs (e.g., data_me.csv, data_friend1.csv)
    # glob helps us find filenames matching a pattern
    all_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))
    
    # Filter out the master file if it already exists so we don't merge it into itself
    all_files = [f for f in all_files if "master_normal_traffic.csv" not in f]
    
    if not all_files:
        print("❌ No CSV files found! Make sure you put your friends' files in 'data/'.")
        return

    print(f"   Found {len(all_files)} files: {[os.path.basename(f) for f in all_files]}")

    df_list = []
    
    for filename in all_files:
        try:
            # Read each file
            df = pd.read_csv(filename)
            print(f"   Reading {filename} -> {len(df)} rows")
            df_list.append(df)
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}")

    if not df_list:
        print("❌ No valid data to merge.")
        return

    # Combine all into one massive table
    master_df = pd.concat(df_list, ignore_index=True)
    
    # Shuffle the data (Randomize rows so the model doesn't learn 'Friend 1' patterns then 'Friend 2' patterns)
    master_df = master_df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Save the Final Master Dataset
    master_df.to_csv(OUTPUT_FILE, index=False)
    
    print("-" * 30)
    print(f"✅ SUCCESS! Merged {len(all_files)} files.")
    print(f"📊 Total Training Data: {len(master_df)} flows")
    print(f"💾 Saved to: {OUTPUT_FILE}")
    print("-" * 30)

if __name__ == "__main__":
    merge_datasets()