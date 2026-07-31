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

# Theme-aware & Apple-Inspired CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Hide default header line */
    header {visibility: hidden;}

    .nav-bar {
        background-color: var(--background-color, rgba(255, 255, 255, 0.05));
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 16px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
    }

    .nav-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    .stat-card {
        background-color: var(--background-color, rgba(255, 255, 255, 0.05));
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }

    .stat-val {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -1px;
    }

    .stat-lbl {
        font-size: 12px;
        font-weight: 600;
        opacity: 0.75;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_database():
    return AuraFitDatabase("data/aurafit.db")

db = init_database()

def main():
    if "responder_render_counter" not in st.session_state:
        st.session_state.responder_render_counter = 0
    st.session_state.responder_render_counter += 1
    chart_key = f"triage_breakdown_chart_{st.session_state.responder_render_counter}"

    st.markdown("""
    <div class="nav-bar">
        <div class="nav-title">🚨 Dispatch Command Center</div>
        <div style="font-weight: 500; opacity: 0.8;">NEMA / SEMA Network</div>
    </div>
    """, unsafe_allow_html=True)
    
    analytics = db.get_incident_analytics()

    if not analytics or analytics.get("total_incidents", 0) == 0:
        st.info("📡 System online. Awaiting incoming emergency transmissions from the victim portal.")
        return

    # ==========================================
    # METRICS ROW
    # ==========================================
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-val" style="color: #007AFF;">{analytics.get('total_incidents', 0)}</div>
            <div class="stat-lbl">Active Cases</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-val" style="color: #FF3B30;">{analytics.get('priority_distribution', {}).get('RED_IMMEDIATE', 0)}</div>
            <div class="stat-lbl">Critical Priority</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-val" style="color: #FF9500;">{analytics.get('priority_distribution', {}).get('YELLOW_DELAYED', 0)}</div>
            <div class="stat-lbl">Delayed Priority</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-val" style="color: #FF2D55;">{analytics.get('evacuation_required', 0)}</div>
            <div class="stat-lbl">Evacuations Needed</div>
        </div>
        """, unsafe_allow_html=True)

    # ==========================================
    # MAP & CHARTS
    # ==========================================
    map_col, chart_col = st.columns([2, 1])
    
    with map_col:
        st.markdown("<h4 style='font-weight: 600; margin-bottom: 16px;'>📍 Live Incident Map</h4>", unsafe_allow_html=True)
        all_incidents_all_status = db.get_all_incidents()
        map_incidents = [i for i in all_incidents_all_status if i.get('latitude') is not None and i.get('longitude') is not None]
        if map_incidents:
            map_df = pd.DataFrame([
                {"lat": i["latitude"], "lon": i["longitude"]} for i in map_incidents
            ])
            with st.container():
                st.map(map_df, latitude="lat", longitude="lon", size=40, color="#FF3B30")
        else:
            st.info("No GPS coordinates available yet.")

    with chart_col:
        st.markdown("<h4 style='font-weight: 600; margin-bottom: 16px;'>📊 Triage Breakdown</h4>", unsafe_allow_html=True)
        priority_data = analytics.get('priority_distribution', {})
        if priority_data:
            priority_df = pd.DataFrame([{"Priority": k.replace("_", " "), "Count": v} for k, v in priority_data.items()])
            fig = px.pie(priority_df, values='Count', names='Priority', hole=0.5,
                         color_discrete_sequence=['#FF3B30', '#FF9500', '#34C759', '#8E8E93'])
            fig.update_layout(
                margin=dict(t=0, b=0, l=0, r=0), 
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, key=chart_key)

    # ==========================================
    # SLEEK INCIDENT FEED WITH FILTERS
    # ==========================================
    st.markdown("<h4 style='font-weight: 600; margin-top: 32px; margin-bottom: 16px;'>📡 Active Dispatch Feed</h4>", unsafe_allow_html=True)
    
    f1, f2 = st.columns(2)
    with f1:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["ALL", "RED IMMEDIATE", "YELLOW DELAYED", "GREEN MINOR", "BLACK EXPECTANT"]
        )
    with f2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["ALL", "OPEN", "IN_PROGRESS", "RESOLVED"]
        )

    all_incidents = db.get_all_incidents()
    
    # Filter logic
    if priority_filter != "ALL":
        target_p = priority_filter.replace(" ", "_")
        all_incidents = [i for i in all_incidents if i.get("incident_priority") == target_p]
    
    if status_filter != "ALL":
        all_incidents = [i for i in all_incidents if i.get("status") == status_filter]

    if not all_incidents:
        st.info("No matching incidents found for selected filters.")
    else:
        # Sort by priority and timestamp
        priority_order = {"RED_IMMEDIATE": 1, "YELLOW_DELAYED": 2, "GREEN_MINOR": 3, "BLACK_EXPECTANT": 4}
        all_incidents.sort(key=lambda x: (priority_order.get(x.get('incident_priority'), 5), -x.get('id', 0)))
        
        for incident in all_incidents[:50]:
            status_str = incident.get('status', 'OPEN')
            status_emoji = "⏳" if status_str == 'OPEN' else ("🏃" if status_str == 'IN_PROGRESS' else "✅")
            p_str = incident.get('incident_priority', 'UNKNOWN').replace('_', ' ')
            loc_str = incident.get('location_description', 'Location unspecified')
            
            header_title = f"{status_emoji} #{incident.get('id')} [{status_str}] | {p_str} | {incident.get('incident_type', 'OTHER')} | {loc_str}"
            
            with st.expander(header_title, expanded=False):
                d1, d2 = st.columns([2, 1])
                
                with d1:
                    st.write(f"**Report ID:** #{incident.get('id')}  |  **Reported At:** {incident.get('created_at', 'N/A')}")
                    st.write(f"**Victim Language:** {incident.get('communication_language', 'English')}")
                    st.write(f"**Casualties Estimate:** {incident.get('casualty_count_estimate', 0)}")
                    
                    evac = incident.get('evacuation_required')
                    st.write(f"**Evacuation Needed:** {'🚨 YES' if evac else '✅ No'}")
                    
                    services = incident.get('emergency_services_required', [])
                    if services:
                        st.write(f"**Services Required:** {', '.join(services)}")
                        
                    hazards = incident.get('hazards_detected', [])
                    st.write(f"**Hazards:** {', '.join(hazards) if hazards else 'None detected'}")
                    
                    if incident.get('medical_summary'):
                        st.write(f"**Medical Assessment:** {incident.get('medical_summary')}")
                        
                    if incident.get('victim_calm_response'):
                        st.info(f"**Advice Sent to Victim ({incident.get('communication_language', 'Local dialect')}):** {incident.get('victim_calm_response')}")

                    lat = incident.get('latitude')
                    lon = incident.get('longitude')
                    if lat is not None and lon is not None:
                        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                        st.markdown(f"[🗺️ Open Coordinates ({lat:.5f}, {lon:.5f}) in Maps]({maps_url})")

                with d2:
                    st.write(f"**Current Case Status:** `{status_str}`")
                    if status_str == 'OPEN':
                        if st.button("Dispatch Rescue Team", key=f"inprog_{incident['id']}", type="primary", use_container_width=True):
                            db.update_incident_status(incident['id'], 'IN_PROGRESS')
                            st.rerun()
                    elif status_str == 'IN_PROGRESS':
                        if st.button("Mark Case Resolved", key=f"resolved_{incident['id']}", use_container_width=True):
                            db.update_incident_status(incident['id'], 'RESOLVED')
                            st.rerun()
                    else:
                        if st.button("Re-open Case", key=f"reopen_{incident['id']}", use_container_width=True):
                            db.update_incident_status(incident['id'], 'OPEN')
                            st.rerun()

if __name__ == "__main__":
    main()
