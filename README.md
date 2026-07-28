# AuraFit - AI Emergency Response Copilot

An AI-powered emergency response platform designed for disaster zones where connectivity is compromised. AuraFit converts multimodal inputs (photos, voice, text) into structured emergency incident records and provides real-time responder dashboards for optimized triage and resource allocation.

## 🎯 Key Features

- **Multimodal Input**: Photo upload, voice recording (supports multiple languages), and text descriptions
- **Intelligent Triage**: START (Simple Triage and Rapid Treatment) protocol-based incident classification
- **Real-time Responder Dashboard**: Color-coded incident management for emergency teams
- **Offline-Ready Architecture**: Designed for edge deployment with local AI inference
- **Function Calling**: Structured JSON output for reliable data extraction
- **Database Persistence**: SQLite for local incident tracking and analytics

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google API Key (for Gemma API access)
- ~500MB disk space for dependencies

### Installation

1. **Clone and Setup**
```bash
cd aurafit
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Key**
```bash
# Create .env file
echo GOOGLE_API_KEY=your_key_here > .env
```

### Running AuraFit

**Start Victim Interface** (for civilians/volunteers):
```bash
streamlit run victim_interface.py
```

**Start Responder Dashboard** (for emergency managers):
```bash
streamlit run responder_dashboard.py
```

Open in browser:
- Victim Interface: http://localhost:8501
- Responder Dashboard: http://localhost:8502 (in separate terminal)

## 🔧 Using the Gemma API

AuraFit is configured to work with **Google's Gemma models** via the google-genai SDK. The Gemma API provides:

- Open-weight frontier models
- Cost-effective inference
- Function calling support for structured outputs
- Excellent performance on emergency triage tasks

### API Configuration

The application uses the `GemmaAPIProvider` by default. Configure it via:

```bash
# Set in .env
GEMMA_MODEL=gemma-4-26b-a4b-it  # Model selection (recommended)
GOOGLE_API_KEY=xxx              # Your API key
```

### Supported Gemma Models

To use a different Gemma model:
```python
# In your .env
GEMMA_MODEL=gemma-4-26b-a4b-it  # Latest and recommended
GEMMA_MODEL=gemma-3-27b-it      # Gemma 3
GEMMA_MODEL=gemma-2-27b-it      # Gemma 2 Large
```

### Testing the API

```python
from src.core.llm_provider import get_llm_provider

llm = get_llm_provider()
response_text, function_call = llm.analyze_disaster(
    image_bytes=None,
    text_prompt="Person with bleeding arm, building flooding"
)
print(function_call)
```

## 📊 Architecture

```
┌─────────────────────────────────────┐
│   Victim/Responder UI (Streamlit)   │
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │ LLM Provider   │
       │ Abstraction    │
       └───────┬────────┘
               │
       ┌───────┴────────┐
       │                │
   [Gemma API]     [Gemini API]
   (Default)        (Fallback)
       │                │
       └───────┬────────┘
               │
    ┌──────────▼──────────┐
    │ Function Executor   │
    │ (Tool Call Parser)  │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │  SQLite Database    │
    │  (Local Incidents)  │
    └─────────────────────┘
```

## 🗄️ Database Schema

Incidents are stored with the following structure:

```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    incident_type TEXT,              -- FLOOD, BUILDING_COLLAPSE, etc.
    incident_priority TEXT,          -- RED_IMMEDIATE, YELLOW_DELAYED, etc.
    casualty_count_estimate INTEGER,
    hazards_detected TEXT,           -- JSON array
    recommended_actions TEXT,        -- JSON array
    evacuation_required BOOLEAN,
    emergency_services_required TEXT,-- JSON array
    confidence_score REAL,
    location_description TEXT,
    medical_summary TEXT,
    created_at TIMESTAMP,
    status TEXT                      -- OPEN, IN_PROGRESS, RESOLVED
)
```

## 🎙️ Audio Processing

AuraFit supports voice input in multiple languages:

- **Transcription**: Google Speech Recognition (supports Nigerian Pidgin, Hausa, Yoruba, Igbo, English)
- **Text-to-Speech**: pyttsx3 for offline audio guidance
- **Voice Duration**: Supports 30-second submissions

```python
from src.utils.audio_processor import transcribe_audio, text_to_speech

# Transcribe voice
text = transcribe_audio(audio_bytes)

# Generate safety guidance audio
audio = text_to_speech("Move to high ground immediately")
```

## 📸 Image Processing

Images are automatically optimized for API submission:

```python
from src.utils.image_processor import process_uploaded_image

# Compresses to ~85% quality, resizes to max 1024x1024
optimized = process_uploaded_image(image_bytes, max_size=1024)
```

## 🔄 Offline Deployment (Future)

To transition to 100% offline mode with local Gemma 4 inference:

```bash
# 1. Install Ollama
# 2. Download Gemma model
ollama pull gemma:7b-q4

