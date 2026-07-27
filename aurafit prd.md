Product Requirements Document (PRD)
AuraFit: Offline AI Disaster & Emergency Response Copilot
Hackathon Track: Gemma 4 - Local Frontier Innovation
Document Version: 1.0.0
Target Build Deadline: Day 7 Hackathon Finalization
Target Regions: Nigeria (e.g., Niger/Benue Basin Flood Zones, Lagos Coastal Areas, Urban Center Collapses) & Globally Extensible
1. Executive Summary & Product Vision
1.1 Executive Summary
During catastrophic events—ranging from flash floods and building collapses to industrial gas explosions and severe road accidents—telecommunications networks and power grids are frequently compromised. Emergency management bodies such as the National Emergency Management Agency (NEMA) and State Emergency Management Agencies (SEMAs) become overwhelmed by thousands of unstructured, redundant, or panicked calls. Concurrently, citizens and first responders are forced to make life-or-death triage and navigation decisions in the dark without reliable internet access or expert medical guidance.
AuraFit is an AI-powered emergency response copilot that bridges the critical decision gap during natural and human-induced disasters. Designed from the ground up for edge execution on low-cost devices, AuraFit converts raw, multimodal inputs (photos, voice notes in local dialects/Pidgin, text) into structured incident records, safety instructions, and actionable responder dashboards.
1.2 Dual-Phase Strategy (MVP vs. Production)
While AuraFit's target end state is 100% local, offline inference powered by quantized Gemma 4 (E2B/E4B) via Ollama or llama.cpp, the constraints of a one-week hackathon timeline necessitate a pragmatic delivery model.
Hackathon MVP (Hosted Demo): Implements the complete product workflow, Streamlit UI, SQLite backend, function calling parser, and responder dashboard using the cloud-hosted Gemini API for inference.
Production Deployment Target: Replaces the single Gemini API client module with a local Gemma 4 inference engine (Gemma-4-E2B / Gemma-4-E4B via Ollama).
The application architecture is explicitly engineered so that zero business logic, frontend code, or database structures change between the MVP and the final offline production release; only the LLM client abstraction layer is swapped.
       +-------------------------------------------------------+
       |             AURAFIT ARCHITECTURAL ABSTRACTION         |
       +-------------------------------------------------------+
       |   Victim UI / Voice / Vision Input (Streamlit Front)  |
       +-------------------------------------------------------+
                                   |
                     +-------------+-------------+
                     | LLM Provider Interface    |
                     +-------------+-------------+
                                   |
            +----------------------+----------------------+
            |                                             |
  [ MVP / Hosted Demo ]                      [ Production / Offline ]
    Gemini API Backend                         Gemma 4 (Ollama / llama.cpp)
   (Cloud Inference)                          (100% On-Device / Edge)
            |                                             |
            +----------------------+----------------------+
                                   |
       +-------------------------------------------------------+
       |  JSON Tool Call Parser & Structured Execution Engine  |
       +-------------------------------------------------------+
                                   |
       +-------------------------------------------------------+
       |    SQLite Database & SEMA/NEMA Responder Dashboard     |
       +-------------------------------------------------------+


2. Target Audience & User Personas
AuraFit serves four primary stakeholders across the emergency management lifecycle:
Persona
Role & Context
Core Needs
AuraFit Value Proposition
Persona A: The Victim
Amina, an urban resident trapped in a rapidly flooding neighborhood in Kogi State with severed cell service.
Needs immediate, plain-language guidance on visual hazards (e.g., submerged electrical lines), first-aid instructions, and safety steps without completing tedious text forms.
Hands-free multimodal intake (voice/photo); instant, step-by-step hazard survival advice and local voice playback.
Persona B: Community Volunteer
Tunde, a youth leader arriving first at a building collapse site in Lagos.
Needs to assess multiple casualties rapidly, stabilize injuries, identify hazardous gas leaks, and relay clear data to incoming rescue teams.
Guided scene safety triage, structured casualty tag generation, and standardized incident categorization.
Persona C: Field Responder
Captain Ibrahim, a SEMA boat rescue lead navigating flooded sectors with an offline tablet.
Needs a consolidated, prioritized feed of verified emergency incidents sorted by critical severity (RED vs. YELLOW) rather than raw text complaints.
Color-coded START triage dashboard, hazard overlays, offline sector filtering, and estimated casualty counts.
Persona D: Emergency Operations Center (EOC)
Director Okon, supervising NEMA regional dispatch centers.
Needs real-time macro-analytics, hazard categorization, resource allocation optimization, and structured incident logs for post-disaster audits.
Aggregated analytics, searchable incident history, power isolation flags, and automatic database synchronization.

