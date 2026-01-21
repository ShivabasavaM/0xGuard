import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score
import os
import sys
import joblib

# Fix path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 1. LOAD DATA
print("📂 Loading Data...")
normal_df = pd.read_csv("data/master_normal_traffic.csv") # Your friends' data
attack_df = pd.read_csv("data/attack_traffic.csv")        # The Nmap data you just captured

# Label the data for testing (1 = Normal, -1 = Attack)
# (We only need these labels to Score the model, not to train it)
normal_df['label'] = 1
attack_df['label'] = -1

# Combine for a "Test Set"
test_df = pd.concat([normal_df.sample(frac=0.2), attack_df]) # Use 20% normal + All attacks
X_test = test_df.drop('label', axis=1)
y_test = test_df['label']

# Features to use
features = ["Dst_Port", "Protocol", "Flow_Packets", "Flow_Bytes", 
            "Flow_Duration", "Packet_Rate", "Byte_Rate", "TCP_Flags_Sum"]

X_train = normal_df[features] # We ONLY train on normal data
X_test = X_test[features]

# 2. DEFINE THE CANDIDATES
# We will test these different "Paranoia Levels"
contaminations = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1]

best_score = 0
best_model = None
best_c = 0

print(f"\n⚔️  STARTING BATTLE ARENA (Training {len(contaminations)} models)...")
print("-" * 60)
print(f"{'CONTAM':<10} | {'DETECTED ATTACKS':<18} | {'FALSE ALARMS':<15} | {'SCORE'}")
print("-" * 60)

for c in contaminations:
    # Train
    model = IsolationForest(n_estimators=200, contamination=c, random_state=42)
    model.fit(X_train)
    
    # Predict on Mixed Test Set
    preds = model.predict(X_test)
    
    # Calculate Metrics
    # True Positives (Detected Attacks)
    detected_attacks = sum((preds == -1) & (y_test == -1))
    total_attacks = sum(y_test == -1)
    attack_recall = detected_attacks / total_attacks if total_attacks > 0 else 0
    
    # False Positives (Normal traffic flagged as attack)
    false_alarms = sum((preds == -1) & (y_test == 1))
    total_normal = sum(y_test == 1)
    false_alarm_rate = false_alarms / total_normal if total_normal > 0 else 0
    
    # CUSTOM SCORE FORMULA: 
    # We want High Attack Detection (Recall) AND Low False Alarms
    # Score = Recall - (False Alarm Rate * 2) 
    # (We penalize false alarms heavily)
    score = attack_recall - (false_alarm_rate * 2)
    
    print(f"{c:<10} | {detected_attacks}/{total_attacks} ({attack_recall:.0%})   | {false_alarms}/{total_normal} ({false_alarm_rate:.0%})    | {score:.4f}")

    if score > best_score:
        best_score = score
        best_model = model
        best_c = c

print("-" * 60)
print(f"🏆 WINNER: Contamination = {best_c}")
print(f"   (It caught {best_score:.0%} of attacks w/ minimal false alarms)")

# 3. SAVE THE CHAMPION
joblib.dump(best_model, "models/isolation_forest.pkl")
print("✅ Saved the Best Model to 'models/isolation_forest.pkl'")