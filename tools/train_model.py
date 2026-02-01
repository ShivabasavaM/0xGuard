import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import ParameterGrid
from sklearn.metrics import precision_score, recall_score, f1_score

# CONFIGURATION
DATA_FILE = "data/master_merged.csv"
MODEL_PATH = "models/isolation_forest.pkl"

# 🧠 THE "HYPERPARAMETER GRID"
# We test ALL these combinations to find the perfect brain.
param_grid = {
    'n_estimators': [100, 200],         # More trees = More stable (but slower)
    'max_samples': [128, 256, 'auto'],  # How many samples each tree sees
    'contamination': [0.01, 0.02, 0.03, 0.04, 0.05], # Sensitivity (1% to 5%)
    'random_state': [42]
}

def train_and_tune():
    print("⚔️  ENTERING THE BATTLE ARENA (Auto-Tuning)...")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: {DATA_FILE} not found. Run merge_data.py first!")
        return

    # 1. Load Data
    df = pd.read_csv(DATA_FILE)
    
    # Features to train on (Must match feature_extractor.py!)
    features = ["Dst_Port", "Protocol", "Flow_Packets", "Flow_Bytes", 
                "Flow_Duration", "Packet_Rate", "Byte_Rate", "TCP_Flags_Sum"]
    
    X = df[features]
    y_true = df['Label'] # 1 = Normal, -1 = Attack

    best_score = 0
    best_params = None
    best_model = None
    
    # 2. Grid Search Loop
    print(f"🔎 Testing {len(list(ParameterGrid(param_grid)))} different model configurations...")
    
    for params in ParameterGrid(param_grid):
        # Train Model
        clf = IsolationForest(**params, n_jobs=-1)
        clf.fit(X)
        
        # Predict
        y_pred = clf.predict(X)
        
        # 3. Custom Scoring: "The Recruiter Score"
        # We value Precision (No False Positives) more than Recall.
        # If we block YouTube (False Positive), we fail.
        prec = precision_score(y_true, y_pred, pos_label=-1, zero_division=0)
        rec = recall_score(y_true, y_pred, pos_label=-1, zero_division=0)
        
        # We filter out models that are too trigger-happy (Low Precision)
        if prec < 0.90: 
            score = 0 # Disqualify models with <90% Precision
        else:
            # F1 Score weighted towards precision
            score = f1_score(y_true, y_pred, pos_label=-1, zero_division=0)

        print(f"   👉 Config: {params} | Precision: {prec:.2f} | Recall: {rec:.2f}")

        # Save Winner
        if score > best_score:
            best_score = score
            best_params = params
            best_model = clf

    # 4. Final Result
    print("\n🏆 CHAMPION MODEL FOUND!")
    print(f"   Config: {best_params}")
    print(f"   Best Score: {best_score:.4f}")
    
    # Save to disk
    joblib.dump(best_model, MODEL_PATH)
    print(f"✅ Saved optimized brain to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_tune()