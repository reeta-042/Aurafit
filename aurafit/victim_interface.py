"""
Victim/Citizen Interface for AuraFit
Multimodal input (photo, voice, text) for emergency guidance
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import streamlit as st
import os
import sys
import logging
from io import BytesIO
import tempfile

# Add src to path
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if "incident_data" not in st.session_state:
    st.session_state.incident_data = None
if "guidance_generated" not in st.session_state:
    st.session_state.guidance_generated = False
if "audio_output" not in st.session_state:
    st.session_state.audio_output = None

# Set page config
st.set_page_config(
    page_title="AuraFit - Emergency Response",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for emergency visibility
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .emergency-banner {
        background-color: #ff4444;
        color: white;
        padding: 20px;
        border-radius: 10px;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .guidance-box {
        background-color: #2d5016;
        border-left: 5px solid #00ff00;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 16px;
    }
    .hazard-warning {
        background-color: #5c1a1a;
        border-left: 5px solid #ff6666;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-size: 14px;
    }
    .priority-red {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_llm_provider():
    return get_llm_provider()

@st.cache_resource
def init_database():
    return AuraFitDatabase("data/aurafit.db")

llm_provider = init_llm_provider()
db = init_database()

# Main UI
def main():
    st.markdown("""
    <div class="emergency-banner">
    🚨 AURAFIT - AI Emergency Response Copilot 🚨
    </div>
    """, unsafe_allow_html=True)
    
    st.write("*Submit emergency information for immediate guidance and hazard assessment*")
    
    # Sidebar or top controls for language configuration
    st.markdown("### 🌐 Language & Communication Settings")
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        communication_language = st.selectbox(
            "Language you are typing/speaking in:",
            ["Nigerian Pidgin", "English", "Yoruba", "Hausa", "Igbo", "Other Ethnic Dialect"],
            index=0,
            help="Select the language or dialect of your text or voice input"
        )
    with lang_col2:
        response_language = st.selectbox(
            "Preferred response & safety guidance language:",
            ["Nigerian Pidgin", "English", "Yoruba", "Hausa", "Igbo"],
            index=0,
            help="Gemma 4 will generate safety guidance in this language"
        )
    
    # Create tabs
    input_tab, guidance_tab = st.tabs(["📥 Submit Emergency", "🆘 Safety Guidance"])
    
    with input_tab:
        st.subheader("Describe Your Emergency Situation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Photo of Scene (Optional)")
            photo_mode = st.radio(
                "Select photo input method:",
                ["📷 Live Camera Capture", "📁 Upload Image File"],
                horizontal=True
            )
            
            image_raw_bytes = None
            if photo_mode == "📷 Live Camera Capture":
                camera_photo = st.camera_input("Take a live photo of the emergency scene")
                if camera_photo:
                    image_raw_bytes = camera_photo.getvalue()
                    st.success("✅ Camera photo captured")
            else:
                uploaded_image = st.file_uploader(
                    "Upload a photo of the emergency scene",
                    type=["jpg", "jpeg", "png"],
                    help="Clear photos help with hazard identification"
                )
                if uploaded_image:
                    image_raw_bytes = uploaded_image.read()
                    st.image(image_raw_bytes, use_container_width=True, caption="Uploaded Scene Photo")
        
        with col2:
            st.write("### Voice Description (Optional)")
            
            st.info("🎤 Click the microphone button to record your voice")
            
            # Use native audio input for direct microphone recording
            audio_data = st.audio_input(
                "Record your voice description",
                help="Speak in any language you're comfortable with. Describe: who, what, where, how many injured"
            )
        
        st.write("### Text Description")
        text_placeholder = "Write inside Nigerian Pidgin, Yoruba, English or your language. E.g., 'Water don flood my compound for Commercial Ave, 3 people dey trapped upstairs...'" if communication_language == "Nigerian Pidgin" else "Describe what's happening (location, injuries, hazards, etc.)"
        text_input = st.text_area(
            f"Describe what's happening (in {communication_language}):",
            height=130,
            placeholder=text_placeholder
        )

        st.write("### 📍 Share Location & GPS (Optional for Responders)")
        st.caption("Sharing your exact location helps emergency teams (NEMA/SEMA) reach you faster!")
        
        geo_location = None
        if streamlit_geolocation:
            st.write("📍 **Click the button below to request & share browser geolocation permission:**")
            geo_location = streamlit_geolocation()
            if geo_location and geo_location.get("latitude") is not None and geo_location.get("longitude") is not None:
                st.success(f"✅ GPS Coordinates Captured: Lat {geo_location['latitude']:.6f}, Lon {geo_location['longitude']:.6f}")

        loc_col1, loc_col2 = st.columns(2)
        with loc_col1:
            default_lat = float(geo_location["latitude"]) if (geo_location and geo_location.get("latitude") is not None) else 0.0
            lat_input = st.number_input("Latitude", value=default_lat, format="%.6f", help="e.g. 6.524400 (Lagos), 9.076500 (Abuja)")
        with loc_col2:
            default_lon = float(geo_location["longitude"]) if (geo_location and geo_location.get("longitude") is not None) else 0.0
            lon_input = st.number_input("Longitude", value=default_lon, format="%.6f", help="e.g. 3.379200 (Lagos), 7.398600 (Abuja)")
        
        landmark_input = st.text_input("Landmark / Street Address", placeholder="e.g. Near Central Market, Commercial Ave, Ikeja...")
        
        # Submit button
        if st.button("🚨 Submit Emergency Report", use_container_width=True, type="primary"):
            if not text_input.strip() and not audio_data and not image_raw_bytes:
                st.error("Please provide at least a text description, voice recording, or photo of the emergency")
            else:
                with st.spinner("🔄 Analyzing emergency... Please wait"):
                    try:
                        # Process inputs
                        image_bytes = None
                        if image_raw_bytes:
                            if validate_image(image_raw_bytes):
                                image_bytes = process_uploaded_image(image_raw_bytes)
                                st.success("✅ Photo processed for hazard analysis")
                            else:
                                st.warning("⚠️ Photo validation failed, proceeding without image")
                        
                        audio_text = None
                        if audio_data:
                            # st.audio_input returns bytes directly
                            audio_text = transcribe_audio(audio_data)
                            if audio_text:
                                st.success(f"✅ Audio transcribed: {audio_text[:50]}...")
                            else:
                                st.warning("⚠️ Could not transcribe audio, proceeding with text")
                        
                        # Prepare location string
                        gps_str = None
                        if lat_input != 0.0 or lon_input != 0.0:
                            gps_str = f"{lat_input:.5f}, {lon_input:.5f}"

                        # Create analysis prompt
                        analysis_prompt = f"""Victim Report:
