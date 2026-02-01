import sys
import os

# --- BULLETPROOF IMPORT FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
# -----------------------------

from scapy.all import sniff
from src.feature_extractor import FlowExtractor
import pandas as pd
import time

# CONFIGURATION
# 1200 seconds = 20 Minutes (The "Gold Standard" for baseline)
CAPTURE_SECONDS = 1200 

print(f"🔵 STARTING BASELINE CAPTURE ({CAPTURE_SECONDS}s)...")
print("⚡ ACTION REQUIRED: Go watch 4K YouTube, download files, and browse now!")

extractor = FlowExtractor()

# Capture packets
sniff(timeout=CAPTURE_SECONDS, prn=extractor.process_packet)

# Extract and Save
df, _ = extractor.extract_features()

# Ensure data folder exists
if not os.path.exists(os.path.join(current_dir, "data")):
    os.makedirs(os.path.join(current_dir, "data"))

# --- FIX: Saving as NORMAL traffic, not ATTACK ---
output_path = os.path.join(current_dir, "data/normal_shiva.csv")
df.to_csv(output_path, index=False)

print(f"✅ Baseline saved with {len(df)} flow records to {output_path}")
print(df.head())