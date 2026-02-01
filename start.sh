#!/bin/bash

# 1. Start the AI Guard in the background (&)
echo "🛡️ Starting 0xGuard Engine..."
python main.py &

# 2. Wait a second to ensure logs are created
sleep 2

# 3. Start the Dashboard (and keep it running)
echo "📊 Starting Dashboard..."
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0