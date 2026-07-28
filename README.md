# C.A.R.S.: Crisis AI Response System

C.A.R.S. is a multimodal AI copilot engineered for crisis environments. It bridges the gap between distressed citizens and emergency dispatchers by converting zero-typing inputs (voice, local dialect, photos) into structured, START-protocol triage data using Google's Gemma models.

Built for the GDG UNN "Build with Gemma" Hackathon.

## System Architecture

C.A.R.S. operates on a dual-interface architecture:

1. **Victim Interface ("Panic Mode"):** A frictionless, web-based capture portal. Users upload a scene photo and a voice note in their native language (English, Pidgin, Hausa, Yoruba, Igbo). 
2. **Responder Dashboard:** A high-contrast, centralized GIS command center. It pulls structured incident reports from the database and ranks them by AI-assigned triage priority.

**Tech Stack:** Python 3.12 | Streamlit | SQLite | Google GenAI SDK (Gemma 4) | Plotly

## The Gemma Implementation

Instead of relying on standard text generation, C.A.R.S. leverages **Gemma 4 (gemma-4-26b-a4b-it)** strictly for **multimodal function calling**. 

The model ingests raw audio transcripts and scene imagery, and is forced to output a strict JSON schema defining:
- `incident_type` (e.g., FIRE_OUTBREAK, STRUCTURAL_COLLAPSE)
- `triage_priority` (🔴 CRITICAL, 🟡 DELAYED, 🟢 MINOR, ⚫ EXPECTANT)
- `casualty_count_estimate`
- `hazards_detected`

This structured data is instantly committed to a local SQLite database, allowing the Responder Dashboard to query, filter, and map incidents without parsing raw text.

## Repository Structure

```text
├── src/
│   ├── core/
│   │   ├── llm_provider.py      # Gemma API orchestration & tool definitions
│   │   ├── database.py          # SQLite connection and schema management
│   │   └── function_executor.py # JSON validation and parser
│   ├── utils/
│   │   ├── image_processor.py   # Pillow-based image optimization
│   │   └── audio_processor.py   # Dialect transcription logic
│   └── __init__.py
├── .env.example                 # Template for required environment variables
├── .gitignore                   # Excludes venv/ and local database files
├── requirements.txt             # Locked dependencies
├── responder_dashboard.py       # Entry point: Dispatcher UI
└── victim_interface.py          # Entry point: Citizen UI
```
*(Note: The local `cars.db` SQLite file is generated dynamically at runtime and intentionally excluded from version control).*

## Local Development Setup

**1. Clone the repository**
```bash
git clone [https://github.com/YourUsername/CARS-Deploy.git](https://github.com/YourUsername/CARS-Deploy.git)
cd CARS-Deploy
```

**2. Initialize the Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate # macOS/Linux
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables**
Copy the `.env.example` file to a new file named `.env` and inject your Google API key:
```env
GOOGLE_API_KEY=your_actual_key_here
GEMMA_MODEL=gemma-4-26b-a4b-it
```

**5. Launch the Infrastructure**
You must run both interfaces on separate local ports. Open two terminal tabs (ensure the `venv` is active in both) and run:

```bash
# Terminal 1:
streamlit run victim_interface.py

# Terminal 2:
streamlit run responder_dashboard.py
```

## Future Roadmap: Edge Deployment
While this MVP relies on Streamlit Cloud and the Gemma API, the architecture is designed to transition to offline edge inference. Future iterations will utilize WebLLM and a quantized Gemma model running directly on responder hardware to ensure operability during telecommunication blackouts.