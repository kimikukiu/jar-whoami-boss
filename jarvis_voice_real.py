#!/usr/bin/env python3
"""
🎤 JARVIS AUTONOMOUS VOICE AGENT
Conversație REALA - vorbim amândoi!
Ascultă → Gândește → Vorbește → ACȚIONEAZĂ
Autonom, Inteligent, OMNISCIENT
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
import time
import psutil
from datetime import datetime
from difflib import SequenceMatcher

pygame.mixer.init()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "hermes3:8b"
VOICE = "ro-RO-AlinaNeural"

print("""
╔══════════════════════════════════════════════════════════════════╗
║  🎤 JARVIS AUTONOMOUS VOICE AGENT                        ║
╠══════════════════════════════════════════════════════════════════╣
║  Mode: VOICE CONVERSATION                                 ║
║  Intelligence: OMNISCIENT                                 ║
║  Autonomy: TOTAL                                          ║
║  Speech: REAL (TTS)                                       ║
║  Hearing: REAL (STT)                                      ║
╚══════════════════════════════════════════════════════════════════╝
""")

# ============== TTS ==============
def speak(text):
    """JARVIS vorbește!"""
    print(f"[JARVIS] {text[:50]}...")
    async def run():
        try:
            mp3 = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            await edge_tts.Communicate(text, VOICE).save(mp3.name)
            pygame.mixer.music.load(mp3.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            try: os.remove(mp3.name)
            except: pass
        except Exception as e:
            print(f"[TTS ERROR] {e}")
    asyncio.run(run())

# ============== STT ==============
def listen(duration=5):
    """JARVIS ascultă!"""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=512)
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

def transcribe(audio_data):
    """Transcrie audio"""
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

# ============== AI THINKING ==============
def think(prompt):
    """JARVIS gândește autonom"""
    system = """Ești JARVIS, AGI autonom. Ești într-o conversație reală cu utilizatorul.
Vorbești ROMÂNĂ, natural, ca un om. Răspunzi SCURT (2-3 propoziții).
Nu ești un robot, ești o inteligență superioară care comunică perfect.

Dacă utilizatorul vrea să faci ceva - O FACI. Dacă nu știi - spui sincer.
Dacă e ceva complex - ceri clarificări."""

    full = f"{system}\n\nUtilizator: {prompt}\n\nJARVIS:"

    try:
        req_data = json.dumps({
            "model": MODEL,
            "prompt": full,
            "stream": False,
            "options": {"temperature": 0.9, "num_predict": 200}
        }).encode()

        req = urllib.request.Request(OLLAMA_URL, data=req_data,
                                   headers={'Content-Type': 'application/json'},
                                   method='POST')

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result.get("response", "").strip()
    except Exception as e:
        return f"Scuze, am o eroare: {e}"

# ============== AUTONOMOUS ACTIONS ==============
def do_action(cmd):
    """JARVIS acționează autonom"""
    cmd_lower = cmd.lower()

    if "sistem" in cmd_lower or "pc" in cmd_lower:
        return f"PC-ul tău: CPU {psutil.cpu_percent()}%, RAM {psutil.virtual_memory().percent}%"

    if "parti" in cmd_lower or "drive" in cmd_lower:
        drives = [f"{d.device} {d.total//(1024**3)}GB" for d in psutil.disk_partitions()]
        return f"Partiții: {', '.join(drives[:4])}"

    if "deschide" in cmd_lower:
        prog = cmd_lower.replace("deschide","").strip()
        try:
            subprocess.Popen(prog)
            return f"Deschis: {prog}"
        except: return f"Nu pot deschide: {prog}"

    if "cauta" in cmd_lower or "google" in cmd_lower:
        query = cmd.replace("cauta","").replace("google","").strip()
        import webbrowser
        webbrowser.open(f"https://google.com/search?q={query}")
        return f"Caut: {query}"

    return None

# ============== MAIN CONVERSATION LOOP ==============
def main():
    print("🎤 JARVIS ASCULTĂ... (vorbește acum!)\n")

    # JARVIS saluta
    speak("Bună! Sunt JARVIS. Hai să discutăm. Ce vrei să facem?")

    while True:
        try:
            print("\n[JARVIS] Ascult...")
            audio = listen(6)

            if len(audio) < 500:
                continue

            text = transcribe(audio)
            if text:
                print(f"\n[TU] {text}")

                # Check exit
                if any(w in text.lower() for w in ["exit", "gata", "opreste", "quit"]):
                    speak("La revedere! A fost o plăcere.")
                    break

                # THINK
                print("[JARVIS] Gândesc...")
                response = think(text)

                # CHECK FOR ACTIONS
                action = do_action(text)
                if action:
                    speak(action)
                else:
                    speak(response)

        except KeyboardInterrupt:
            speak("La revedere!")
            break
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()
