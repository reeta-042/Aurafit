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


def get_cached_module(module_name, relative_path):
    cache_key = f"{module_name}_module"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = load_module(module_name, relative_path)
    return st.session_state[cache_key]


def show_home():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        .home-title {
            text-align: center;
            padding: 30px 10px;
        }

        .home-heading {
            font-size: 42px;
            font-weight: 700;
            letter-spacing: -1px;
            margin-bottom: 8px;
        }

        .home-subheading {
            font-size: 18px;
            font-weight: 500;
            opacity: 0.75;
        }

        .portal-card {
            background-color: var(--background-color, rgba(255, 255, 255, 0.05));
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 18px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
            margin-bottom: 20px;
        }

        .portal-card h3 {
            margin-bottom: 12px;
            font-weight: 600;
        }

        .portal-card p {
            opacity: 0.8;
            font-size: 15px;
            line-height: 1.5;
            margin-bottom: 18px;
        }
        </style>

        <div class="home-title">
            <h1 class="home-heading">🚨 C.A.R.S. Platform</h1>
            <p class="home-subheading">Crisis AI Response System</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="portal-card">
            <h3>Emergency Reporting Portal</h3>
            <p>For citizens and victims to send multimodal crisis reports with automated triage and dialect analysis.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Victim Portal", type="primary", use_container_width=True):
            st.session_state.view = "victim"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="portal-card">
            <h3>Dispatch Command Center</h3>
            <p>Real-time live incident mapping, triage charts, and resource routing management for NEMA/SEMA services.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Dispatch HQ", type="primary", use_container_width=True):
            st.session_state.view = "responder"
            st.rerun()


def show_victim_page():
    st.session_state.view = "victim"
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()
    module = get_cached_module("victim_app", "app_pages/victim_interface.py")
    if hasattr(module, "main"):
        module.main()


def show_responder_page():
    st.session_state.view = "responder"
    if st.button("🏠 Back to Home", use_container_width=True):
        st.session_state.view = "home"
        st.rerun()
    module = get_cached_module("responder_app", "app_pages/2_responder_dashboard.py")
    if hasattr(module, "main"):
        module.main()


if st.session_state.view == "victim":
    show_victim_page()
elif st.session_state.view == "responder":
    show_responder_page()
else:
    show_home()