Text Description: {text_input or 'None provided'}
Landmark/Address: {landmark_input or 'Not provided'}
GPS Coordinates: {gps_str or 'Not provided'}
Communication Language: {communication_language}
Target Guidance Language: {response_language}

Analyze the emergency, assess hazards, assign START triage priority, determine location and casualty estimates, and generate a calm reassuring message and safety steps in {response_language}."""
                        
                        # Call Gemma LLM Provider
                        response_text, function_call_data = llm_provider.analyze_disaster(
                            image_bytes=image_bytes,
                            text_prompt=analysis_prompt,
                            audio_text=audio_text,
                            communication_language=communication_language,
                            response_language=response_language
                        )
                        
                        # Parse function call or JSON text response
                        incident_data = parse_function_call(response_text, function_call_data)
                        
                        if incident_data:
                            # Add language & location metadata to incident record
                            incident_data["communication_language"] = communication_language
                            if lat_input != 0.0:
                                incident_data["latitude"] = lat_input
                            if lon_input != 0.0:
                                incident_data["longitude"] = lon_input
                            if gps_str:
                                incident_data["gps_coordinates"] = gps_str
                            if landmark_input:
                                incident_data["location_description"] = f"{landmark_input} ({incident_data.get('location_description', '')})"
                            
                            # Store incident in database
                            incident_id = db.insert_incident(incident_data)
                            st.session_state.incident_data = incident_data
                            st.session_state.guidance_generated = True
                            
                            st.success(f"✅ Emergency report #{incident_id} received and recorded")
                            st.rerun()
                        else:
                            st.error("Failed to analyze emergency report")
                            
                    except Exception as e:
                        logger.error(f"Error processing emergency: {e}")
                        st.error(f"Error: {str(e)}")
    
    with guidance_tab:
        if st.session_state.guidance_generated and st.session_state.incident_data:
            incident = st.session_state.incident_data
            
            # Priority indicator
            priority_color_map = {
                "RED_IMMEDIATE": "#ff4444",
                "YELLOW_DELAYED": "#ffaa00",
                "GREEN_MINOR": "#00aa00",
                "BLACK_EXPECTANT": "#666666"
            }
            
            priority = incident.get("incident_priority", "YELLOW_DELAYED")
            priority_label = priority.replace("_", " ")
            
            st.markdown(f"""
            <div class="priority-red" style="background-color: {priority_color_map.get(priority, '#ffaa00')}">
            TRIAGE LEVEL: {priority_label}
            </div>
            """, unsafe_allow_html=True)
            
            # Reassuring Calm Response Section for Victim
            calm_msg = incident.get("victim_calm_response")
            if calm_msg:
                st.markdown(f"""
                <div style="background-color: #1b382b; border-left: 6px solid #00ff88; padding: 18px; margin: 15px 0; border-radius: 8px;">
                    <h3 style="margin-top:0; color: #00ff88;">💚 Calm Guidance from AuraFit Copilot</h3>
                    <p style="font-size: 18px; line-height: 1.6; color: #ffffff;">{calm_msg}</p>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Incident Type:** {incident.get('incident_type', 'Unknown')}")
                st.write(f"**Confidence:** {incident.get('confidence_score', 0):.0%}")
                st.write(f"**Estimated Casualties:** {incident.get('casualty_count_estimate', 0)}")
            
            with col2:
                st.write(f"**Location:** {incident.get('location_description', 'Unknown')}")
                gps_coords = incident.get("gps_coordinates")
                if gps_coords:
                    st.write(f"**📍 Shared GPS:** `{gps_coords}`")
                st.write(f"**Evacuation Required:** {'✅ YES' if incident.get('evacuation_required') else '❌ No'}")
            
            # Hazards section
            if incident.get("hazards_detected"):
                st.write("### ⚠️ Identified Hazards")
                for hazard in incident["hazards_detected"]:
                    st.markdown(f'<div class="hazard-warning">🚫 {hazard}</div>', unsafe_allow_html=True)
            
            # Medical summary
            if incident.get("medical_summary"):
                st.write("### 🏥 Medical Assessment")
                st.write(incident["medical_summary"])
            
            # Immediate actions
            st.write("### 🆘 Immediate Actions to Take")
            
            actions = incident.get("recommended_actions", [])
            
            for i, action in enumerate(actions, 1):
                st.markdown(f'<div class="guidance-box">✓ Step {i}: {action}</div>', unsafe_allow_html=True)
            
            # TTS for guidance
            if st.button("🔊 Play Safety Guidance Audio", use_container_width=True):
                with st.spinner("Generating audio guidance..."):
                    safe_actions = get_safe_actions(actions)
                    speech_content = f"{calm_msg if calm_msg else ''}. Step-by-step guidance: " + " ".join(safe_actions)
                    
                    audio_bytes = text_to_speech(speech_content, output_file=tempfile.mktemp(suffix=".mp3"))
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        st.success("✅ Audio guidance ready")
                    else:
                        st.warning("Could not generate audio, please read the guidance above")
            
            # Emergency services
            if incident.get("emergency_services_required"):
                st.write("### 🚑 Required Emergency Services")
                for service in incident["emergency_services_required"]:
                    st.write(f"- {service}")
            
            # Reset button
            if st.button("📝 Submit Another Report", use_container_width=True):
                st.session_state.incident_data = None
                st.session_state.guidance_generated = False
                st.rerun()
        
        else:
            st.info("👈 Submit an emergency report on the left to receive safety guidance")


if __name__ == "__main__":
    main()