3. Core Problem Statement
During emergency scenarios across Nigeria and similar developing regions, emergency response fails due to five critical bottlenecks:
Information Asymmetry & Panic: Victims and untrained volunteers lack immediate access to medical or hazard-mitigation advice, leading to harmful interventions (e.g., applying tourniquets incorrectly, entering electrified floodwaters).
Infrastructure Vulnerability: Disasters systematically destroy cell towers, power lines, and fiber-optic backhauls, rendering standard web and cloud-based emergency services unusable.
Unstructured Data Overload: Emergency agencies (NEMA/SEMA) are flooded with disparate phone calls and voice recordings that take hours to parse, verify, and transcribe manually.
Poor Incident Prioritization: Field teams waste critical "Golden Hour" response time attending to low-risk issues because they lack a unified triage standard (e.g., Simple Triage and Rapid Treatment - START).
Language and Literacy Barriers: Emergency interfaces often demand typed English inputs, ignoring panicked victims speaking Nigerian Pidgin, Hausa, Yoruba, or Igbo.
4. Product Objectives & Success Metrics
4.1 Key Product Objectives
Instant Safety Guidance: Deliver localized visual and spoken emergency instructions in under 4 seconds from input submission.
Structured Triage Generation: Automate 100% of incoming unstructured multimodal reports into structured JSON records adhering to the START protocol.
Seamless Offline Migration: Maintain strict decoupling between the application layer and the AI model backend to allow one-line deployment swaps from Gemini API to Gemma 4.
Resource Optimization for Responders: Provide a prioritized, filterable incident dashboard that reduces field triage decision time for emergency responders.
4.2 Key Success Metrics
Schema Adherence:  valid JSON output parsing rate without runtime schema validation failures.
Inference Latency (MVP):  seconds end-to-end response time using Gemini API.
Inference Latency (Target Edge):  seconds total time for 4-bit quantized Gemma 4 on target hardware (16GB RAM Apple Silicon or mid-range GPU).
Zero UI Code Alteration:  change required in the Streamlit frontend when switching between hosted API and local Ollama inference.
5. Feature Specifications & System Capabilities
5.1 Victim / Civilian Module
Multimodal Intake Engine:
Photo Upload: Direct camera frame capture or image file upload supporting disaster scene analysis (e.g., floodwater depth, fire scale, physical injuries, structural collapse).
Voice Recording: Integrated browser audio recorder accepting voice descriptions in Nigerian Pidgin, Hausa, Yoruba, Igbo, or English (up to 30 seconds).
Text Input: High-contrast text area for manual symptom or situation description.
Immediate Guidance Panel:
Actionable Safety Instructions: Step-by-step bulleted instructions displayed in large, readable text.
Hazard Explanation: Explicit warnings regarding identified environmental threats (e.g., "Active Gas Leak - Do Not Light Fires").
Offline Speech Playback (TTS): Automated text-to-speech output using pyttsx3 for hands-free audio guidance in low-literacy contexts.
Evacuation Guidance (Future-Proof Stub): Safe path recommendations based on local landmark extraction.
5.2 Responder Command Dashboard
Prioritized Incident Feed:
Color-coded incident cards categorized according to disaster triage levels:
RED (Immediate): Critical injuries, severe bleeding, trapped under rubble, active high-voltage hazards.
YELLOW (Delayed): Fractures, moderate burns, stable trapped individuals.
GREEN (Minor): Minor abrasions, walking wounded, shelter/food requests.
BLACK (Expectant / Deceased): Non-survivable injuries or confirmed fatalities.
Filter & Search System: Filter by priority, hazard type (e.g., ELECTRICAL, GAS_LEAK, CHEMICAL), evacuation requirement, or text query (e.g., "Kogi flood sector B").
Incident Analytics Panel: Interactive Plotly charts showing incident distribution by priority, total estimated casualties, and hazard frequency over time.
Detailed Incident Modal: Expanded view presenting the original photo, transcribed audio, identified hazards, recommended actions, and power isolation status.
+-----------------------------------------------------------------------------------+
| AURAFIT DISASTER RESPONDER DASHBOARD                                              |
+-----------------------------------------------------------------------------------+
| Total Incidents: 42  | RED (Immediate): 8  | YELLOW: 14  | Evacuations Needed: 19 |
+-----------------------------------------------------------------------------------+
| [FILTER: All Priorities ▼] [SEARCH: "Lagos Collapse"       ] [EXPORT SQLITE DB]  |
+-----------------------------------------------------------------------------------+
|  [RED - CRITICAL] Building Collapse - Sector 4                                   |
|  Casualties: ~5 Trapped | Hazards: Gas Leak, Unstable Rubble                     |
|  Location: 14 Commercial Ave, Yaba | Power Isolation Req: YES                    |
|  [View Full Details & Photo] [Mark In-Progress]                                   |
+-----------------------------------------------------------------------------------+
|  [YELLOW - DELAYED] Submerged Vehicle - Flash Flood                               |
|  Casualties: 2 Stable | Hazards: Rising Water (Knee Level)                        |
|  Location: Oworonshoki Expressway | Power Isolation Req: NO                      |
|  [View Full Details & Photo] [Mark In-Progress]                                   |
+-----------------------------------------------------------------------------------+


