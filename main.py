import os
import time
import joblib
import logging
import pandas as pd
from datetime import datetime
from scapy.all import sniff
from src.feature_extractor import FlowExtractor
from src.response_manager import ResponseManager

# --- CONFIGURATION ---
MODEL_PATH = "models/isolation_forest.pkl"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "security_log.csv")
CAPTURE_WINDOW = 5  # Seconds

# --- LOGGING SETUP ---
# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure console output (Standard format)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [0xGUARD] - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("0xGuard")

class NIDS:
    """
    Network Intrusion Detection System (NIDS) v2.0
    Uses Isolation Forest (Unsupervised Learning) to detect zero-day anomalies.
    """

    def __init__(self):
        self._load_model()
        self.extractor = FlowExtractor()
        self.responder = ResponseManager()
        self._init_csv_logger()

    def _load_model(self):
        """Loads the pre-trained Isolation Forest model."""
        if not os.path.exists(MODEL_PATH):
            logger.critical(f"Model not found at {MODEL_PATH}. Run tools/train_model.py first.")
            exit(1)
        self.clf = joblib.load(MODEL_PATH)
        logger.info(f"Model loaded successfully from {MODEL_PATH}")

    def _init_csv_logger(self):
        """Initializes the CSV audit log for the dashboard."""
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                f.write("Timestamp,Source_IP,Risk_Level,Action,Protocol,Anomaly_Score\n")

    def _log_threat(self, ip, risk, action, protocol, score):
        """Writes threat details to the persistent CSV log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp},{ip},{risk},{action},{protocol},{score:.4f}\n")

    def analyze_traffic(self):
        """Main loop: Captures, Features Extracts, Predicts, and Responds."""
        # 1. Capture Traffic
        # logger.info(f"Capturing traffic for {CAPTURE_WINDOW}s...")
        sniff(timeout=CAPTURE_WINDOW, prn=self.extractor.process_packet, store=0)

        # 2. Extract Features
        df, _ = self.extractor.extract_features()

        if df.empty:
            return

        # 3. Inference
        feature_cols = ["Dst_Port", "Protocol", "Flow_Packets", "Flow_Bytes", 
                        "Flow_Duration", "Packet_Rate", "Byte_Rate", "TCP_Flags_Sum"]
        
        try:
            predictions = self.clf.predict(df[feature_cols])
            scores = self.clf.decision_function(df[feature_cols])
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return

        # 4. Response Logic
        for i, result in enumerate(predictions):
            if result == -1:  # Anomaly Detected
                ip_src = "192.168.0.195"  # (Note: In live deploy, extract from packet metadata)
                score = scores[i]
                protocol = df.iloc[i]["Protocol"]

                if score < 0.00:
                    logger.warning(f"BLOCKING MALICIOUS TRAFFIC: {ip_src} (Score: {score:.3f})")
                    self.responder.block_ip(ip_src)
                    self._log_threat(ip_src, "CRITICAL", "BLOCKED", protocol, score)
                
                elif score < -0.05:
                    logger.info(f"Suspicious Activity Detected: {ip_src}")
                    self._log_threat(ip_src, "HIGH", "ALERT", protocol, score)
                
                else:
                    # Low confidence anomalies are logged but not printed to console to reduce noise
                    self._log_threat(ip_src, "MEDIUM", "LOGGED", protocol, score)

if __name__ == "__main__":
    logger.info("Initializing 0xGuard Autonomous Agent...")
    guard = NIDS()
    logger.info("Monitoring Active. Press Ctrl+C to stop.")
    
    try:
        while True:
            guard.analyze_traffic()
    except KeyboardInterrupt:
        logger.info("Shutting down agent.")