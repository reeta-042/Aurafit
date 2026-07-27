# 🚀 AuraFit Developer Reference Card

## Quick Commands

```bash
# Setup
python install.py              # Interactive setup
pip install -r requirements.txt # Manual install
python setup.py                # Validate installation

# Testing
python test_suite.py           # Run tests

# Running
streamlit run victim_interface.py      # Citizen UI (port 8501)
streamlit run responder_dashboard.py   # Manager UI (port 8502)

# Database
sqlite3 data/aurafit.db        # Direct DB access
```

---

## Key Files

| File | Purpose |
|------|---------|
| `victim_interface.py` | Citizen emergency input UI |
| `responder_dashboard.py` | Manager incident dashboard |
| `src/core/llm_provider.py` | AI API abstraction |
| `src/core/database.py` | SQLite operations |
| `src/core/function_executor.py` | JSON validation |
| `.env.example` | Configuration template |

---

## Environment Variables

```bash
GOOGLE_API_KEY=your_key             # Required
GEMMA_MODEL=gemma-4-26b-a4b-it      # Model name (recommended)
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
```

---

## API Usage

```python
from src.core.llm_provider import get_llm_provider

llm = get_llm_provider()
response_text, function_call = llm.analyze_disaster(
    image_bytes=None,
    text_prompt="3 people trapped",
    audio_text="Spoken description"
)

# function_call contains:
{
    "incident_type": "BUILDING_COLLAPSE",
    "incident_priority": "RED_IMMEDIATE",
    "casualty_count_estimate": 3,
    "hazards_detected": ["UNSTABLE_STRUCTURE"],
    "recommended_actions": ["Move away"],
    "evacuation_required": true,
    "emergency_services_required": ["FIRE_SERVICE"],
    "confidence_score": 0.9,
    "location_description": "Market area",
    "medical_summary": "3 trapped"
}
```

---

## Database Usage

```python
from src.core.database import AuraFitDatabase

db = AuraFitDatabase()

# Insert
incident_id = db.insert_incident(incident_data)

# Retrieve
all_incidents = db.get_all_incidents()
red_incidents = db.get_incidents_by_priority("RED_IMMEDIATE")
flood_incidents = db.get_incidents_by_type("FLOOD")
search_results = db.search_incidents("Lagos")

# Analytics
stats = db.get_incident_analytics()
# Returns: {
#   "total_incidents": 42,
#   "priority_distribution": {"RED_IMMEDIATE": 8, ...},
#   "type_distribution": {"FLOOD": 5, ...},
#   "total_casualties": 23,
#   "evacuation_required": 19
# }

# Update
db.update_incident_status(incident_id, "IN_PROGRESS")
```

---

## Function Executor

```python
from src.core.function_executor import FunctionExecutor

# Validate and execute function call
validated_data = FunctionExecutor.validate_and_execute(raw_data)

# Returns validated incident dict or fallback if validation fails
# Always returns valid data (never throws)
```

---

## Image Processing

```python
from src.utils.image_processor import (
    process_uploaded_image,
    validate_image,
    get_image_dimensions
)

# Validate
if validate_image(image_bytes):
    # Process (resize, compress, optimize)
    optimized = process_uploaded_image(image_bytes)
    
    # Get dimensions
    width, height = get_image_dimensions(image_bytes)
```

---

## Audio Processing

```python
from src.utils.audio_processor import (
    transcribe_audio,
    text_to_speech,
    validate_audio
)

# Transcribe
text = transcribe_audio(audio_bytes)

# Generate audio
audio_bytes = text_to_speech("Move to safety", "output.mp3")

# Validate
if validate_audio(audio_bytes):
    # Process audio
    pass
```

---

## Enum Values

### Incident Types
```python
FLOOD, BUILDING_COLLAPSE, FIRE_OUTBREAK, ROAD_ACCIDENT,
GAS_EXPLOSION, LANDSLIDE, STORM_DAMAGE, MEDICAL_EMERGENCY,
OTHER
```

### Priorities
```python
RED_IMMEDIATE, YELLOW_DELAYED, GREEN_MINOR, BLACK_EXPECTANT
```

### Common Hazards
```python
SUBMERGED_POWER_LINE, GAS_LEAK, UNSTABLE_STRUCTURE,
CHEMICAL_SPILL, RAGING_FIRE, DEBRIS, FLOODING,
ELECTRICAL_HAZARD, CRUSH_HAZARD, CONTAMINATED_WATER
```

---

## Streamlit Components

