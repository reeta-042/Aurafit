"""
Audio processing utilities for AuraFit
Handles speech recognition and text-to-speech conversion
"""

import logging
import os
import io
import speech_recognition as sr
from typing import Optional
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

logger = logging.getLogger(__name__)

# Google TTS fallback for Streamlit Cloud environments without local espeak support.
def _build_tts_audio(text: str) -> Optional[bytes]:
    try:
        if not text or not text.strip() or gTTS is None:
            return None

        tts = gTTS(text=text, lang="en", slow=False)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.warning(f"Google TTS unavailable: {e}")
        return None


def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    """
    Convert audio bytes to text using speech recognition
    
    Args:
        audio_bytes: Raw audio data
        
    Returns:
        Transcribed text or None if recognition failed
    """
    try:
        recognizer = sr.Recognizer()
        
        # Convert bytes to AudioData
        audio = sr.AudioData(
            frame_data=audio_bytes,
            sample_rate=16000,
            sample_width=2
        )
        
        # Try Google speech recognition (free tier)
        try:
            text = recognizer.recognize_google(audio, language="en-NG")
            logger.info(f"Speech recognized: {text[:50]}...")
            return text
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.warning(f"Speech recognition service error: {e}")
            return None
            
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return None


def text_to_speech(text: str, output_file: Optional[str] = None) -> Optional[bytes]:
    """
    Convert text to speech using Google TTS.
    This avoids the local espeak dependency that is missing in Streamlit Cloud.
    """
    try:
        audio_bytes = _build_tts_audio(text)
        if audio_bytes is None:
            logger.warning("Google TTS unavailable; skipping speech output")
            return None

        if output_file:
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
            logger.info(f"TTS audio generated: {len(audio_bytes)} bytes")
            return audio_bytes

        logger.info(f"TTS audio generated: {len(audio_bytes)} bytes")
        return audio_bytes

    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        return None


def validate_audio(audio_bytes: bytes) -> bool:
    """
    Validate audio data
    
    Args:
        audio_bytes: Raw audio data
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Minimum audio length (0.5 seconds at 16kHz, 16-bit)
        min_bytes = 16000 * 0.5 * 2
        
        if len(audio_bytes) < min_bytes:
            logger.warning(f"Audio too short: {len(audio_bytes)} bytes")
            return False
        
        # Maximum reasonable audio length (5 minutes)
        max_bytes = 16000 * 5 * 60 * 2
        if len(audio_bytes) > max_bytes:
            logger.warning(f"Audio too long: {len(audio_bytes)} bytes")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating audio: {e}")
        return False


def get_safe_actions(actions_list: list) -> list:
    """
    Filter and sanitize recommended actions for TTS
    Returns only the first few critical actions to avoid overwhelming users
    """
    try:
        # Take first 3-5 most critical actions
        safe_actions = actions_list[:5]
        return safe_actions
    except Exception as e:
        logger.error(f"Error filtering actions: {e}")
        return []
