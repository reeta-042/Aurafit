from pathlib import Path
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent

# 1. Page Configuration
st.set_page_config(
    page_title="C.A.R.S. Disaster Response System",
    page_icon="🚨",
    layout="wide"
)

# 2. Define the pages relative to app.py
# Using absolute paths avoids Streamlit's working-directory resolution issues.
victim_page = st.Page(
    str(ROOT_DIR / "app_pages" / "victim_interface.py"),
    title="Victim Portal",
    icon="🆘"
)
responder_hq = st.Page(
    str(ROOT_DIR / "app_pages" / "2_responder_dashboard.py"),
    title="Responder Command Center",
    icon="🗺️"
)
# 3. Create a clean home landing dashboard
def show_home():
    st.markdown("""
        <div style='text-align: center; padding: 40px;'>
            <h1 style='font-size: 48px; font-weight: 700; letter-spacing: -1px;'>🚨 C.A.R.S. Platform</h1>
            <p style='color: #86868B; font-size: 20px; font-weight: 500;'>Crisis Action & Response System</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='background: white; padding: 24px; border-radius: 18px; box-shadow: 0 4px 24px rgba(0,0,0,0.04); text-align: center;'>", unsafe_allow_html=True)
        st.subheader("Emergency Reporting Portal")
        st.write("For citizens and victims to send multimodal crisis reports with automated triage and dialect analysis.")
        if st.button("Open Victim Portal", type="primary", use_container_width=True):
            st.switch_page(victim_page)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div style='background: white; padding: 24px; border-radius: 18px; box-shadow: 0 4px 24px rgba(0,0,0,0.04); text-align: center;'>", unsafe_allow_html=True)
        st.subheader("Dispatch Command Center")
        st.write("Real-time live incident mapping, triage charts, and resource routing management for NEMA/SEMA services.")
        if st.button("Open Dispatch HQ", type="primary", use_container_width=True):
            st.switch_page(responder_hq)
        st.markdown("</div>", unsafe_allow_html=True)

home_page = st.Page(show_home, title="Home HQ", icon="🏠")

# 4. Initialize Navigation
pg = st.navigation([home_page, victim_page, responder_hq])
pg.run()