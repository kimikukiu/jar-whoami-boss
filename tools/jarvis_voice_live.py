#!/usr/bin/env python3
"""
JARVIS GOD MODE - Ollama Optimized
- Better Ollama support with retry
- Fallback models
- Fast response
"""

import pyaudio
import speech_recognition as sr
import pygame
import asyncio
import urllib.request
import json
import os
import tempfile
import edge_tts
import subprocess
import threading
import time
import psutil
from datetime import datetime
from difflib import SequenceMatcher
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

# FFmpeg
FFMPEG_PATH = r"C:\Program Files\Gyan\FFmpeg\bin"
if FFMPEG_PATH not in os.environ.get('PATH', ''):
    os.environ['PATH'] = FFMPEG_PATH + ";" + os.environ.get('PATH', '')

pygame.mixer.init()

# ========================
# GOD STATUS
# ========================
GOD = {
    "mode": "GOD",
    "status": "JARVIS ready",
    "ollama_connected": False,
    "models_available": []
}

app = Flask(__name__)

@app.route('/api/jarvis/status')
def get_status():
    return jsonify(GOD)

@app.route('/api/jarvis/ollama/check')
def check_ollama():
    return jsonify({
        "connected": GOD["ollama_connected"],
        "models": GOD["models_available"]
    })

def start_api():
    app.run(host='0.0.0.0', port=5003, debug=False, use_reloader=False, threaded=True)

# Don't start API on startup to avoid blocking
# threading.Thread(target=start_api, daemon=True).start()

# ========================
# OLLAMA CONNECTION
# ========================
OLLAMA_URL = "http://localhost:11434"
MODEL = "hermes3:8b"  # Stable model
VOICE_NAME = "ro-RO-AlinaNeural"

# Load model from config if exists
try:
    config_path = r"D:\jarvis\ecosystem\config\ollama.json"
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            MODEL = config.get("model", MODEL)
            print(f"[CONFIG] Using model: {MODEL}")
except:
    pass

def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method='GET')
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            models = [m['name'] for m in data.get('models', [])]
            GOD["ollama_connected"] = True
            GOD["models_available"] = models
            print(f"[OLLAMA] Connected! Models: {len(models)}")
            return True
    except Exception as e:
        print(f"[OLLAMA] Not connected: {e}")
        GOD["ollama_connected"] = False
        return False

def ollama_generate(prompt, model=None):
    """Generate with Ollama - robust with retry"""
    model = model or MODEL

    system_prompt = """Ești JARVIS, AI asistent. Răspunzi scurt, direct, în română.
Expresii: "Sir", "Așadar". Nu ești superfluu."""

    full_prompt = f"{system_prompt}\n\n{prompt}\n\nJARVIS:"

    for attempt in range(3):
        try:
            req_data = json.dumps({
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": 150
                }
            }).encode()

            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/generate",
                data=req_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=45) as resp:
                result = json.loads(resp.read().decode())
                return result.get("response", "").strip()

        except Exception as e:
            print(f"[OLLAMA] Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(1)

    return "Scuze, Sir, am întâmpinat o problemă cu AI-ul."

# Check Ollama on startup (non-blocking)
try:
    check_ollama_connection()
except:
    pass

print(f"""
╔══════════════════════════════════════════════════════════╗
║  🎛️  JARVIS GOD MODE - OLLAMA OPTIMIZED              ║
╠══════════════════════════════════════════════════════════╣
║  Model: {MODEL}                                      ║
║  Ollama: {"Connected" if GOD['ollama_connected'] else "Checking..."}                                      ║
║  Mode: GOD (Always Active)                           ║
╚══════════════════════════════════════════════════════════╝
""")

# ========================
# TTS
# ========================
def speak(text):
    print(f"[TTS] {text[:50]}...")
    GOD["status"] = f"Speaking: {text[:30]}..."

    async def run():
        try:
            temp_dir = r"D:\jarvis\temp"
            os.makedirs(temp_dir, exist_ok=True)
            mp3_path = os.path.join(temp_dir, "jarvis_tts.mp3")

            communicate = edge_tts.Communicate(text, VOICE_NAME)
            await communicate.save(mp3_path)

            if os.path.exists(mp3_path):
                pygame.mixer.music.load(mp3_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                try: os.remove(mp3_path)
                except: pass
        except Exception as e:
            print(f"[TTS ERROR] {e}")
        finally:
            GOD["status"] = "JARVIS ready"

    asyncio.run(run())

# ========================
# LISTEN
# ========================
def listen(duration=4):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                   input=True, frames_per_buffer=512)
    frames = []
    for _ in range(int(16000 / 512 * duration)):
        try:
            data = stream.read(512, exception_on_overflow=False)
            frames.append(data)
        except: break
    stream.stop_stream()
    stream.close()
    p.terminate()
    return b''.join(frames)

# ========================
# TRANSCRIBE
# ========================
def transcribe(audio_data):
    try:
        r = sr.Recognizer()
        audio = sr.AudioData(audio_data, 16000, 2)
        for lang in ["ro-RO", "en-US"]:
            try:
                text = r.recognize_google(audio, language=lang)
                if text:
                    return text
            except: continue
    except: pass
    return None

# ========================
# SYSTEM INFO
# ========================
def get_system():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return f"CPU: {cpu}% | RAM: {mem}%"

# ========================
# MAIN - GOD MODE
# ========================
def main():
    print("🎛️  GOD MODE - Vorbește direct!\n")

    # Skip greeting to avoid blocking
    # speak("JARVIS online. Vorbește direct.")

    while True:
        try:
            print("[GOD] Ascult...")
            GOD["status"] = "Listening"

            audio = listen(4)

            if len(audio) < 500:
                continue

            text = transcribe(audio)
            if text:
                print(f"[YOU] '{text}'")
                GOD["status"] = f"Processing: {text[:40]}"

                text_lower = text.lower()

                # Exit
                if any(w in text_lower for w in ["exit", "gata", "opreste"]):
                    speak("JARVIS offline.")
                    break

                # System
                if any(w in text_lower for w in ["sistem", "system"]):
                    speak(f"Sistem: {get_system()}")
                    continue

                # AI Response
                response = ollama_generate(text)
                speak(response)

        except KeyboardInterrupt:
            speak("JARVIS shutdown.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
