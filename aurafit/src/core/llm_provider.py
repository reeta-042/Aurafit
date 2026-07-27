"""
LLM Provider - Gemma API
Google Gemma models for disaster incident analysis with function calling
"""

import os
import json
import base64
import logging
from typing import Optional, Tuple, Dict, Any
from google import genai

logger = logging.getLogger(__name__)


class GemmaAPIProvider:
    """Uses Google's Gemma models via google-genai SDK"""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemma-4-26b-a4b-it"):
        """
        Initialize Gemma API provider
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model_name: Model name to use (e.g., "gemma-4-26b-a4b-it")
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Initialize the genai client with the API key
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        logger.info(f"Initialized Gemma API Provider with model: {self.model_name}")

    def analyze_disaster(
        self, 
        image_bytes: Optional[bytes],
        text_prompt: str,
        audio_text: Optional[str] = None,
        communication_language: str = "Nigerian Pidgin",
        response_language: str = "Nigerian Pidgin"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze disaster using Gemma API with structured JSON output and strict system prompt.
        Accepts inputs in Nigerian Pidgin, English, Yoruba, Hausa, Igbo, or ethnic languages.
        Generates calm, reassuring victim guidance in the preferred response language.
        """
        try:
            system_prompt = f"""You are AuraFit, an AI emergency response copilot for disaster triage and victim survival guidance.

CRITICAL INSTRUCTIONS:
1. Input Handling: The victim is communicating using {communication_language}. Accept and interpret all text, photo/image analysis, and audio transcriptions regardless of slang, pidgin, or local dialect.
2. Triage & Assessment: Classify according to the START (Simple Triage and Rapid Treatment) protocol.
   - Priority must be one of: "RED_IMMEDIATE", "YELLOW_DELAYED", "GREEN_MINOR", "BLACK_EXPECTANT".
   - Type must be one of: "FLOOD", "BUILDING_COLLAPSE", "FIRE_OUTBREAK", "ROAD_ACCIDENT", "GAS_EXPLOSION", "LANDSLIDE", "STORM_DAMAGE", "MEDICAL_EMERGENCY", "OTHER".
3. Victim Reassurance (Calm Tone): Provide "victim_calm_response" written directly in {response_language}. The tone MUST be extremely calm, compassionate, reassuring, and direct—specifically spoken to a person currently in danger to keep them calm and safe.
4. Actionable Steps: Provide "recommended_actions" as step-by-step instructions in {response_language}.

Output MUST be a single, strictly formatted valid JSON object matching this exact schema:
{{
  "incident_type": "FLOOD",
  "incident_priority": "RED_IMMEDIATE",
  "casualty_count_estimate": 1,
  "hazards_detected": ["HIGH_WATER", "ELECTRICAL_HAZARD"],
  "recommended_actions": ["Step 1 in {response_language}", "Step 2 in {response_language}"],
  "evacuation_required": true,
  "emergency_services_required": ["AMBULANCE", "RESCUE_BOAT"],
  "confidence_score": 0.9,
  "location_description": "Location description from report",
  "medical_summary": "Medical status summary",
  "victim_calm_response": "Calm, empathetic, reassuring message to victim in {response_language}",
  "communication_language": "{communication_language}",
  "latitude": 6.5244,
  "longitude": 3.3792,
  "gps_coordinates": "6.52440, 3.37920"
}}"""

            # Build full prompt
            full_prompt = text_prompt
            if audio_text:
                full_prompt = f"{text_prompt}\n\nVoice Recording Input: {audio_text}"

            # Prepare content parts
            content_parts = []
            
            # Add image if provided
            if image_bytes:
                try:
                    content_parts.append(
                        genai.types.Part.from_bytes(
                            data=image_bytes,
                            mime_type="image/jpeg"
                        )
                    )
                    logger.info("Attached JPEG image part for Gemma API multimodal analysis")
                except Exception as e:
                    logger.error(f"Error encoding image: {e}")
                    logger.info("Continuing with text-only analysis")
            
            # Add system prompt and user text
            content_parts.append(genai.types.Part.from_text(f"{system_prompt}\n\nEmergency Report Input:\n{full_prompt}"))
            
            # Call Gemma API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=content_parts,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                )
            )
            
            response_text = ""
            function_call_data = {}
            
            if response.text:
                response_text = response.text
                text = response_text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
                try:
                    function_call_data = json.loads(text)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing error: {e}. Raw response: {response_text[:100]}")
            
            return response_text, function_call_data
            
        except Exception as e:
            logger.error(f"Error in Gemma API analysis: {e}")
            raise





def get_llm_provider() -> GemmaAPIProvider:
    """
    Get Gemma API provider instance
    
    Returns:
        GemmaAPIProvider instance
    """
    model_name = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")
    return GemmaAPIProvider(model_name=model_name)
