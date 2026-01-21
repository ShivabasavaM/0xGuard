import sys
import os

# --- BULLETPROOF IMPORT FIX ---
# This tells Python: "Look for the 'src' folder right here, next to me."
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# -----------------------------

from scapy.all import sniff
from src.feature_extractor import FlowExtractor
import pandas as pd
import time

# CONFIGURATION
CAPTURE_SECONDS = 1000

print(f"🔵 STARTING BASELINE CAPTURE ({CAPTURE_SECONDS}s)... Browse the web now!")

extractor = FlowExtractor()

# Capture packets
# iface=None lets Scapy pick the default interface. 
# If it fails, we might need to specify iface="en0"
sniff(timeout=CAPTURE_SECONDS, prn=extractor.process_packet)

# Extract and Save
df, _ = extractor.extract_features()

# Ensure data folder exists
if not os.path.exists(os.path.join(current_dir, "data")):
    os.makedirs(os.path.join(current_dir, "data"))
    
output_path = os.path.join(current_dir, "data/attack_traffic.csv")
df.to_csv(output_path, index=False)

print(f"✅ Baseline saved with {len(df)} flow records to {output_path}")
print(df.head())