# 3. Run local inference
ollama serve

# 4. Switch environment
export AURAFIT_MODE=OFFLINE
export OLLAMA_ENDPOINT=http://localhost:11434

# 5. The code remains identical - only the LLM provider changes
streamlit run victim_interface.py
```

## 📋 Function Calling Schema

AuraFit uses structured function calling for reliable incident extraction:

```json
{
  "name": "log_disaster_incident",
  "parameters": {
    "incident_type": "FLOOD|BUILDING_COLLAPSE|FIRE_OUTBREAK|...",
    "incident_priority": "RED_IMMEDIATE|YELLOW_DELAYED|GREEN_MINOR|BLACK_EXPECTANT",
    "casualty_count_estimate": 0,
    "hazards_detected": ["SUBMERGED_POWER_LINE", ...],
    "recommended_actions": ["Action 1", ...],
    "evacuation_required": true,
    "emergency_services_required": ["FIRE_SERVICE", ...],
    "confidence_score": 0.95,
    "location_description": "Lagos, Commercial Ave",
    "medical_summary": "3 with bleeding injuries"
  }
}
```

## 🚨 START Triage Priorities

- **RED (Immediate)**: Life-threatening injuries requiring immediate treatment
- **YELLOW (Delayed)**: Moderate injuries that can wait up to 3 hours
- **GREEN (Minor)**: Minor injuries, stable patients
- **BLACK (Expectant)**: Non-survivable injuries or deceased

## 📊 Responder Dashboard Features

- Real-time incident feed with color-coded priorities
- Search and filter by priority, type, or location
- Casualty and evacuation tracking
- Incident analytics (distribution charts, hazard frequency)
- Status management (OPEN → IN_PROGRESS → RESOLVED)
- Export capabilities for post-disaster audits

## 🔐 Data Privacy

- **All incident data stored locally** on device
- **No telemetry or tracking** of emergency submissions
- **No third-party data sharing**
- SQLite database can be backed up or transferred securely

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Required
GOOGLE_API_KEY=your_gemma_api_key

# Optional
AURAFIT_MODE=GEMMA                    # GEMMA or GEMINI
GEMMA_MODEL=gemma-2-9b-it            # Model to use
DATABASE_PATH=data/aurafit.db         # Database location
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR
```

## 📚 Project Structure

```
aurafit/
├── victim_interface.py          # Streamlit UI for civilians
├── responder_dashboard.py       # Dashboard for responders
├── src/
│   ├── core/
│   │   ├── llm_provider.py      # Gemma/Gemini API abstraction
│   │   ├── database.py          # SQLite management
│   │   └── function_executor.py # Tool call parsing & validation
│   └── utils/
│       ├── image_processor.py   # Image optimization
│       └── audio_processor.py   # Speech recognition & TTS
├── data/
│   └── aurafit.db              # SQLite database (created at runtime)
├── requirements.txt            # Python dependencies
└── .env                        # Configuration (create this)
```

## 🧪 Testing

### Test Incident Submission

```python
python -c "
from src.core.llm_provider import get_llm_provider
from src.core.database import AuraFitDatabase

llm = get_llm_provider()
db = AuraFitDatabase()

response, func_call = llm.analyze_disaster(
    image_bytes=None,
    text_prompt='3 people trapped in flood water near the market'
)
print('LLM Response:', response[:100])
print('Function Call:', func_call)

# Save to database
incident_id = db.insert_incident(func_call)
print(f'Stored as incident #{incident_id}')
"
```

## 🤝 Contributing

To extend AuraFit:

1. **Add a new disaster type**: Update `incident_type` enum in `llm_provider.py`
2. **Custom hazard detection**: Extend hazard list in `function_executor.py`
3. **New language support**: Configure in `audio_processor.py`
4. **Custom analytics**: Add queries to `database.py` and charts to `responder_dashboard.py`

## ⚠️ Important Notes

- **API Key Security**: Never commit `.env` files or API keys to version control
- **Latency Expectations**: First requests may take 2-3 seconds due to model initialization
- **Image Quality**: Clear, well-lit photos improve hazard detection accuracy
- **Audio Quality**: Speak clearly; background noise may affect transcription
- **Network Independence**: Switch to offline mode when internet unavailable

## 📞 Support & Documentation

- **Gemma API Docs**: https://ai.google.dev/gemma
- **Streamlit Docs**: https://docs.streamlit.io
- **START Protocol**: https://en.wikipedia.org/wiki/START_triage

## 📄 License

This project is built for the Gemma Hackathon and is provided as-is for emergency response demonstration.

---

**Built with ❤️ for emergency resilience in underserved regions**