5.3 AI Processing & Reasoning Pipeline
Multimodal Data Ingestion: Accepts raw byte stream for image and audio data.
Preprocessing & Transcription: Converts spoken audio to text via speech recognition tools or direct multimodal tokenization.
Structured Triage Reasoning: Analyzes combined image and text tokens through an emergency prompt template.
Tool Call Execution: Generates structured JSON parameters and executes the local Python function log_disaster_incident().
Database Persistence: Inserts parsed JSON attributes directly into the local SQLite store.
6. Function Calling Specification & Schema
AuraFit relies on structured tool calling to convert chaotic human inputs into machine-readable disaster logs. The schema below is shared identically across both the Gemini API client and the local Gemma 4 tool engine.
{
  "name": "log_disaster_incident",
  "description": "Parses an emergency or disaster report, assesses risks, identifies hazards, assigns START triage priority, and records a structured incident log.",
  "parameters": {
    "type": "object",
    "properties": {
      "incident_type": {
        "type": "string",
        "enum": [
          "FLOOD",
          "BUILDING_COLLAPSE",
          "FIRE_OUTBREAK",
          "ROAD_ACCIDENT",
          "GAS_EXPLOSION",
          "LANDSLIDE",
          "STORM_DAMAGE",
          "MEDICAL_EMERGENCY",
          "OTHER"
        ],
        "description": "Primary disaster or emergency classification."
      },
      "incident_priority": {
        "type": "string",
        "enum": ["RED_IMMEDIATE", "YELLOW_DELAYED", "GREEN_MINOR", "BLACK_EXPECTANT"],
        "description": "START triage priority category based on threat to life."
      },
      "casualty_count_estimate": {
        "type": "integer",
        "description": "Estimated number of victims or injured persons observed or reported."
      },
      "hazards_detected": {
        "type": "array",
        "items": { "type": "string" },
        "description": "List of active hazards identified (e.g., 'SUBMERGED_POWER_LINE', 'GAS_LEAK', 'UNSTABLE_STRUCTURE', 'CHEMICAL_SPILL', 'RAGING_FIRE')."
      },
      "recommended_actions": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Step-by-step immediate first-aid or survival instructions for the victim or volunteer."
      },
      "evacuation_required": {
        "type": "boolean",
        "description": "Set to true if immediate physical evacuation from the area is necessary."
      },
      "emergency_services_required": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Required response teams (e.g., 'FIRE_SERVICE', 'AMBULANCE', 'BOMB_SQUAD', 'FLOOD_RESCUE_BOAT', 'POWER_GRID_OPERATOR')."
      },
      "confidence_score": {
        "type": "number",
        "description": "Confidence score between 0.0 and 1.0 of the AI assessment."
      },
      "location_description": {
        "type": "string",
        "description": "Landmarks, sector tags, street names, or regional descriptions extracted from input."
      },
      "medical_summary": {
        "type": "string",
        "description": "Concise summary of physical injuries, trauma, or clinical state of casualties."
      }
    },
    "required": [
      "incident_type",
      "incident_priority",
      "casualty_count_estimate",
      "hazards_detected",
      "recommended_actions",
      "evacuation_required",
      "emergency_services_required",
      "confidence_score",
      "location_description",
      "medical_summary"
    ]
  }
}


7. Technical Architecture & System Data Flow
7.1 MVP Hosted Architecture (Hackathon Demo)
In the MVP implementation, user inputs are submitted through a Streamlit interface running on Streamlit Cloud. The backend routes the multimodal payload to the Gemini API, parses the function call response, executes local Python database logic, and updates SQLite.
+-----------------------------------------------------------------------+
|                         MVP HOSTED ARCHITECTURE                       |
+-----------------------------------------------------------------------+

  [ USER / VICTIM ]
         |
         | (Photo / Voice / Text)
         v