### Input
```python
uploaded_image = st.file_uploader("Upload photo", type=["jpg", "png"])
audio_file = st.file_uploader("Upload audio", type=["wav", "mp3"])
text_input = st.text_area("Description", height=150)
button_clicked = st.button("Submit", type="primary")
```

### Display
```python
st.success("✅ Incident stored")
st.error("❌ Error occurred")
st.warning("⚠️ Warning message")
st.info("ℹ️ Info message")

st.markdown("<div>HTML content</div>", unsafe_allow_html=True)
st.dataframe(df)
col1, col2 = st.columns(2)
```

### Charts
```python
import plotly.express as px
fig = px.pie(df, values='count', names='priority')
st.plotly_chart(fig)
```

---

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: streamlit` | `pip install -r requirements.txt` |
| `GOOGLE_API_KEY not set` | Set in `.env` file |
| `Port 8501 already in use` | Use different port: `--server.port 8502` |
| `Invalid image` | Check format (JPG, PNG) and size |
| `API timeout` | Try again; check internet |
| `Database locked` | Close other connections |
| `Audio too quiet` | Speak louder; check microphone |

---

## Performance Tips

| Optimization | Impact |
|-------------|--------|
| Image size <1MB | Faster API calls |
| Audio <30sec | Faster transcription |
| Cached DB queries | 10x faster retrieval |
| Indexed tables | 100x faster on large DB |
| Compression 85% | 70% file size reduction |

---

## Deployment Checklist

- [ ] `.env` configured with API key
- [ ] `requirements.txt` installed
- [ ] Test suite passes
- [ ] Both UIs launch
- [ ] Sample submission works
- [ ] Dashboard shows incidents
- [ ] Database persists data
- [ ] Ready for production

---

## Offline Migration Checklist

- [ ] Install Ollama
- [ ] Download Gemma model: `ollama pull gemma:7b-q4`
- [ ] Start Ollama: `ollama serve`
- [ ] Update `.env`: `AURAFIT_MODE=OFFLINE`
- [ ] No code changes needed
- [ ] Test with internet disabled
- [ ] Deploy to edge device

---

## Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Access session state (Streamlit)
print(st.session_state)

# Check database directly
sqlite3 data/aurafit.db
SELECT * FROM incidents LIMIT 5;

# Monitor API calls
import json
print(json.dumps(function_call, indent=2))
```

---

## File Paths

| Path | Purpose |
|------|---------|
| `data/aurafit.db` | SQLite database |
| `.env` | Configuration |
| `logs/` | Application logs |
| `venv/` | Virtual environment |
| `src/core/` | Core logic |
| `src/utils/` | Helper functions |

---

## HTTP Endpoints (Future)

```
POST /submit-emergency    # New incident
GET  /incidents           # List incidents
GET  /incidents/<id>      # Get incident
PUT  /incidents/<id>      # Update incident
GET  /analytics           # Get stats
```

---

## Database Queries

```sql
-- Most recent incidents
SELECT * FROM incidents ORDER BY created_at DESC LIMIT 10;

-- RED incidents
SELECT * FROM incidents WHERE incident_priority='RED_IMMEDIATE' AND status='OPEN';

-- Count by priority
SELECT incident_priority, COUNT(*) FROM incidents GROUP BY incident_priority;

-- Total casualties
SELECT SUM(casualty_count_estimate) FROM incidents WHERE status='OPEN';

-- Search location
SELECT * FROM incidents WHERE location_description LIKE '%Lagos%';
```

---

## Code Style

```python
# Imports
from typing import Optional, Dict, Any
import logging

# Constants
MAX_IMAGE_SIZE = 1024
DEFAULT_PRIORITY = "YELLOW_DELAYED"

# Functions
def process_data(input_dict: Dict[str, Any]) -> Optional[Dict]:
    """Process data with validation"""
    try:
        # Logic
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

# Classes
class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
```

---

## Resources

- 📖 README.md - Features & usage
- 🚀 QUICKSTART.md - 5-min setup
- 📦 DEPLOYMENT.md - Deployment guide
- 🏗️ ARCHITECTURE.md - Technical details
- ✅ BUILD_CHECKLIST.md - Quality checklist
- 🔗 https://ai.google.dev - Gemma API docs
- 📚 https://docs.streamlit.io - Streamlit docs

---

## Support

1. Check the documentation first (README.md)
2. Run test suite (`python test_suite.py`)
3. Check logs for error details
4. Review ARCHITECTURE.md for design
5. Contact team with specific error message

---

**Quick Reference v1.0**  
Last Updated: 2026-07-26  
Status: ✅ Ready for Use
