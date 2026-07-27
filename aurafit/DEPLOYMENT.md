# AuraFit Deployment & Architecture Guide

## 🏗️ System Architecture

### MVP Architecture (Current - Gemma API)

```
┌──────────────────────────────────────────────────┐
│           User Interfaces (Streamlit)            │
│  ┌────────────────────────────────────────────┐  │
│  │  Victim Interface    │  Responder Dashboard│  │
│  │  (Photo/Voice/Text)  │  (Analytics/Triage) │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
                           │
         ┌─────────────────┴──────────────────┐
         │                                    │
    ┌────▼──────────────┐        ┌──────────▼────┐
    │  Image Processor  │        │ Audio Processor│
    │  (Pillow/OpenCV)  │        │ (Speech-to-Text│
    │  Max 1024x1024    │        │  + pyttsx3 TTS)│
    │  85% quality      │        └────────────────┘
    └────┬──────────────┘
         │
    ┌────▼────────────────────────┐
    │  LLM Provider - Gemma API    │
    │  (google-genai SDK)          │
    │                              │
    │  ┌──────────────────────┐    │
    │  │ GemmaAPIProvider     │◄───┼─── Uses Gemma models
    │  │ (Primary Engine)     │    │    (gemma-4-26b, etc.)
    │  └──────────────────────┘    │
    └────┬─────────────────────────┘
         │
         │ Function Call Parameters (JSON)
         ▼
    ┌────────────────────────────┐
    │  Function Executor         │
    │  (Tool Call Parser)        │
    │                            │
    │  - Validates schema        │
    │  - Normalizes data         │
    │  - Fallback handling       │
    └────┬───────────────────────┘
         │
         │ Structured Incident Data
         ▼
    ┌────────────────────────────┐
    │  SQLite Database           │
    │  (Local Persistence)       │
    │                            │
    │  Stores:                   │
    │  - Incident records        │
    │  - Triage priority         │
    │  - Hazard identification   │
    │  - Medical assessment      │
    │  - Recommended actions     │
    └────────────────────────────┘
```

### Production Architecture (Future - Offline)

```
                      Same Interfaces
                            │
         ┌──────────────────┴──────────────────┐
         │                                     │
    Image/Audio Processing (same as MVP)
         │
    ┌────▼──────────────────────────┐
    │  LLM Provider Abstraction     │
    │                               │
    │  ┌─────────────────────────┐  │
    │  │ GemmaLocalProvider      │  │
    │  │ (Ollama / llama.cpp)    │  │
    │  │ 100% Offline            │  │
    │  └─────────────────────────┘  │
    └────┬──────────────────────────┘
         │
    ┌────▼─────────────────────────┐
    │  Gemma 4 Model (Local)       │
    │  - E2B or E4B quantized      │
    │  - 4-bit quantization        │
    │  - No internet required      │
    │  - Native function calling   │
    └────┬─────────────────────────┘
         │
    Function Executor (identical to MVP)
         │
    SQLite Database (identical to MVP)
```

**Key Design Principle**: Identical code; only LLM backend changes.

---

## 🎯 Deployment Scenarios

### Scenario 1: Hackathon Demo (Cloud)

**Stack:**
- Streamlit Cloud hosting
- Gemma API (pay-per-use)
- SQLite on server
- No local setup for judges

**Advantages:**
- Instant access for judges
- No hardware requirements
- Fully functional demo

**Cost Estimation:**
- 100 requests @ ~$0.001/request = $0.10
- Very affordable for hackathon

**Setup:**
```bash
# 1. Push to GitHub
git push origin main

# 2. Connect to Streamlit Cloud
# 3. Set GOOGLE_API_KEY in Streamlit secrets
# 4. Deploy victim_interface.py and responder_dashboard.py
```

### Scenario 2: Local Development

**Stack:**
- Python + Streamlit (local)
- Gemma API
- SQLite (local file)
- Internet required

**Use Case:**
- Development/testing
- Small deployments
- Resource-constrained areas (with connectivity)

**Performance:**
- API response: 1-3 seconds
- Total latency: 2-4 seconds
- Suitable for emergency use

### Scenario 3: Offline Edge Deployment

**Stack:**
- Python + Streamlit (local)
- Gemma 4 (Ollama/llama.cpp)
- SQLite (local)
- Zero internet required

**Use Case:**
- Disaster zones without connectivity
- Remote deployment
- Production use

**Performance:**
- Inference latency: 3-8 seconds (on 16GB RAM)
- Suitable for emergency use
- Total latency: 5-10 seconds

---

## 💰 Cost Analysis

### MVP (Gemma API)

| Component | Cost |
|-----------|------|
| Gemma 2-9B inference | ~$0.001 per request |
| Streamlit Cloud | Free (up to 3 apps) |
| Data storage | Negligible |
| **Total for 1000 incidents** | ~$1.00 |

### Production (Offline)

| Component | Cost |
|-----------|------|
| Gemma 4 model | Free (open-weight) |
| Ollama | Free |
| Hardware (16GB RAM) | $500-2000 one-time |
| Streamlit | Free |
| **Total operating cost** | $0.00 |

---

## 🔄 Migration Path

### Phase 1: Development (This Week)
- [ ] Build with Gemma API
- [ ] Verify schema and function calling
- [ ] Test with realistic scenarios
- [ ] Deploy to Streamlit Cloud