+------------------+      HTTP API      +-------------------------------+
|  Streamlit UI    | -----------------> | Gemini API                    |
| (Streamlit Cloud)| <----------------- | (gemini-2.5-flash / vision)   |
+------------------+  Function Call     +-------------------------------+
         |             JSON Payload
         v
+-----------------------------------------------------------------------+
|                       REASONING & PARSING LAYER                       |
| - Validates JSON Function Call Structure                              |
| - Extracts `recommended_actions` for Victim UI                        |
+-----------------------------------------------------------------------+
         |
         v
+-----------------------------------------------------------------------+
|                         PYTHON EXECUTOR                               |
| - Executes `log_disaster_incident()` function                         |
| - Formats hazard alerts & TTS audio triggers                          |
+-----------------------------------------------------------------------+
         |
         v
+-----------------------------------------------------------------------+
|                       LOCAL SQLITE DATABASE                           |
| - Stores structured incident card records                             |
+-----------------------------------------------------------------------+
         |
         v
+-----------------------------------------------------------------------+
|                    RESPONDER COMMAND DASHBOARD                        |
| - Real-time Plotly charts, START triage feeds, & filtering            |
+-----------------------------------------------------------------------+


7.2 Production Offline Architecture (Future Edge Deployment)
In full offline production, cloud API calls are completely removed. Gemma 4 runs locally on the host device (laptop, ruggedized server, or mobile hub) via Ollama or llama.cpp. Native function calling is processed locally, keeping all data 100% on-device.
+-----------------------------------------------------------------------+
|                   FUTURE OFFLINE EDGE ARCHITECTURE                    |
+-----------------------------------------------------------------------+

  [ USER / VICTIM ]
         |
         | (Photo / Voice / Text via Local Wi-Fi Hotspot or USB/Direct)
         v
+------------------+
|   Streamlit UI   |
| (Local Runtime)  |
+------------------+
         |
         | IPC / Local HTTP (localhost:11434)
         v
+-----------------------------------------------------------------------+
|                   GEMMA 4 LOCAL INFERENCE ENGINE                      |
| - Model: Gemma 4 E2B / E4B (4-bit Quantized)                          |
| - Runner: Ollama / llama.cpp (100% Offline / Zero Cloud)             |
| - Processing: Native Local Multimodal + Tool Use                      |
+-----------------------------------------------------------------------+
         |
         | Native Function Call Output
         v
+-----------------------------------------------------------------------+
|                     NATIVE FUNCTION CALL PARSER                       |
| - Identical parser interface as MVP                                   |
+-----------------------------------------------------------------------+
         |
         v
+-----------------------------------------------------------------------+
|                       LOCAL SQLITE DATABASE                           |
+-----------------------------------------------------------------------+
         |
         v
+-----------------------------------------------------------------------+
|                    RESPONDER COMMAND DASHBOARD                        |
+-----------------------------------------------------------------------+


7.3 Architectural Parity & Migration Mechanics
To prove that switching from MVP to Production requires minimal engineering effort, the application utilizes an explicit Strategy Pattern for the LLM interface:
# System Provider Interface Abstraction (llm_provider.py)
import os

class LLMProvider:
    def analyze_disaster(self, image_bytes, text_prompt, audio_bytes):
        raise NotImplementedError

class GeminiAPIProvider(LLMProvider):
    """Used for Hosted Hackathon MVP Demo"""
    def analyze_disaster(self, image_bytes, text_prompt, audio_bytes):
        # Calls google.generativeai / gemini API with tools schema
        pass

class GemmaLocalProvider(LLMProvider):
    """Used for Offline Production Deployment"""
    def analyze_disaster(self, image_bytes, text_prompt, audio_bytes):
        # Calls local Ollama endpoint (http://localhost:11434/api/generate)
        pass

# Factory selection based on single environment variable
def get_llm_provider() -> LLMProvider:
    mode = os.getenv("AURAFIT_MODE", "HOSTED_MVP")
    if mode == "LOCAL_OFFLINE":
        return GemmaLocalProvider()
    return GeminiAPIProvider()


