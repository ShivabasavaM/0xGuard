import pandas as pd
import random
import numpy as np

# CONFIGURATION
OUTPUT_FILE = "data/attack_traffic.csv"
NUM_ROWS = 1000  # We want 1000 attack examples

print(f"🧪 generating {NUM_ROWS} synthetic attack flows...")

data = []

for _ in range(NUM_ROWS):
    # 1. ATTACK BEHAVIOR: Random High Ports (Scanning)
    dst_port = random.choice([80, 443] + list(range(1024, 65535)))
    
    # 2. ATTACK BEHAVIOR: TCP (Scan) or UDP (Flood)
    protocol = random.choice([6, 17])
    
    # 3. ATTACK BEHAVIOR: Low Packet Count (Scan) or High (Flood)
    flow_packets = random.randint(1, 50) if random.random() > 0.5 else random.randint(500, 5000)
    
    # 4. ATTACK BEHAVIOR: Fast Duration (Machine speed, not Human speed)
    flow_duration = random.uniform(0.001, 2.0)
    
    # 5. ATTACK BEHAVIOR: Massive Packet Rate (The key anomaly)
    # Normal is ~10-100. Attack is 500-100,000.
    packet_rate = flow_packets / flow_duration if flow_duration > 0 else 0
    
    # Calculate bytes (approximate)
    flow_bytes = flow_packets * random.randint(60, 1500)
    byte_rate = flow_bytes / flow_duration if flow_duration > 0 else 0
    
    # 6. ATTACK BEHAVIOR: Weird Flags (SYN flood, etc)
    tcp_flags = random.choice([2, 16, 18, 0, 41]) # SYN, ACK, SYN-ACK, NULL, etc.

    data.append([dst_port, protocol, flow_packets, flow_bytes, flow_duration, packet_rate, byte_rate, tcp_flags])

# Create DataFrame
columns = ["Dst_Port", "Protocol", "Flow_Packets", "Flow_Bytes", 
           "Flow_Duration", "Packet_Rate", "Byte_Rate", "TCP_Flags_Sum"]
df = pd.DataFrame(data, columns=columns)

# Save
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Success! Saved {len(df)} rows to {OUTPUT_FILE}")
print(df.head())