### Phase 2: Testing (Day 5-6)
- [ ] Install Ollama locally
- [ ] Download Gemma 4 model
- [ ] Test with local inference
- [ ] Record offline demo video

### Phase 3: Production (Week 2+)
- [ ] Deploy to edge devices
- [ ] Test in field scenarios
- [ ] Gather feedback
- [ ] Optimize model quantization

### Code Changes Required: **0 lines**
(Only environment variables change)

---

## 🧠 Model Selection Guide

### For MVP (Hackathon)
- **Model**: `gemma-2-9b-it` (default)
- **Why**: Good balance of speed and quality, fast API responses
- **Cost**: Cheapest tier

### For Production (Offline)
- **Model**: `gemma-4-e2b` or `gemma-4-e4b` (4-bit quantized)
- **Why**: Optimized for edge, 4-bit quantization for 16GB devices
- **Performance**: 5-8 seconds inference on typical hardware

### Alternative Models

| Model | Size | Speed | Quality | Cost | Use Case |
|-------|------|-------|---------|------|----------|
| Gemma 2-9B | 9B | Fast | Good | $$ | MVP/Demo |
| Gemma 2-27B | 27B | Med | Excellent | $$$ | High-accuracy |
| Gemma 1.1-7B | 7B | Very Fast | Good | $$ | Lightweight |
| Llama 2-7B | 7B | Very Fast | Fair | - | Open alternative |
| Mistral-7B | 7B | Very Fast | Good | - | High speed |

---

## 🚀 Deployment Checklist

### Pre-Deployment

- [ ] `.env` configured with API key
- [ ] `requirements.txt` installed
- [ ] Database schema verified
- [ ] Test suite passes (`python test_suite.py`)
- [ ] Both UIs launch without errors
- [ ] Sample incident submission works
- [ ] Dashboard displays incidents
- [ ] Responder filtering works

### Deployment

- [ ] Push to GitHub (private repo recommended)
- [ ] Set environment secrets in Streamlit Cloud
- [ ] Deploy victim_interface.py
- [ ] Deploy responder_dashboard.py
- [ ] Verify live URLs work
- [ ] Test with sample incidents
- [ ] Check database persistence
- [ ] Monitor for errors

### Post-Deployment

- [ ] Share access URLs with judges
- [ ] Document any issues
- [ ] Record offline demo video
- [ ] Create project summary
- [ ] Prepare presentation

---

## 🛠️ Configuration for Different Scenarios

### Configuration: Local Development
```env
AURAFIT_MODE=GEMMA
GEMMA_MODEL=gemma-2-9b-it
GOOGLE_API_KEY=your_key
LOG_LEVEL=DEBUG
```

### Configuration: Streamlit Cloud
```
(Set in Streamlit Cloud Secrets)
GOOGLE_API_KEY=your_key
AURAFIT_MODE=GEMMA
GEMMA_MODEL=gemma-2-9b-it
```

### Configuration: Offline (Future)
```env
AURAFIT_MODE=OFFLINE
OLLAMA_ENDPOINT=http://localhost:11434
GEMMA_MODEL=gemma-4-e2b
LOG_LEVEL=INFO
```

---

## 📊 Performance Optimization

### API Call Caching
```python
@st.cache_data(ttl=3600)
def cached_analysis(prompt_hash):
    # Results cached for 1 hour
    pass
```

### Image Optimization
- Maximum size: 1024x1024 pixels
- Quality: 85% JPEG
- Expected reduction: 70% file size

### Database Indexing
```sql
CREATE INDEX idx_priority ON incidents(incident_priority);
CREATE INDEX idx_created_at ON incidents(created_at DESC);
```

---

## 🔐 Security Considerations

### API Key Security
- Never commit `.env` files
- Use Streamlit Secrets for cloud deployment
- Rotate keys regularly
- Use separate keys for dev/prod

### Data Privacy
- All incidents stored locally
- No telemetry or tracking
- No third-party data sharing
- Backup database regularly

### Network Security
- HTTPS for cloud deployments
- Local network only for offline mode
- Firewall rules for edge devices

---

## 📈 Scaling Considerations

### Single Device Scaling
- **Streamlit local**: Up to 50 concurrent users
- **Database**: Up to 100k incidents on 1GB storage
- **Memory**: 4GB sufficient for MVP

### Multi-Device Scaling
- Multiple Streamlit instances with load balancer
- Shared SQLite via network (not recommended)
- Consider PostgreSQL for production
- Cache incidents across devices

---

## 🆘 Emergency Response

### If Gemma API is Down
- Automatic fallback to Gemini API (if configured)
- Manual fallback with structured text input
- Offline mode with local Gemma 4

### If Database Corrupts
```bash
# Restore from backup
cp data/aurafit_backup.db data/aurafit.db

# Or start fresh
rm data/aurafit.db  # Will recreate on next run
```

### If Internet Drops
- Offline mode continues unaffected
- Local TTS works without internet
- Database persists locally
- Sync happens when internet restored

---

## 🎯 Success Metrics

### MVP Hackathon
- ✅ Both UIs functional
- ✅ Gemma API successfully called
- ✅ Incidents stored and retrieved
- ✅ Responder dashboard displays data
- ✅ Judges can test live

### Production
- ✅ 99% uptime in offline mode
- ✅ <10 second response time
- ✅ Accurate triage classification
- ✅ Scalable to 1000+ incidents
- ✅ Field-tested reliability

---

**Ready to deploy?** Start with Scenario 1 (Cloud) for the hackathon! 🚀