8. Technology Stack Selection
Technology
Role
Justification
Python 3.10+
Core Programming Language
Universal ecosystem support for AI SDKs, data manipulation, and web frameworks; primary language of the team.
Streamlit
UI Framework
Enables rapid creation of both victim-facing interfaces and complex responder dashboards using pure Python without JavaScript overhead.
Google Gemini API (gemini-2.5-flash)
MVP Inference Engine
High-speed multimodal processing and structured tool-calling support for the online hackathon demonstration.
Gemma 4 (E2B / E4B via Ollama)
Production Inference Engine
Google's open frontier model optimized for edge deployment, providing local multimodal reasoning and tool invocation without network access.
SQLite
Database
Zero-configuration, lightweight, single-file relational database embedded directly within Python standard library. Ideal for offline edge devices.
SpeechRecognition / Whisper
Audio Processing
Audio-to-text transcription engine for converting non-standard speech and regional accents into text tokens.
pyttsx3
Text-to-Speech (TTS)
Fully offline, cross-platform Python text-to-speech engine that converts AI safety instructions into spoken audio without internet dependencies.
Pillow & OpenCV
Image Preprocessing
Lightweight Python libraries for cropping, resizing, and normalizing user-uploaded emergency scene photos.
Pandas & Plotly
Analytics & Visualizations
Powers the Responder Command Dashboard with real-time triage charts, casualty metrics, and hazard distributions.
Requests / HTTPX
Network Abstraction
Handles communication between Streamlit app and local Ollama REST endpoints or remote Gemini APIs.

9. Execution Strategy: Hosted Demo vs. Offline Production
9.1 The Hackathon Evaluation Problem
Hackathon judges evaluate submissions remotely over short timeframes. Demanding that judges download 4GB–8GB Gemma model weights, configure local Ollama environments, and execute GPU drivers introduces friction that leads to evaluation failures.
9.2 The Dual-Deployment Solution
AuraFit solves this by delivering a two-tier verification package:
Tier 1: Hosted Interactive Web App (For Convenience)
Deployed directly on Streamlit Cloud.
Driven by GeminiAPIProvider (AURAFIT_MODE=HOSTED_MVP).
Allows judges to immediately test photo uploads, voice clips, function calling, database writes, and dashboard views in their browser.
Tier 2: Recorded Offline Video & Architecture Verification (For Proof of Concept)
Unedited 3-minute video showing a laptop running AuraFit with Wi-Fi and Bluetooth completely disabled.
Demonstrates local audio/image ingestion, Ollama local inference execution via Gemma 4, SQLite database persistence, and pyttsx3 local voice playback.
Open-source repository with clear instructions on toggling AURAFIT_MODE=LOCAL_OFFLINE.
10. One-Week Development Roadmap
+---------------------------------------------------------------------------------------+
|                              ONE-WEEK BUILD SCHEDULE                                  |
+---------------------------------------------------------------------------------------+
  Day 1: Architecture setup, prompt engineering & function schema definition.
  Day 2: Multimodal intake pipelines (Pillow image processing & Speech-to-Text).
  Day 3: Core AI reasoning engine integration, function call parser, SQLite schema.
  Day 4: SEMA/NEMA Responder Command Dashboard & Plotly analytics implementation.
  Day 5: UI polish, error handling, local pyttsx3 TTS, scenario testing.
  Day 6: Cloud deployment, offline demo video recording, pitch deck & README drafting.
  Day 7: Code freeze, bug fixes, final presentation submission.
+---------------------------------------------------------------------------------------+


