"""
Audio processing utilities for AuraFit
Handles speech recognition and text-to-speech conversion
"""

import logging
import io
import os
from typing import Optional
import speech_recognition as sr

logger = logging.getLogger(__name__)

# Safely initialize TTS Engine lazily to avoid crash on import
_tts_engine = None

def get_tts_engine():
    global _tts_engine
    if _tts_engine is None:
        try:
            import pyttsx3
            _tts_engine = pyttsx3.init()
            _tts_engine.setProperty('rate', 150)
            _tts_engine.setProperty('volume', 0.9)
        except Exception as e:
            logger.warning(f"Could not initialize pyttsx3 TTS engine: {e}")
            _tts_engine = False  # Mark as unavailable
    return _tts_engine if _tts_engine is not False else None


def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    """Convert audio bytes to text using speech recognition"""
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
    Convert text to speech using pyttsx3 (offline)
    """
    engine = get_tts_engine()
    if not engine:
        logger.error("TTS Engine is not available on this server.")
        return None

    try:
        if output_file:
            engine.save_to_file(text, output_file)
            engine.runAndWait()

            # Verify file exists before opening
            if os.path.exists(output_file):
                with open(output_file, 'rb') as f:
                    audio_bytes = f.read()
                logger.info(f"TTS audio generated: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                logger.error(f"TTS output file not found at {output_file}")
                return None
        else:
            logger.warning("In-memory TTS not fully supported, using file approach")
            return None

    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        return None


def validate_audio(audio_bytes: bytes) -> bool:
    """Validate audio data"""
    try:
        min_bytes = 16000 * 0.5 * 2
        if len(audio_bytes) < min_bytes:
            logger.warning(f"Audio too short: {len(audio_bytes)} bytes")
            return False

        max_bytes = 16000 * 5 * 60 * 2
        if len(audio_bytes) > max_bytes:
            logger.warning(f"Audio too long: {len(audio_bytes)} bytes")
            return False

        return True
    except Exception as e:
        logger.error(f"Error validating audio: {e}")
        return False


def get_safe_actions(actions_list: list) -> list:
    """Filter and sanitize recommended actions for TTS"""
    try:
        safe_actions = actions_list[:5]
        return safe_actions
    except Exception as e:
        logger.error(f"Error filtering actions: {e}")
        return []
