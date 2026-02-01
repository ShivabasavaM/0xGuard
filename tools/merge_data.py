import pandas as pd
import os

# CONFIGURATION
DATA_DIR = "data"
OUTPUT_FILE = "data/master_merged.csv"

# FILES TO MERGE
FILE_SHIVA = "data/normal_shiva.csv"
FILE_FRIEND = "data/normal_friend.csv"
FILE_ATTACK = "data/attack_traffic.csv"

def merge_datasets():
    print("🔄 STARTING FEDERATED DATA MERGE...")
    dfs = []

    # 1. Load Shiva's Normal Data (Label = 1)
    if os.path.exists(FILE_SHIVA):
        df_shiva = pd.read_csv(FILE_SHIVA)
        df_shiva['Label'] = 1  # 1 = Normal
        dfs.append(df_shiva)
        print(f"   ✅ Loaded Shiva's Data: {len(df_shiva)} rows")
    else:
        print(f"   ⚠️ Warning: {FILE_SHIVA} not found (Skipping)")

    # 2. Load Friend's Normal Data (Label = 1)
    if os.path.exists(FILE_FRIEND):
        df_friend = pd.read_csv(FILE_FRIEND)
        df_friend['Label'] = 1  # 1 = Normal
        dfs.append(df_friend)
        print(f"   ✅ Loaded Friend's Data: {len(df_friend)} rows")
    else:
        print(f"   ⚠️ Warning: {FILE_FRIEND} not found (Skipping)")

    # 3. Load Synthetic Attack Data (Label = -1)
    if os.path.exists(FILE_ATTACK):
        df_attack = pd.read_csv(FILE_ATTACK)
        df_attack['Label'] = -1  # -1 = Attack (Anomaly)
        dfs.append(df_attack)
        print(f"   🔴 Loaded Attack Data: {len(df_attack)} rows")
    else:
        print(f"   ❌ CRITICAL: {FILE_ATTACK} not found! Run augment_data.py first.")
        return

    # 4. Merge & Shuffle
    if dfs:
        master_df = pd.concat(dfs, ignore_index=True)
        
        # Shuffle rows so the model doesn't memorize the order
        master_df = master_df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Save
        master_df.to_csv(OUTPUT_FILE, index=False)
        
        print("-" * 30)
        print(f"🎉 MERGE COMPLETE!")
        print(f"📊 Total Rows: {len(master_df)}")
        print(f"   - Normal (1):  {len(master_df[master_df['Label'] == 1])}")
        print(f"   - Attack (-1): {len(master_df[master_df['Label'] == -1])}")
        print(f"💾 Saved to: {OUTPUT_FILE}")
        print("-" * 30)
    else:
        print("❌ No data loaded. Check your filenames.")

if __name__ == "__main__":
    merge_datasets()