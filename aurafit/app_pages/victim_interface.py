"""
Victim/Citizen Interface for C.A.R.S
Multimodal input (photo, voice, text) for emergency guidance
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sys
import logging
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.llm_provider import get_llm_provider
from src.core.database import AuraFitDatabase
from src.core.function_executor import parse_function_call
from src.utils.image_processor import process_uploaded_image, validate_image
from src.utils.audio_processor import transcribe_audio, text_to_speech, get_safe_actions

try:
    from streamlit_geolocation import streamlit_geolocation
except ImportError:
    streamlit_geolocation = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if "incident_data" not in st.session_state:
    st.session_state.incident_data = None
if "guidance_generated" not in st.session_state:
    st.session_state.guidance_generated = False
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .emergency-banner {
        background: linear-gradient(135deg, #d93025 0%, #b31412 100%);
        color: #ffffff !important;
        padding: 18px 24px;
        border-radius: 14px;
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 6px 18px rgba(217, 48, 37, 0.3);
        letter-spacing: -0.5px;
    }

    .guidance-step {
        background-color: rgba(30, 142, 62, 0.12);
        border-left: 6px solid #1e8e3e;
        padding: 16px;
        margin: 12px 0;
        border-radius: 10px;
        color: var(--text-color, inherit);
        font-size: 16px;
        font-weight: 500;
        line-height: 1.5;
    }

    .hazard-warning {
        background-color: rgba(217, 48, 37, 0.12);
        border-left: 6px solid #d93025;
        padding: 16px;
        margin: 12px 0;
        border-radius: 10px;
        color: var(--text-color, inherit);
        font-size: 15px;
        font-weight: 500;
        line-height: 1.5;
    }

    .calm-box {
        background-color: rgba(26, 115, 232, 0.12);
        border-left: 6px solid #1a73e8;
        padding: 20px;
        margin: 20px 0;
        border-radius: 12px;
        color: var(--text-color, inherit);
    }

    .calm-box h3 {
        color: #1a73e8 !important;
        margin-top: 0;
        font-weight: 600;
    }

    .triage-tag {
        color: #ffffff !important;
        padding: 14px;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
        font-size: 18px;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    [data-testid="stAudioInput"] {
        background-color: rgba(217, 48, 37, 0.08);
        padding: 12px;
        border-radius: 12px;
        border: 2px dashed #d93025;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_llm_provider():
    return get_llm_provider()

@st.cache_resource
def init_database():
    return AuraFitDatabase("data/aurafit.db")

try:
    llm_provider = init_llm_provider()
except Exception as e:
    logger.warning(f"LLM provider unavailable during startup: {e}")
    llm_provider = None

db = init_database()

def main():
    st.markdown("""
    <div class="emergency-banner">
    🚨 C.A.R.S.: Crisis AI Response System
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.guidance_generated:
        
        # Unified Language Selector
        st.markdown("### 🌐 Select Language")
        selected_language = st.selectbox(
            "Language",
            ["English", "Nigerian Pidgin", "Hausa", "Yoruba", "Igbo"],
            index=0,
            label_visibility="collapsed",
            help="Select the language you will speak/type in. The AI will reply in this language."
        )

        st.divider()

        # 1. Panic Mode: Voice First
        st.markdown("### 🎤 1. What is happening?")
        audio_data = st.audio_input("Record voice", label_visibility="collapsed")

        # 2. Unified Camera/Upload Box
        st.markdown("### 📷 2. Show us the scene (Required)")
        with st.container(border=True):
            photo_mode = st.radio(
                "Choose input method:", 
                ["📸 Camera", "📁 Gallery"], 
                horizontal=True, 
                label_visibility="collapsed"
            )
            image_raw_bytes = None
            
            if photo_mode == "📸 Camera":
                camera_photo = st.camera_input("Capture scene", label_visibility="collapsed")
                if camera_photo: 
                    image_raw_bytes = camera_photo.getvalue()
            else:
                uploaded_image = st.file_uploader("Select an image from gallery", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
                if uploaded_image: 
                    image_raw_bytes = uploaded_image.read()
                    st.image(image_raw_bytes, use_container_width=True, caption="Uploaded Image")

        # 3. Location Auto-Grab
        geo_location = None
        if streamlit_geolocation:
            geo_location = streamlit_geolocation()
            
        with st.expander("📝 I cannot speak (Type instead)"):
            text_input = st.text_area("Describe the emergency:", height=100)
            landmark_input = st.text_input("Nearby Landmark:")

        st.write("")
        
        if st.button("🚨 GET IMMEDIATE HELP", use_container_width=True, type="primary"):
            if llm_provider is None:
                st.error("⚠️ The AI service is unavailable right now. Please check the environment configuration and try again.")
                return
            if not image_raw_bytes:
                st.error("⚠️ We need a photo to assess hazards. Please take or upload a photo.")
            else:
                with st.spinner("🔄 C.A.R.S is analyzing the scene..."):
                    try:
                        image_bytes = process_uploaded_image(image_raw_bytes) if validate_image(image_raw_bytes) else None
                        audio_text = transcribe_audio(audio_data) if audio_data else None

                        gps_str = None
                        lat_val = None
                        lon_val = None
                        if geo_location and geo_location.get("latitude") is not None:
                            try:
                                lat_val = float(geo_location["latitude"])
                                lon_val = float(geo_location["longitude"])
                                gps_str = f"{lat_val:.5f}, {lon_val:.5f}"
                            except (ValueError, TypeError):
                                pass

                        analysis_prompt = f"""Victim Report:
                        User Selected Language: {selected_language}
                        Text Description: {text_input or 'None provided'}
                        Voice Transcription: {audio_text or 'None provided'}
                        Landmark: {landmark_input or 'Not provided'}
                        GPS: {gps_str or 'Not provided'}

                        INSTRUCTIONS:
                        1. The user is communicating in {selected_language}. Expect the voice transcription or text to be in this language/dialect.
                        2. Analyze the emergency, hazards, START triage priority, and casualty estimates.
                        3. CRITICAL: Generate 'victim_calm_response' and 'recommended_actions' STRICTLY in {selected_language}.
                        """
                        
                        response_text, function_call_data = llm_provider.analyze_disaster(
                            image_bytes=image_bytes, text_prompt=analysis_prompt, audio_text=audio_text
                        )
                        
                        incident_data = parse_function_call(response_text, function_call_data)
                        
                        if incident_data:
                            # Attach location, language, and GPS data explicitly
                            if gps_str: 
                                incident_data["gps_coordinates"] = gps_str
                            if lat_val is not None and lon_val is not None:
                                incident_data["latitude"] = lat_val
                                incident_data["longitude"] = lon_val
                            if landmark_input: 
                                incident_data["location_description"] = landmark_input
                            incident_data["communication_language"] = selected_language
                            
                            db.insert_incident(incident_data)
                            st.session_state.incident_data = incident_data
                            st.session_state.guidance_generated = True
                            st.rerun()
                        else:
                            st.error("Failed to analyze. Please try again.")
                            
                    except Exception as e:
                        logger.error(f"Error analyzing emergency report: {e}")
                        st.error("System error while processing report. Please try again.")

    else:
        incident = st.session_state.incident_data
        
        if st.button("← Submit Another Report", use_container_width=True):
            st.session_state.guidance_generated = False
            st.session_state.incident_data = None
            st.rerun()

        priority_color_map = {
            "RED_IMMEDIATE": "#d93025", 
            "YELLOW_DELAYED": "#f29900", 
            "GREEN_MINOR": "#1e8e3e", 
            "BLACK_EXPECTANT": "#202124"
        }
        priority = incident.get("incident_priority", "YELLOW_DELAYED")
        
        st.markdown(f"""
        <div class="triage-tag" style="background-color: {priority_color_map.get(priority, '#f29900')}">
        TRIAGE LEVEL: {priority.replace('_', ' ')}
        </div>
        """, unsafe_allow_html=True)
        
        calm_msg = incident.get("victim_calm_response")
        if calm_msg:
            st.markdown(f"""
            <div class="calm-box">
                <h3>🛡️ Message from AuraFit</h3>
                <p style="font-size: 18px; line-height: 1.5; margin-bottom: 0;">{calm_msg}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Step-by-Step Safety Guide")
        actions = incident.get("recommended_actions", [])
        for i, action in enumerate(actions, 1):
            st.markdown(f'<div class="guidance-step"><b>Step {i}:</b> {action}</div>', unsafe_allow_html=True)
            
        if st.button("🔊 Read Instructions Aloud", use_container_width=True):
            with st.spinner("Generating audio..."):
                speech_content = f"{calm_msg if calm_msg else ''}. Here are your steps: " + " ".join(get_safe_actions(actions))
                audio_bytes = text_to_speech(speech_content, output_file=tempfile.mktemp(suffix=".mp3"))
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                else:
                    st.info("Audio playback is unavailable in this environment, but the safety steps are shown above.")

        if incident.get("hazards_detected"):
            st.markdown("### ⚠️ Hazards to Avoid")
            for hazard in incident["hazards_detected"]:
                st.markdown(f'<div class="hazard-warning">🚫 {hazard}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()