10.1 Daily Work Plan
Day 1: Architecture & Schema Specification
Establish GitHub repository structure and environment configuration.
Formalize log_disaster_incident JSON function calling schema.
Engineer system prompt templates for emergency triage reasoning.
Test raw Gemini API function calling vs. simulated local responses.
Day 2: Data Intake & Pipeline Integration
Build Streamlit camera input, image upload, and file handler.
Implement audio recording UI component and Speech-to-Text transcription parser.
Test multimodal payload assembly (Image + Audio Text + Prompt).
Day 3: Core AI Engine & Database Layer
Implement llm_provider.py abstraction layer.
Build JSON Tool Call Parser with schema validation and fallback error handling.
Initialize SQLite database schema and write helper methods (insert_incident, get_all_incidents).
Day 4: Responder Command Dashboard
Build SEMA/NEMA multi-column dashboard layout in Streamlit.
Create color-coded priority cards (RED, YELLOW, GREEN, BLACK).
Build Plotly analytics charts (incidents by priority, hazards breakdown).
Implement sector and priority filtering logic.
Day 5: UI Polish & Local TTS Integration
Add high-contrast CSS styling tailored for emergency/field visibility.
Integrate pyttsx3 offline text-to-speech engine for audio guidance output.
Conduct simulated disaster scenarios (floods, building collapses, gas leaks).
Day 6: Deployment & Assets Production
Deploy MVP web application to Streamlit Cloud.
Record unedited 3-minute offline demonstration video (Wi-Fi disconnected, local execution).
Draft project README.md, architectural diagrams, and pitch deck.
Day 7: Final Polish & Submission
Perform end-to-end bug sweeps and handling for edge cases (corrupt images, empty audio).
Lock code repository.
Submit project to the Hackathon portal.
11. Team Task Breakdown (2-Person Team)
To maximize velocity during a 7-day sprint, responsibilities are strictly split between two engineers:
+-----------------------------------------------------------------------------------+
|                            TEAM RESPONSIBILITY MATRIX                             |
+-----------------------------------------------------------------------------------+
| TEAMMATE 1: Backend Engineer / System Architect                                   |
| - Streamlit UI development (Victim interface & Responder Dashboard)               |
| - LLM Provider abstraction implementation (Gemini API & Ollama local stub)        |
| - SQLite database setup, query functions, and state management                    |
| - Plotly analytics charts & filter logic                                          |
| - Cloud deployment to Streamlit Cloud & system config handling                    |
| - Offline demo video recording & project submission documentation                 |
+-----------------------------------------------------------------------------------+
| TEAMMATE 2: ML / Prompt Engineering & Domain Lead                                 |
| - Prompt engineering for disaster triage and hazard detection                     |
| - JSON function calling schema design (`log_disaster_incident`)                   |
| - Multimodal intake handling (Image preprocessing & Audio-to-Text pipeline)       |
| - System validation across Nigerian disaster scenario test sets                   |
| - Evaluation of local Gemma 4 quantization performance & schema adherence        |
| - Slide deck creation, README architectural writing, & pitch asset prep           |
+-----------------------------------------------------------------------------------+


12. Non-Functional Requirements
Offline Capability (Target State): 100% of core inference, database reads/writes, and text-to-speech generation must execute locally without an active internet connection.
Inference Latency: Total response latency from user submission to visual output display must not exceed 5.0 seconds on target edge hardware.
Data Privacy & Security: All emergency incident data and medical summaries must remain on local device storage; no telemetry tracking or third-party analytical leaks.
Resilient UI Design: High-contrast user interface with large touch targets suitable for low-light conditions, outdoor sunlight, or field deployment on tablets.
Codebase Maintainability: High abstraction between UI, database, and LLM inference engine ensuring seamless back-end migration with minimal code churn.
13. Risk Matrix & Mitigation Strategies
Risk Description
Severity
Likelihood
Impact Area
Mitigation Strategy
API Response Instability / Schema Failures
High
Medium
Function Calling
Enforce strict pydantic/JSON schema validation; implement robust fallback parsing to extract structured data from unstructured text if tool calling fails.
Image Understanding Limitations
Medium
Medium
Vision Pipeline
Combine vision prompt tokens with text/voice descriptions to ensure double redundancy during scene assessment.
Speech Recognition Errors on Dialects
High
High
Audio Input
Implement fallback manual selection buttons (e.g., "Select Disaster Type") if audio transcription confidence falls below set threshold.
API Latency during Live Judge Demos
Medium
Low
MVP Performance
Implement client-side caching for pre-tested sample inputs; keep image resolution constrained to 1024x1024 max before payload transmission.
Local Hardware Constraints for Gemma 4
High
Medium
Future Offline
Utilize 4-bit quantized Gemma 4 model weights (E2B or E4B) designed specifically for low-footprint laptop deployment (8GB–16GB RAM).
Hackathon Timeline Compression
High
Medium
Delivery
Strictly adhere to the scope boundaries outlined in the Day-by-Day roadmap; defer non-essential features (e.g., mesh networking) to post-hackathon phases.

14. Implementation Checklist & Verification
[ ] log_disaster_incident schema finalized and validated.
[ ] Multimodal upload components functional in Streamlit.
[ ] Gemini API provider successfully outputting compliant JSON.
[ ] SQLite table creation and auto-logging logic verified.
[ ] Responder Dashboard updating in real-time with priority color codes.
[ ] Plotly analytics correctly rendering incident metrics.
[ ] AURAFIT_MODE environment switch tested between API and local modes.
[ ] Unedited offline video demo recorded and linked in documentation.
[ ] Streamlit Cloud deployment published and verified live.
End of Product Requirements Document.
