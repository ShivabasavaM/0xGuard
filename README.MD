# 🛡️ 0xGuard: Autonomous AI Intrusion Detection System

**0xGuard** is a lightweight, edge-based Network Intrusion Detection System (NIDS) powered by Unsupervised Machine Learning. Unlike traditional firewalls that rely on static signatures, 0xGuard learns the behavioral baseline of a network to detect zero-day anomalies, port scans, and persistence threats in real-time.


---

## 📂 Project Structure

The project is organized into modular components for data engineering, training, and real-time inference:

```text
0xGuard/
├── data/                  # Stores raw CSV traffic logs (Normal & Attack)
├── models/                # Stores the trained Isolation Forest (.pkl)
├── src/                   # Helper modules (Feature Extraction, Response Logic)
├── augment_data.py        # Generates synthetic attack traffic to fix class imbalance
├── auto_tuner.py          # "Battle Arena" engine to optimize model hyperparameters
├── capture_baseline.py    # Sniffer tool to collect normal network traffic
├── main_guard.py          # The core Real-Time Protection Agent
├── merge_data.py          # Utility to combine federated datasets
├── train_model.py         # Standard model training script
└── requirements.txt       # Project dependencies

🚀 Getting Started
1. Prerequisites
This system requires Root/Sudo privileges to access the network card in promiscuous mode.
    pip install -r requirements.txt

2. Build the Intelligence (Data Pipeline)
Step A: Collect Baseline Data Capture "Normal" traffic from your device to teach the AI what safe behavior looks like.
    sudo python3 capture_baseline.py

Step B: Generate Synthetic Attacks Use Data Augmentation to create mathematical simulations of attacks (Port Scans, Floods) to ensure the model has a balanced training set.
    sudo python3 augment_data.py

Step C: Merge Datasets Combine your normal traffic and synthetic attacks into a master training set.
    python3 merge_data.py

3. Train & Optimize the Brain
Option A: The "Battle Arena" (Recommended) Automatically trains multiple models and tests them against the attack data to find the optimal sensitivity (Contamination Rate).
    python3 auto_tuner.py

Result: Saves the highest-performing model to models/isolation_forest.pkl

Option B: Manual Training Train a standard model with fixed parameters.
    python3 train_model.py

4. Start the Guard 🛡️
Launch the real-time agent. It monitors traffic in 5-second windows and takes autonomous action against threats.
    sudo python3 main_guard.py

🧠 How It Works
Packet Sniffing: scapy captures raw TCP/UDP headers.

Feature Engineering: src/feature_extractor.py converts raw packets into statistical features (Flow Duration, Packet Rate, Byte Variance).

Anomaly Detection: An Isolation Forest model evaluates the flow. If the anomaly score crosses the threshold, it is flagged.

Autonomous Response:
Level 1 (Warning): Logs suspicious activity.
Level 2 (Critical): Detects persistence.
Level 3 (Action): Updates Firewall rules to block the IP.

📊 Performance
Precision: ~95% (Optimized via Auto-Tuner)
False Positive Rate: <3% (On optimized 0.02 contamination)
Latency: <50ms processing time per window