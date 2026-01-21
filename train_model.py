import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os
import sys

# --- PATH FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# ----------------

# 1. Configuration
# POINTING TO THE NEW MASTER FILE
DATA_FILE = os.path.join(current_dir, "data/master_normal_traffic.csv") 
MODEL_FILE = os.path.join(current_dir, "models/isolation_forest.pkl")

print(f"🧠 Training 0xGuard Brain on {DATA_FILE}...")

# 2. Load Data
if not os.path.exists(DATA_FILE):
    print(f"❌ Error: '{DATA_FILE}' not found.")
    print("   Did you run merge_data.py?")
    exit()

df = pd.read_csv(DATA_FILE)
print(f"   Loaded {len(df)} flow records.")

# 3. Feature Selection
# We drop the IPs because we want to learn BEHAVIOR, not specific ADDRESSES.
feature_cols = ["Dst_Port", "Protocol", "Flow_Packets", "Flow_Bytes", 
                "Flow_Duration", "Packet_Rate", "Byte_Rate", "TCP_Flags_Sum"]

X = df[feature_cols]

# 4. Train Model
# n_estimators=200: Increased from 100 to 200 for better stability with more data
# contamination=0.01: We assume 1% of your friend's data might be noise/weird.
print("   Fitting Isolation Forest model (this might take a moment)...")
model = IsolationForest(n_estimators=200, contamination=0.005, random_state=42)
model.fit(X)

# 5. Save Model
if not os.path.exists(os.path.join(current_dir, "models")):
    os.makedirs(os.path.join(current_dir, "models"))

joblib.dump(model, MODEL_FILE)
print("-" * 30)
print(f"✅ SUCCESS! Model trained and saved to '{MODEL_FILE}'")
print(f"   The Brain is ready. You can now run the Guard.")
print("-" * 30)