"""
Agency Dispatch Center for C.A.R.S
Real-time incident management for NEMA/SEMA and emergency services
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.database import AuraFitDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="C.A.R.S - Dispatch",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apple-Inspired CSS
st.markdown("""
    <style>
    /* Force Apple System Fonts and Light Gray Background */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        background-color: #F5F5F7 !important; /* Apple hardware light gray */
        color: #1D1D1F !important;
    }
    
    .stApp {
        background-color: #F5F5F7 !important;
    }

    /* Hide the default header line to make it look like a native app */
    header {visibility: hidden;}

    /* Glass/Apple Cards */
    .apple-card {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
        border: none;
        margin-bottom: 20px;
        transition: transform 0.2s ease;
    }
    
    .apple-card:hover {
        transform: translateY(-2px);
    }

    /* Top Navigation Bar */
    .nav-bar {
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 16px 32px;
        border-radius: 20px;
        margin-bottom: 32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }

    .nav-title {
        font-size: 24px;
        font-weight: 600;
        letter-spacing: -0.5px;
        color: #1D1D1F;
    }

    /* Clean Metrics */
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        letter-spacing: -1px;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 500;
        color: #86868B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Native-looking buttons */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_database():
    return AuraFitDatabase("data/aurafit.db")

db = init_database()

def main():
    # 1. Render the nav bar BEFORE checking data so the layout isn't completely empty
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-title">Dispatch Command</div>
        <div style="color: #86868B; font-weight: 500;">NEMA / SEMA Network</div>
    </div>
    """, unsafe_allow_html=True)
    
    analytics = db.get_incident_analytics()

    # 2. Handle empty state gracefully without cutting off the code engine entirely
    if not analytics or analytics.get("total_incidents", 0) == 0:
        st.info("📡 System online. Awaiting incoming emergency transmissions from the victim portal.")
        
        # Optional: Add a button to seed mock data during testing
        if st.button("Seed Test Incident Data"):
            # Call a helper to populate a mock row to test maps/charts
            db.insert_mock_incident() 
            st.rerun()
        return

    # ... rest of your layout code continues safely below ...

    # ==========================================
    # METRICS ROW (Clean, Apple Health style)
    # ==========================================
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="apple-card">
            <div class="metric-value" style="color: #007AFF;">{analytics.get('total_incidents', 0)}</div>
            <div class="metric-label">Active Cases</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="apple-card">
            <div class="metric-value" style="color: #FF3B30;">{analytics.get('priority_distribution', {}).get('RED_IMMEDIATE', 0)}</div>
            <div class="metric-label">Critical Priority</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="apple-card">
            <div class="metric-value" style="color: #FF9500;">{analytics.get('priority_distribution', {}).get('YELLOW_DELAYED', 0)}</div>
            <div class="metric-label">Delayed Priority</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="apple-card">
            <div class="metric-value" style="color: #FF2D55;">{analytics.get('evacuation_required', 0)}</div>
            <div class="metric-label">Evacuations Needed</div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # MAP & CHARTS
    # ==========================================
    map_col, chart_col = st.columns([2, 1])
    
    with map_col:
        st.markdown("<h4 style='font-weight: 600; margin-bottom: 16px;'>Live Tracking</h4>", unsafe_allow_html=True)
        map_incidents = [i for i in db.get_all_incidents() if i.get('latitude') is not None and i.get('longitude') is not None]
        if map_incidents:
            map_df = pd.DataFrame([
                {"lat": i["latitude"], "lon": i["longitude"]} for i in map_incidents
            ])
            # Wrap map in a container to give it rounded edges
            with st.container():
                st.map(map_df, latitude="lat", longitude="lon", size=40, color="#FF3B30")
        else:
            st.info("No GPS coordinates provided by active reporters yet.")

    with chart_col:
        st.markdown("<h4 style='font-weight: 600; margin-bottom: 16px;'>Triage Breakdown</h4>", unsafe_allow_html=True)
        priority_data = analytics.get('priority_distribution', {})
        if priority_data:
            priority_df = pd.DataFrame([{"Priority": k.replace("_", " "), "Count": v} for k, v in priority_data.items()])
            # Apple color palette for charts
            fig = px.pie(priority_df, values='Count', names='Priority', hole=0.5,
                         color_discrete_sequence=['#FF3B30', '#FF9500', '#34C759', '#8E8E93'])
            fig.update_layout(
                margin=dict(t=0, b=0, l=0, r=0), 
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

    # ==========================================
    # SLEEK INCIDENT FEED
    # ==========================================
    st.markdown("<h4 style='font-weight: 600; margin-top: 32px; margin-bottom: 16px;'>Active Dispatch Feed</h4>", unsafe_allow_html=True)
    
    all_incidents = db.get_all_incidents()
    
    if not all_incidents:
        st.success("No active incidents.")
    else:
        # Sort by priority
        priority_order = {"RED_IMMEDIATE": 1, "YELLOW_DELAYED": 2, "GREEN_MINOR": 3, "BLACK_EXPECTANT": 4}
        all_incidents.sort(key=lambda x: (priority_order.get(x['incident_priority'], 5), -x['id']))
        
        for incident in all_incidents[:50]:
            status_emoji = "⏳" if incident['status'] == 'OPEN' else ("🏃" if incident['status'] == 'IN_PROGRESS' else "✅")
            
            # Clean, compact title for the expander
            header_title = f"{status_emoji} {incident['incident_priority'].replace('_', ' ')} | {incident['incident_type']} | {incident['location_description']}"
            
            # expanded=False forces all tabs to be closed by default for a clean look
            with st.expander(header_title, expanded=False):
                d1, d2 = st.columns([2, 1])
                
                with d1:
                    st.write(f"**Casualties:** {incident['casualty_count_estimate']}")
                    st.write(f"**Hazards:** {', '.join(incident['hazards_detected']) if incident['hazards_detected'] else 'None'}")
                    if incident.get('latitude') is not None:
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={incident['latitude']},{incident['longitude']}"
                        st.markdown(f"[🗺️ Open in Apple/Google Maps]({maps_url})")

                with d2:
                    if incident['status'] == 'OPEN':
                        if st.button("Dispatch Team", key=f"inprog_{incident['id']}", type="primary", use_container_width=True):
                            db.update_incident_status(incident['id'], 'IN_PROGRESS')
                            st.rerun()
                    elif incident['status'] == 'IN_PROGRESS':
                        if st.button("Resolve Case", key=f"resolved_{incident['id']}", use_container_width=True):
                            db.update_incident_status(incident['id'], 'RESOLVED')
                            st.rerun()

if __name__ == "__main__":
    main()