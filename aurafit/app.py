from pathlib import Path
import importlib.util
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="C.A.R.S. Disaster Response System",
    page_icon="🚨",
    layout="wide"
)

if "view" not in st.session_state:
    st.session_state.view = "home"


def load_module(module_name, relative_path):
    path = ROOT_DIR / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Module not found: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
            st.session_state.view = "victim"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='background: white; padding: 24px; border-radius: 18px; box-shadow: 0 4px 24px rgba(0,0,0,0.04); text-align: center;'>", unsafe_allow_html=True)
        st.subheader("Dispatch Command Center")
        st.write("Real-time live incident mapping, triage charts, and resource routing management for NEMA/SEMA services.")
        if st.button("Open Dispatch HQ", type="primary", use_container_width=True):
            st.session_state.view = "responder"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def show_victim_page():
    st.session_state.view = "victim"
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()
    module = load_module("victim_app", "app_pages/victim_interface.py")
    if hasattr(module, "main"):
        module.main()


def show_responder_page():
    st.session_state.view = "responder"
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()
    module = load_module("responder_app", "app_pages/2_responder_dashboard.py")
    if hasattr(module, "main"):
        module.main()


if st.session_state.view == "victim":
    show_victim_page()
elif st.session_state.view == "responder":
    show_responder_page()
else:
    show_home()
