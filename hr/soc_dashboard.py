#!/usr/bin/env python3
"""
STRATEGICKHAOS Dashboard
Streamlit-based SOC dashboard for real-time monitoring
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time

# === PAGE CONFIG ===

st.set_page_config(
    page_title="STRATEGICKHAOS Empire Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-healthy { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-critical { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# === API ENDPOINTS ===

HR_API = "http://hr-api:8002"
LEGION_API = "http://legion-orchestrator:8000"
QDRANT_API = "http://qdrant:6333"

def safe_request(url, method="GET", **kwargs):
    """Make safe API requests with error handling"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5, **kwargs)
        elif method == "POST":
            response = requests.post(url, timeout=5, **kwargs)
        else:
            return None
            
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# === MAIN DASHBOARD ===

def main():
    st.markdown('<h1 class="main-header">🏛️ STRATEGICKHAOS EMPIRE DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown("**Node 137 | Real-time SOC Monitoring | Domenic Garza (@strategickhaos)**")
    
    # === SIDEBAR ===
    
    with st.sidebar:
        st.header("🎯 Empire Controls")
        
        if st.button("🔄 Refresh All"):
            st.rerun()
            
        st.header("🗣️ Jarvis Commands")
        st.code('''
        "Hey Jarvis, run full recon"
        "Hey Jarvis, show employee status"
        "Hey Jarvis, check system health"
        ''')
        
        st.header("📡 Service Status")
        services = {
            "HR API": safe_request(f"{HR_API}/health"),
            "Legion": safe_request(f"{LEGION_API}/health"),
            "Qdrant": safe_request(f"{QDRANT_API}/collections")
        }
        
        for service, status in services.items():
            if status:
                st.success(f"✅ {service}")
            else:
                st.error(f"❌ {service}")
    
    # === MAIN CONTENT ===
    
    col1, col2, col3 = st.columns(3)\n    \n    # === ORGANIZATION STATS ===\n    \n    with col1:\n        st.header(\"👔 HR & Organization\")\n        \n        hr_stats = safe_request(f\"{HR_API}/stats\")\n        if hr_stats:\n            st.metric(\"Total Agents\", hr_stats.get(\"total_agents\", 0))\n            st.metric(\"Active Agents\", hr_stats.get(\"active_agents\", 0))\n            st.metric(\"Pending Complaints\", hr_stats.get(\"pending_complaints\", 0))\n            \n            health = hr_stats.get(\"system_health\", \"unknown\")\n            health_color = \"status-healthy\" if health == \"excellent\" else \"status-warning\" if health in [\"fair\", \"concerning\"] else \"status-critical\"\n            st.markdown(f'<p class=\"{health_color}\">System Health: {health.upper()}</p>', unsafe_allow_html=True)\n            \n            performance = hr_stats.get(\"average_performance\", 0)\n            st.progress(performance / 100)\n            st.caption(f\"Average Performance: {performance:.1f}%\")\n        else:\n            st.error(\"HR API unavailable\")\n    \n    # === LEGION RECON STATUS ===\n    \n    with col2:\n        st.header(\"🏛️ Legion Recon\")\n        \n        legion_status = safe_request(f\"{LEGION_API}/status\")\n        if legion_status:\n            st.metric(\"Total Reports\", legion_status.get(\"total_reports\", 0))\n            st.metric(\"Active Recons\", legion_status.get(\"active_recons\", 0))\n            \n            jarvis_status = \"🟢 Connected\" if legion_status.get(\"jarvis_connected\") else \"🔴 Disconnected\"\n            st.write(f\"Jarvis: {jarvis_status}\")\n            \n            qdrant_status = \"🟢 Connected\" if legion_status.get(\"qdrant_connected\") else \"🔴 Disconnected\"\n            st.write(f\"Qdrant: {qdrant_status}\")\n            \n            last_recon = legion_status.get(\"last_recon\")\n            if last_recon:\n                st.caption(f\"Last Recon: {last_recon}\")\n        else:\n            st.error(\"Legion API unavailable\")\n        \n        # Manual recon trigger\n        if st.button(\"🚀 Trigger Recon\"):\n            result = safe_request(f\"{LEGION_API}/trigger\", method=\"POST\", json={})\n            if result:\n                st.success(\"Recon triggered successfully!\")\n            else:\n                st.error(\"Failed to trigger recon\")\n    \n    # === MEMORY & INTELLIGENCE ===\n    \n    with col3:\n        st.header(\"🧠 Memory & Intelligence\")\n        \n        qdrant_collections = safe_request(f\"{QDRANT_API}/collections\")\n        if qdrant_collections and \"result\" in qdrant_collections:\n            collections = qdrant_collections[\"result\"][\"collections\"]\n            st.metric(\"Qdrant Collections\", len(collections))\n            \n            for collection in collections:\n                st.write(f\"📚 {collection['name']}: {collection.get('vectors_count', 0)} vectors\")\n        else:\n            st.error(\"Qdrant unavailable\")\n        \n        # Quick stats\n        st.subheader(\"⚡ Quick Stats\")\n        st.info(\"Empire Status: OPERATIONAL\")\n        st.info(f\"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\")\n    \n    # === RECENT EVENTS ===\n    \n    st.header(\"📋 Recent Events\")\n    \n    col_hr, col_legion = st.columns(2)\n    \n    with col_hr:\n        st.subheader(\"👔 HR Events\")\n        hr_events = safe_request(f\"{HR_API}/events\")\n        if hr_events and \"events\" in hr_events:\n            events_df = pd.DataFrame(hr_events[\"events\"][:10])  # Last 10 events\n            if not events_df.empty:\n                st.dataframe(events_df[['timestamp', 'type']].head(), use_container_width=True)\n            else:\n                st.info(\"No HR events recorded\")\n        else:\n            st.error(\"Could not load HR events\")\n    \n    with col_legion:\n        st.subheader(\"🏛️ Legion Reports\")\n        legion_reports = safe_request(f\"{LEGION_API}/reports\")\n        if legion_reports and \"reports\" in legion_reports:\n            reports = legion_reports[\"reports\"]\n            if reports:\n                reports_df = pd.DataFrame(reports)\n                st.dataframe(reports_df[['filename', 'size_bytes', 'modified']].head(), use_container_width=True)\n            else:\n                st.info(\"No recon reports available\")\n        else:\n            st.error(\"Could not load Legion reports\")\n    \n    # === AGENT LIST ===\n    \n    st.header(\"🤖 Active Agents\")\n    \n    agents = safe_request(f\"{HR_API}/agents\")\n    if agents and \"agents\" in agents:\n        agents_data = agents[\"agents\"]\n        if agents_data:\n            agents_df = pd.DataFrame(agents_data)\n            \n            # Display agents table\n            st.dataframe(\n                agents_df[['name', 'role', 'status', 'performance_score', 'complaints']],\n                use_container_width=True\n            )\n            \n            # Agent performance chart\n            if 'performance_score' in agents_df.columns:\n                st.subheader(\"📊 Agent Performance\")\n                st.bar_chart(agents_df.set_index('name')['performance_score'])\n        else:\n            st.info(\"No agents registered in the system\")\n    else:\n        st.error(\"Could not load agents data\")\n    \n    # === AUTO REFRESH ===\n    \n    if st.checkbox(\"Auto-refresh (30s)\"):\n        time.sleep(30)\n        st.rerun()\n\nif __name__ == \"__main__\":\n    main()