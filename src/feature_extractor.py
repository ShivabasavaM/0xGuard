import pandas as pd
from collections import defaultdict
from scapy.all import IP, TCP, UDP

class FlowExtractor:
    def __init__(self):
        # Key: (Src_IP, Dst_IP, Dst_Port, Protocol)
        self.current_flows = defaultdict(lambda: {
            "start_time": 0, "last_time": 0, "packet_count": 0, 
            "byte_count": 0, "tcp_flags": 0
        })

    def process_packet(self, packet):
        if IP in packet:
            src = packet[IP].src
            dst = packet[IP].dst
            proto = packet[IP].proto
            length = len(packet)
            timestamp = float(packet.time)
            
            dst_port = 0
            flags = 0
            if TCP in packet:
                dst_port = packet[TCP].dport
                flags = int(packet[TCP].flags)
            elif UDP in packet:
                dst_port = packet[UDP].dport

            flow_key = (src, dst, dst_port, proto)
            
            # Update Flow Data
            flow = self.current_flows[flow_key]
            if flow["packet_count"] == 0:
                flow["start_time"] = timestamp
            
            flow["last_time"] = timestamp
            flow["packet_count"] += 1
            flow["byte_count"] += length
            flow["tcp_flags"] |= flags # Accumulate flags

    def extract_features(self):
        """Converts raw flow data into a DataFrame for the ML model."""
        dataset = []
        flow_keys = []
        
        for key, data in self.current_flows.items():
            duration = data["last_time"] - data["start_time"]
            if duration == 0: duration = 0.001 # Avoid division by zero
            
            pkt_rate = data["packet_count"] / duration
            byte_rate = data["byte_count"] / duration
            
            # Features matched to training columns
            dataset.append([
                key[2], # Dst_Port
                key[3], # Protocol
                data["packet_count"],
                data["byte_count"],
                duration,
                pkt_rate,
                byte_rate,
                data["tcp_flags"]
            ])
            flow_keys.append(key) # Store keys to identify IP later
            
        columns = ["Dst_Port", "Protocol", "Flow_Packets", "Flow_Bytes", 
                   "Flow_Duration", "Packet_Rate", "Byte_Rate", "TCP_Flags_Sum"]
        
        # Reset flows after extraction (for next window)
        self.current_flows.clear()
        
        return pd.DataFrame(dataset, columns=columns), flow_keys