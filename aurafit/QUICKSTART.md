# 🚀 AuraFit Quick Start Guide

## ⚡ 5-Minute Setup

### 1️⃣ Get Your API Key

Visit [Google AI Studio](https://ai.google.dev) and:
1. Sign in with your Google account
2. Click "Get API Key"
3. Create a new project or use existing
4. Copy your API key

### 2️⃣ Clone Configuration

```bash
cd aurafit

# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

Your `.env` should look like:
```
GOOGLE_API_KEY=sk-xxxxx-your-actual-key-xxxxx
GEMMA_MODEL=gemma-4-26b-a4b-it
```

### 3️⃣ Install & Run

```bash
# Install dependencies (one time)
pip install -r requirements.txt

# Verify setup
python setup.py

# Terminal 1: Run victim interface
streamlit run victim_interface.py

# Terminal 2: Run responder dashboard
streamlit run responder_dashboard.py
```

That's it! 🎉

---

## 🎯 Using AuraFit

### Victim Interface (Port 8501)

1. **Upload Emergency Photo** (optional)
   - Building collapse, flooding, fire, etc.
   - Automatically optimized for API

2. **Record Audio** (optional)
   - Speak freely in any language
   - Describe: "Who, What, Where, How many injured"

3. **Type Description** (required)
   - "3 people trapped in flooded house near market"
   - Clear, concise information

4. **Submit** and get:
   - ✅ Safety instructions (step-by-step)
   - ⚠️ Hazard warnings
   - 🚑 Emergency services needed
   - 🔊 Audio guidance (optional)

### Responder Dashboard (Port 8502)

1. **View Summary Metrics**
   - Total incidents, RED alerts, casualties
   - Evacuation requirements

2. **Filter & Search**
   - By priority level (RED/YELLOW/GREEN)
   - By incident type (flood, collapse, etc.)
   - By location keyword

3. **Manage Incidents**
   - View full details and photo
   - Mark as "In Progress"
   - Mark as "Resolved"

4. **Analytics**
   - Pie chart of priorities
   - Bar chart of incident types
   - Casualty tracking

---

## 🧪 Test Without API Key

To test locally first:

```bash
# Run test suite (doesn't require API key)
python test_suite.py
```

You'll see:
- ✅ Database operations
- ✅ Function parsing
- ✅ Image processing
- ⚠️ LLM Provider (expected to fail without key)

---

## 📊 What Happens Behind the Scenes

1. **User Submits Report** → Victim Interface
2. **Image Optimized** → 1024x1024 max, 85% quality
3. **Audio Transcribed** → Google Speech Recognition
4. **Sent to Gemma API** → AI analysis with function calling
5. **Structured JSON Extracted** → incident_type, priority, hazards, actions
6. **Stored in SQLite** → Local database
7. **Dashboard Updates** → Real-time incident display
8. **Safety Guidance Rendered** → User sees actions
9. **Audio Generated** → pyttsx3 text-to-speech

---

## 🔧 Troubleshooting

### "Invalid API Key"
- Check `.env` file exists
- Verify key format (should be ~40 chars)
- Try again with correct key

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "Port 8501 already in use"
```bash
# Use different port
streamlit run victim_interface.py --server.port 8502
```

### "Audio transcription not working"
- Requires internet connection (for Google Speech API)
- Check audio file format (WAV, MP3)
- Ensure clear audio (not too quiet)

### "Image processing slow"
- Images are optimized automatically
- Large photos may take 1-2 seconds
- Compression ratio: ~70% file size reduction

---

## 🌍 Offline Mode (Future)

When you have Gemma 4 running locally:

```bash
# 1. Install Ollama from ollama.ai
# 2. Download Gemma
ollama pull gemma:7b-q4

# 3. Start Ollama in another terminal
ollama serve

# 4. Update .env
AURAFIT_MODE=OFFLINE
OLLAMA_ENDPOINT=http://localhost:11434

# 5. No internet needed - everything runs locally!
streamlit run victim_interface.py
```

---

## 💾 Database Location

Incidents are stored in:
```
data/aurafit.db
```

To backup:
```bash
cp data/aurafit.db data/aurafit_backup.db
```

To clear (testing):
```bash
rm data/aurafit.db
```

---

## 📞 Emergency Information

### START Triage Colors
- 🔴 **RED** - Immediate life threat → Treat first
- 🟡 **YELLOW** - Serious but stable → Wait up to 3 hours
- 🟢 **GREEN** - Minor injuries → Self-care
- ⚫ **BLACK** - Non-salvageable → Comfort care

### Typical Incident Types
- FLOOD / BUILDING_COLLAPSE / FIRE_OUTBREAK
- ROAD_ACCIDENT / GAS_EXPLOSION / LANDSLIDE
- STORM_DAMAGE / MEDICAL_EMERGENCY / OTHER

### Common Hazards
- SUBMERGED_POWER_LINE / GAS_LEAK / UNSTABLE_STRUCTURE
- CHEMICAL_SPILL / RAGING_FIRE / DEBRIS / FLOODING
- ELECTRICAL_HAZARD / CRUSH_HAZARD

---

## ✅ Checklist Before Going Live

- [ ] API key working
- [ ] Both interfaces launch without errors
- [ ] Can upload photo without crashes
- [ ] Can type description and submit
- [ ] Database stores incidents
- [ ] Responder dashboard shows incidents
- [ ] Can filter and search
- [ ] Audio output works (optional)

---

## 📈 Performance Expectations

| Operation | Time |
|-----------|------|
| API call (first) | 2-3 seconds |
| API call (cached) | 1-2 seconds |
| Image optimization | 0.5 seconds |
| Database insert | <100ms |
| Dashboard refresh | <500ms |
| Audio generation | 1-2 seconds |

---

## 🎓 Learn More

- [Gemma API Docs](https://ai.google.dev/gemma)
- [Streamlit Docs](https://docs.streamlit.io)
- [START Triage](https://en.wikipedia.org/wiki/START_triage)
- [Emergency Response](https://www.nema.gov.ng/)

---

**Questions?** Check the main [README.md](README.md) for full documentation.

**Ready?** Run `streamlit run victim_interface.py` 🚀
