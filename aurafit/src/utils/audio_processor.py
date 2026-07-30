"""
Audio processing utilities for AuraFit
Handles speech recognition and text-to-speech conversion
"""

import logging
import io
import pyttsx3
from typing import Optional
import speech_recognition as sr

logger = logging.getLogger(__name__)

# Initialize TTS engine lazily so the app can still run on systems without espeak.
tts_engine = None
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)  # Slower speech for clarity
    tts_engine.setProperty('volume', 0.9)
except Exception as e:
    logger.warning(f"TTS unavailable, continuing without speech output: {e}")


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
    Convert text to speech using pyttsx3 (offline)
    
    Args:
        text: Text to convert
        output_file: Optional file path to save audio
        
    Returns:
        Audio bytes or None if conversion failed
    """
    try:
        if tts_engine is None:
            logger.warning("TTS engine unavailable; skipping speech output")
            return None

        if output_file:
            tts_engine.save_to_file(text, output_file)
            tts_engine.runAndWait()
            
            # Read the file
            with open(output_file, 'rb') as f:
                audio_bytes = f.read()
            logger.info(f"TTS audio generated: {len(audio_bytes)} bytes")
            return audio_bytes
        else:
            # In-memory conversion (less reliable)
            logger.warning("In-memory TTS not fully supported, using file approach")
            return None
            
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
