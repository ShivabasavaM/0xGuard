import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os

# --- CONFIGURATION ---
LOG_FILE = "logs/security_log.csv"
REFRESH_RATE = 2  # Seconds

st.set_page_config(
    page_title="0xGuard Security Console",
    page_icon="🛡️",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
    <style>
        .metric-card {
            background-color: #1E1E1E;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("0xGuard | Network Intrusion Detection System")
st.markdown("**Status:** 🟢 Active | **Model:** Isolation Forest v2.0 | **Mode:** Autonomous Response")
st.divider()

# --- REAL-TIME METRICS ---
col1, col2, col3, col4 = st.columns(4)
metric_total = col1.empty()
metric_blocked = col2.empty()
metric_critical = col3.empty()
metric_last_seen = col4.empty()

# --- CHARTS & LOGS ---
col_chart, col_log = st.columns([2, 1])

with col_chart:
    st.subheader("Threat Velocity (Packet Anomalies)")
    chart_placeholder = st.empty()

with col_log:
    st.subheader("Live Audit Log")
    log_placeholder = st.empty()

def load_logs():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["Timestamp", "Source_IP", "Risk_Level", "Action", "Protocol", "Anomaly_Score"])
    try:
        df = pd.read_csv(LOG_FILE)
        return df
    except Exception:
        return pd.DataFrame()

# --- MAIN LOOP ---
while True:
    df = load_logs()
    
    if not df.empty:
        # Metrics
        total_events = len(df)
        blocked_count = len(df[df['Action'] == 'BLOCKED'])
        critical_count = len(df[df['Risk_Level'] == 'CRITICAL'])
        last_event = df['Timestamp'].iloc[-1] if not df.empty else "N/A"

        metric_total.metric("Total Anomalies", total_events)
        metric_blocked.metric("⛔ Threats Mitigated", blocked_count, delta_color="inverse")
        metric_critical.metric("🔥 Critical Alerts", critical_count, delta_color="inverse")
        metric_last_seen.metric("Last Event", last_event.split(' ')[-1])

        # Chart: Anomalies over time
        if 'Timestamp' in df.columns:
            df['Time'] = pd.to_datetime(df['Timestamp'])
            hourly_counts = df.resample('1min', on='Time').count()['Source_IP']
            fig = px.area(hourly_counts, x=hourly_counts.index, y='Source_IP', title="Anomalies / Minute")
            fig.update_traces(line_color='#FF4B4B', fillcolor="rgba(255, 75, 75, 0.2)")
            fig.update_layout(xaxis_title="Time", yaxis_title="Events", template="plotly_dark")
            chart_placeholder.plotly_chart(fig, use_container_width=True, key=time.time())

        # Log Table
        latest_logs = df.tail(15)[::-1]
        
        def color_risk(val):
            color = '#ff4b4b' if val == 'CRITICAL' else '#ffa726' if val == 'HIGH' else '#ffffff'
            return f'color: {color}'

        log_placeholder.dataframe(
            latest_logs[['Timestamp', 'Risk_Level', 'Action']].style.applymap(color_risk, subset=['Risk_Level']),
            use_container_width=True,
            hide_index=True
        )
    else:
        metric_total.metric("System Status", "Scanning...")

    time.sleep(REFRESH_RATE)