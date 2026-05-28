"""
JARVIS Whisper Speech-to-Text
Local offline speech recognition with OpenAI Whisper
"""

import os
import sys
import threading
import queue
import tempfile
import subprocess
import json
import time
import numpy as np

WHISPER_AVAILABLE = False
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    whisper = None

SR_AVAILABLE = False
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    sr = None



class WhisperSTT:
    """
    Whisper-based Speech-to-Text with fallback to Google Speech
    """
    
    def __init__(self, model_size="base", language="ro"):
        self.model_size = model_size
        self.language = language
        self.model = None
        self._recognizer = None
        self._microphone = None
        self._audio_queue = queue.Queue()
        self._running = False
        self._thread = None
        
        if WHISPER_AVAILABLE:
            print(f"[WHISPER] Loading model: {model_size}")
            try:
                self.model = whisper.load_model(model_size)
                print(f"[WHISPER] Model loaded successfully")
            except Exception as e:
                print(f"[WHISPER] Error loading model: {e}")
        
        if SR_AVAILABLE:
            self._recognizer = sr.Recognizer()
            self._recognizer.dynamic_energy_threshold = True
    
    def _record_audio(self, duration=5):
        """Record audio from microphone"""
        if not SR_AVAILABLE:
            return None
        
        try:
            if self._microphone is None:
                self._microphone = sr.Microphone()
            
            with self._microphone as source:
                print(f"[WHISPER] Recording for {duration}s...")
                self._recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self._recognizer.listen(source, timeout=duration+2, phrase_time_limit=duration)
                return audio
        except Exception as e:
            print(f"[WHISPER] Recording error: {e}")
            return None
    
    def _audio_to_numpy(self, audio):
        """Convert speech_recognition AudioData to numpy array"""
        raw_data = audio.get_raw_data(convert_width=2)
        audio_array = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
        return audio_array
    
    def transcribe(self, audio_data=None, duration=5):
        """
        Transcribe audio to text
        If audio_data is None, will record from microphone
        """
        # Record if no audio provided
        if audio_data is None:
            audio_data = self._record_audio(duration)
            if audio_data is None:
                return None
        
        # Try Whisper first
        if self.model is not None:
            try:
                print("[WHISPER] Processing with Whisper...")
                audio_array = self._audio_to_numpy(audio_data)
                
                result = self.model.transcribe(
                    audio_array, 
                    language=self.language,
                    fp16=False
                )
                text = result.get("text", "").strip()
                if text:
                    print(f"[WHISPER] Transcribed: '{text}'")
                    return text
            except Exception as e:
                print(f"[WHISPER] Error: {e}")
        
        # Fallback to Google Speech Recognition
        if SR_AVAILABLE and self._recognizer:
            try:
                print("[WHISPER] Falling back to Google Speech...")
                text = self._recognizer.recognize_google(
                    audio_data, 
                    language=f"{self.language}-{self.language.upper()}"
                )
                print(f"[WHISPER] Google transcribed: '{text}'")
                return text
            except Exception as e:
                print(f"[WHISPER] Google error: {e}")
        
        return None
    
    def listen_and_transcribe(self, duration=5):
        """Convenience method: record and transcribe"""
        return self.transcribe(duration=duration)



# Standalone test
if __name__ == "__main__":
    stt = WhisperSTT(model_size="base", language="ro")
    
    print("\n=== Test Whisper STT ===")
    print("Speak now (Romanian)...")
    
    result = stt.listen_and_transcribe(duration=5)
    
    if result:
        print(f"\n✓ Result: '{result}'")
    else:
        print("\n✗ No speech recognized")
