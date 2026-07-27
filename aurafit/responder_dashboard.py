"""
Responder Command Dashboard for AuraFit
Real-time incident management for emergency responders
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.database import AuraFitDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="AuraFit - Responder Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for responder dashboard
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1b2a;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1a2a3a;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #00aaff;
    }
    .incident-card-red {
        background-color: #3a1a1a;
        border-left: 5px solid #ff4444;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .incident-card-yellow {
        background-color: #3a3a1a;
        border-left: 5px solid #ffaa00;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .incident-card-green {
        background-color: #1a3a1a;
        border-left: 5px solid #00aa00;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .dashboard-header {
        background-color: #ff4444;
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def init_database():
    return AuraFitDatabase("data/aurafit.db")

db = init_database()

def get_card_class(priority: str) -> str:
    """Get CSS class based on priority"""
    priority_class_map = {
        "RED_IMMEDIATE": "incident-card-red",
        "YELLOW_DELAYED": "incident-card-yellow",
        "GREEN_MINOR": "incident-card-green",
        "BLACK_EXPECTANT": "incident-card-red"
    }
    return priority_class_map.get(priority, "incident-card-yellow")

def format_priority_badge(priority: str) -> str:
    """Format priority as badge"""
    priority_map = {
        "RED_IMMEDIATE": "🔴 CRITICAL",
        "YELLOW_DELAYED": "🟡 DELAYED",
        "GREEN_MINOR": "🟢 MINOR",
        "BLACK_EXPECTANT": "⚫ EXPECTANT"
    }
    return priority_map.get(priority, priority)

def main():
    st.markdown("""
    <div class="dashboard-header">
    📊 AURAFIT - SEMA/NEMA Responder Command Center 📊
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh
    st.write("*Real-time incident tracking and triage management*")
    
    # Refresh button
    col_refresh, col_spacer = st.columns([1, 10])
    with col_refresh:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get analytics
    analytics = db.get_incident_analytics()
    
    if analytics.get("total_incidents", 0) == 0:
        st.info("⏳ No incidents reported yet. Awaiting emergency submissions...")
    else:
        # Summary metrics
        st.write("### 📈 INCIDENT SUMMARY")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
            <div style="font-size: 24px; font-weight: bold; color: #00aaff">
            {analytics.get('total_incidents', 0)}
            </div>
            <div style="font-size: 12px">Total Incidents</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            red_count = analytics.get('priority_distribution', {}).get('RED_IMMEDIATE', 0)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #ff4444">
            <div style="font-size: 24px; font-weight: bold; color: #ff6666">
            {red_count}
            </div>
            <div style="font-size: 12px">CRITICAL (RED)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            yellow_count = analytics.get('priority_distribution', {}).get('YELLOW_DELAYED', 0)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #ffaa00">
            <div style="font-size: 24px; font-weight: bold; color: #ffdd00">
            {yellow_count}
            </div>
            <div style="font-size: 12px">DELAYED (YELLOW)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #ff9999">
            <div style="font-size: 24px; font-weight: bold; color: #ff9999">
            {analytics.get('total_casualties', 0)}
            </div>
            <div style="font-size: 12px">Est. Casualties</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #ff9999">
            <div style="font-size: 24px; font-weight: bold; color: #ff9999">
            {analytics.get('evacuation_required', 0)}
            </div>
            <div style="font-size: 12px">Evacuations Needed</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts & Map Section
        st.write("### 📊 ANALYTICS & GIS MAP")
        
        map_incidents = [i for i in db.get_all_incidents() if i.get('latitude') is not None and i.get('longitude') is not None]
        if map_incidents:
            st.write("#### 🗺️ Real-Time Incident Map")
            map_df = pd.DataFrame([
                {
                    "lat": i["latitude"],
                    "lon": i["longitude"],
                    "Incident": i["incident_type"],
                    "Priority": i["incident_priority"],
                    "Location": i["location_description"]
                }
                for i in map_incidents
            ])
            st.map(map_df, latitude="lat", longitude="lon", size=20, color="#ff4444")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Priority distribution
            priority_data = analytics.get('priority_distribution', {})
            if priority_data:
                priority_df = pd.DataFrame([
                    {"Priority": k.replace("_", " "), "Count": v}
                    for k, v in priority_data.items()
                ])
                
                fig = px.pie(priority_df, values='Count', names='Priority',
                            title="Incidents by Priority",
                            color_discrete_sequence=['#ff4444', '#ffaa00', '#00aa00', '#666666'])
                fig.update_layout(
                    template="plotly_dark",
                    font=dict(color="white"),
                    paper_bgcolor='rgba(13, 27, 42, 1)',
                    plot_bgcolor='rgba(13, 27, 42, 1)'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Type distribution
            type_data = analytics.get('type_distribution', {})
            if type_data:
                type_df = pd.DataFrame([
                    {"Type": k, "Count": v}
                    for k, v in sorted(type_data.items(), key=lambda x: x[1], reverse=True)[:8]
                ])
                
                fig = px.bar(type_df, x='Count', y='Type', orientation='h',
                            title="Incidents by Type",
                            color='Count',
                            color_continuous_scale=['#1a3a6a', '#0066ff'])
                fig.update_layout(
                    template="plotly_dark",
                    font=dict(color="white"),
                    paper_bgcolor='rgba(13, 27, 42, 1)',
                    plot_bgcolor='rgba(13, 27, 42, 1)',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Filtering and search
        st.write("### 🔍 INCIDENT SEARCH & FILTER")
        
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            priority_filter = st.multiselect(
                "Filter by Priority",
                ["RED_IMMEDIATE", "YELLOW_DELAYED", "GREEN_MINOR", "BLACK_EXPECTANT"],
                default=["RED_IMMEDIATE", "YELLOW_DELAYED"]
            )
        
        with filter_col2:
            incident_type_filter = st.text_input(
                "Filter by Incident Type",
                placeholder="e.g., FLOOD, BUILDING_COLLAPSE"
            )
        
        with filter_col3:
            search_query = st.text_input(
                "Search Location",
                placeholder="e.g., Lagos, Commercial Ave"
            )
        
        # Get incidents
        all_incidents = db.get_all_incidents()
        
        # Apply filters
        filtered_incidents = []
        for incident in all_incidents:
            if incident['incident_priority'] not in priority_filter:
                continue
            if incident_type_filter and incident_type_filter.upper() not in incident['incident_type']:
                continue
            if search_query and search_query.lower() not in incident['location_description'].lower():
                continue
            filtered_incidents.append(incident)
        
        # Display incidents
        st.write(f"### 🚨 ACTIVE INCIDENTS ({len(filtered_incidents)})")
        
        if filtered_incidents:
            # Sort by priority then by creation time
            priority_order = {"RED_IMMEDIATE": 1, "YELLOW_DELAYED": 2, "GREEN_MINOR": 3, "BLACK_EXPECTANT": 4}
            filtered_incidents.sort(
                key=lambda x: (priority_order.get(x['incident_priority'], 5), -x['id'])
            )
            
            for incident in filtered_incidents[:50]:  # Limit to 50 for performance
                priority = incident['incident_priority']
                card_class = get_card_class(priority)
                priority_badge = format_priority_badge(priority)
                
                with st.container(border=True):
                    col_badge, col_type, col_location = st.columns([2, 2, 3])
                    
                    with col_badge:
                        st.markdown(f"**{priority_badge}**")
                    
                    with col_type:
                        st.write(f"**{incident['incident_type']}**")
                    
                    with col_location:
                        st.write(f"📍 {incident['location_description']}")
                        lat = incident.get('latitude')
                        lon = incident.get('longitude')
                        gps_c = incident.get('gps_coordinates')
                        if lat is not None and lon is not None:
                            maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                            st.markdown(f"📍 **GPS:** `{lat:.5f}, {lon:.5f}` — [🗺️ **Open Google Maps Navigation**]({maps_url})")
                        elif gps_c:
                            st.write(f"📍 **GPS:** `{gps_c}`")
                    
                    col_casualties, col_evac, col_confidence = st.columns([2, 2, 2])
                    
                    with col_casualties:
                        st.write(f"Casualties: **{incident['casualty_count_estimate']}**")
                    
                    with col_evac:
                        evac = "✅ YES" if incident['evacuation_required'] else "❌ NO"
                        st.write(f"Evacuation: {evac}")
                    
                    with col_confidence:
                        st.write(f"Confidence: **{incident['confidence_score']:.0%}**")
                    
                    # Language & Victim Notes
                    comm_lang = incident.get('communication_language', 'English')
                    calm_resp = incident.get('victim_calm_response', '')
                    if comm_lang or calm_resp:
                        st.write(f"🌐 **Victim Communication Language:** {comm_lang}")
                        if calm_resp:
                            st.write(f"💬 **Victim Guidance Provided:** *\"{calm_resp}\"*")
                    
                    # Hazards
                    if incident['hazards_detected']:
                        st.write("**Hazards Detected:**")
                        hazards_text = ", ".join(incident['hazards_detected'])
                        st.write(hazards_text)
                    
                    # Medical summary
                    if incident['medical_summary']:
                        st.write("**Medical Assessment:**")
                        st.write(incident['medical_summary'])
                    
                    # Recommended actions
                    if incident['recommended_actions']:
                        st.write("**Recommended Actions:**")
                        for action in incident['recommended_actions'][:3]:
                            st.write(f"• {action}")
                    
                    # Status update
                    col_status_label, col_status_action = st.columns([2, 1])
                    with col_status_label:
                        st.write(f"**Status:** {incident['status']}")
                    with col_status_action:
                        if incident['status'] == 'OPEN':
                            if st.button("✅ Mark In-Progress", key=f"inprog_{incident['id']}", use_container_width=True):
                                db.update_incident_status(incident['id'], 'IN_PROGRESS')
                                st.rerun()
                        elif incident['status'] == 'IN_PROGRESS':
                            if st.button("✔️ Mark Resolved", key=f"resolved_{incident['id']}", use_container_width=True):
                                db.update_incident_status(incident['id'], 'RESOLVED')
                                st.rerun()
        
        else:
            st.info("No incidents match your filters")


if __name__ == "__main__":
    main()
