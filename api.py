from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import traceback

# 1. Initialize App
app = FastAPI(title="0xGuard AI Security API", version="3.0 - Production")

# 2. Load Model
try:
    model = joblib.load('models/isolation_forest.pkl')
    print("✅ Model loaded. Ready for inference.")
except Exception as e:
    print(f"❌ CRITICAL: Model failed to load: {e}")
    model = None

# 3. Define EXACT Input Schema (Matching your Model)
class NetworkFlow(BaseModel):
    dst_port: int
    protocol: int
    flow_packets: int
    flow_bytes: int
    flow_duration: float
    packet_rate: float
    byte_rate: float
    tcp_flags_sum: int

# 4. Predict Endpoint
@app.post("/analyze")
def analyze_traffic(flow: NetworkFlow):
    if not model:
        raise HTTPException(status_code=500, detail="Model is offline")

    try:
        # Create DataFrame with EXACT column names and order
        input_data = pd.DataFrame([{
            'Dst_Port': flow.dst_port,
            'Protocol': flow.protocol,
            'Flow_Packets': flow.flow_packets,
            'Flow_Bytes': flow.flow_bytes,
            'Flow_Duration': flow.flow_duration,
            'Packet_Rate': flow.packet_rate,
            'Byte_Rate': flow.byte_rate,
            'TCP_Flags_Sum': flow.tcp_flags_sum
        }])

        # Get Anomaly Score
        score = model.decision_function(input_data)[0]

        # Threshold Logic (Tweak this if needed)
        threshold = 0.00
        status = "SAFE" if score > threshold else "THREAT"
        action = "ALLOW" if status == "SAFE" else "BLOCK"

        return {
            "status": status,
            "action": action,
            "anomaly_score": float(score),
            "details": "Traffic analyzed successfully"
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction Failed: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "active", "system": "0xGuard API"}