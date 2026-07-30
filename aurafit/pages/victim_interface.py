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

#sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..',..'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

st.set_page_config(
    page_title="C.A.R.S.: Crisis AI Response System",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #202124; }
    .material-card { background-color: #ffffff; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 24px; border: 1px solid #e8eaed; }
    .emergency-banner { background-color: #d93025; color: white; padding: 16px; border-radius: 12px; font-size: 22px; font-weight: 600; text-align: center; margin-bottom: 24px; box-shadow: 0 4px 6px rgba(217, 48, 37, 0.2); }
    .guidance-step { background-color: #e6f4ea; border-left: 6px solid #1e8e3e; padding: 16px; margin: 12px 0; border-radius: 8px; color: #137333; font-size: 16px; font-weight: 500; }
    .hazard-warning { background-color: #fce8e6; border-left: 6px solid #d93025; padding: 16px; margin: 12px 0; border-radius: 8px; color: #c5221f; font-size: 15px; font-weight: 500; }
    .triage-tag { color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stAudioInput"] { background-color: #fce8e6; padding: 10px; border-radius: 10px; border: 2px dashed #d93025; }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_llm_provider():
    return get_llm_provider()

@st.cache_resource
def init_database():
    return AuraFitDatabase("data/aurafit.db")

llm_provider = init_llm_provider()
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
            photo_mode = st.radio("Choose input method:", ["📸 Camera", "📁 Gallery"], horizontal=True, label_visibility="collapsed")
            image_raw_bytes = None
            if photo_mode == "📸 Camera":
                camera_photo = st.camera_input("Capture scene", label_visibility="collapsed")
                if camera_photo: image_raw_bytes = camera_photo.getvalue()
            else:
                uploaded_image = st.file_uploader("Select an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
                if uploaded_image: 
                    image_raw_bytes = uploaded_image.read()
                    st.image(image_raw_bytes, use_container_width=True)

        # 3. Location Auto-Grab
        geo_location = None
        if streamlit_geolocation:
            geo_location = streamlit_geolocation()
            
        # Hidden Text Input (Removed the Syntax Error here)
        with st.expander("📝 I cannot speak (Type instead)"):
            text_input = st.text_area("Describe the emergency:", height=100)
            landmark_input = st.text_input("Nearby Landmark:")

        st.write("")
        
        if st.button("🚨 GET IMMEDIATE HELP", use_container_width=True, type="primary"):
            if not image_raw_bytes:
                st.error("⚠️ We need a photo to assess hazards. Please take or upload a photo.")
            else:
                with st.spinner("🔄 C.A.R.S is analyzing the scene..."):
                    try:
                        image_bytes = process_uploaded_image(image_raw_bytes) if validate_image(image_raw_bytes) else None
                        audio_text = transcribe_audio(audio_data) if audio_data else None

                        gps_str = f"{geo_location['latitude']:.5f}, {geo_location['longitude']:.5f}" if geo_location and geo_location.get("latitude") else None

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
                            if gps_str: incident_data["gps_coordinates"] = gps_str
                            if landmark_input: incident_data["location_description"] = landmark_input
                            
                            db.insert_incident(incident_data)
                            st.session_state.incident_data = incident_data
                            st.session_state.guidance_generated = True
                            st.rerun()
                        else:
                            st.error("Failed to analyze. Please try again.")
                            
                    except Exception as e:
                        logger.error(f"Error: {e}")
                        st.error("System error. Please try again.")

    else:
        incident = st.session_state.incident_data
        
        if st.button("← Submit Another Report", use_container_width=True):
            st.session_state.guidance_generated = False
            st.session_state.incident_data = None
            st.rerun()

        priority_color_map = {
            "RED_IMMEDIATE": "#d93025", "YELLOW_DELAYED": "#f29900", 
            "GREEN_MINOR": "#1e8e3e", "BLACK_EXPECTANT": "#202124"
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
            <div style="background-color: #e8f0fe; border-left: 6px solid #1a73e8; padding: 20px; margin: 20px 0; border-radius: 8px;">
                <h3 style="margin-top:0; color: #1967d2;">🛡️ Message from C.A.R.S</h3>
                <p style="font-size: 18px; line-height: 1.5; color: #202124; margin-bottom: 0;">{calm_msg}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Step-by-Step Safety Guide")
        actions = incident.get("recommended_actions", [])
        for i, action in enumerate(actions, 1):
            st.markdown(f'<div class="guidance-step"><b>Step {i}:</b> {action}</div>', unsafe_allow_html=True)
            
        #if st.button("🔊 Read Instructions Aloud", use_container_width=True):
            #with st.spinner("Generating audio..."):
                #speech_content = f"{calm_msg if calm_msg else ''}. Here are your steps: " + " ".join(get_safe_actions(actions))
               # audio_bytes = text_to_speech(speech_content, output_file=tempfile.mktemp(suffix=".mp3"))
                #if audio_bytes:
                  #  st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        if st.button("🔊 Read Instructions Aloud", use_container_width=True):
            with st.spinner("Generating audio..."):
                speech_content = f"{calm_msg if calm_msg else ''}. Here are your steps: " + " ".join(get_safe_actions(actions))
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    temp_audio_path = tmp_file.name
                result = text_to_speech(speech_content, output_file=temp_audio_path)
                if result and os.path.exists(temp_audio_path):
                    st.audio(temp_audio_path, format="audio/mp3", autoplay=True)
                else:
                    st.error("Could not generate audio output.")

        if incident.get("hazards_detected"):
            st.markdown("### ⚠️ Hazards to Avoid")
            for hazard in incident["hazards_detected"]:
                st.markdown(f'<div class="hazard-warning">🚫 {hazard}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
