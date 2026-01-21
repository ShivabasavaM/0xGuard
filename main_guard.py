import time
import joblib
import pandas as pd
from scapy.all import sniff
from src.feature_extractor import FlowExtractor
from src.response_manager import ResponseManager
import sys
import os

# Fix path
sys.path.append(os.getcwd())

import time
import joblib
# ... rest of your code ...
# CONFIGURATION
WINDOW_SIZE = 5  # Analyze traffic every 5 seconds

print("🛡️ 0xGuard INITIALIZING...")

# 1. Load Model
try:
    model = joblib.load("models/isolation_forest.pkl")
    print("✅ Brain Loaded.")
except:
    print("❌ Model not found. Run train_model.py first.")
    exit()

# 2. Initialize Components
extractor = FlowExtractor()
responder = ResponseManager()

print(f"🟢 MONITORING ACTIVE (Window: {WINDOW_SIZE}s)... Press Ctrl+C to stop.")

try:
    while True:
        # A. Capture for Window
        sniff(timeout=WINDOW_SIZE, prn=extractor.process_packet)
        
        # B. Extract Features
        df, flow_keys = extractor.extract_features()
        
        if not df.empty:
            # C. Predict (1=Normal, -1=Anomaly)
            predictions = model.predict(df)
            
            # D. Analyze Results
            for i, pred in enumerate(predictions):
                if pred == -1:
                    src_ip = flow_keys[i][0] # Get Source IP from key
                    dst_port = flow_keys[i][2]
                    
                    print(f"🔻 ANOMALY DETECTED: {src_ip} -> Port {dst_port}")
                    responder.handle_threat(src_ip)
            
            print(f"Analyzed {len(df)} flows. System Clean.")
        else:
            print("No traffic in this window...")

except KeyboardInterrupt:
    print("\n🔴 0xGuard STOPPED.")