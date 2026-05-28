"""
JARVIS Voice System v5 - OLLAMA ADVANCED
"""

import threading
import queue
import os
import sys
import time
import subprocess
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EDGE_TTS_AVAILABLE = False
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    edge_tts = None

# Whisper STT for Romanian speech recognition
WHISPER_AVAILABLE = False
try:
    from whisper_stt import WhisperSTT
    WHISPER_AVAILABLE = True
except ImportError:
    WhisperSTT = None

VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    sr = None

PYTHONCOM_AVAILABLE = False
try:
    import pythoncom
    PYTHONCOM_AVAILABLE = True
except ImportError:
    pythoncom = None


def _play_tts_async(mp3_path):
    def play():
        try:
            subprocess.Popen(
                ['powershell', '-c', f'(New-Object Media.SoundPlayer "{mp3_path}").PlaySync()'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=0x08000000
            )
        except Exception:
            try:
                os.startfile(mp3_path)
            except Exception:
                pass
        try:
            time.sleep(2)
            os.remove(mp3_path)
        except Exception:
            pass
    threading.Thread(target=play, daemon=True).start()


class VoiceSystem:
    def __init__(self):
        self.wake_word = "jarvis"
        self.preferred_languages = ["en-US", "ro-RO"]
        self.callback = None
        self._tts_queue = queue.Queue()
        self._ollama_model = os.environ.get("JARVIS_OLLAMA_MODEL", "hermes3:8b")
        self._ollama_url = os.environ.get("JARVIS_OLLAMA_URL", "http://localhost:11434/api/generate")
        self._running = False
        
        # Initialize Whisper for Romanian STT
        self._whisper_stt = None
        if WHISPER_AVAILABLE:
            try:
                print("[VOICE] Initializing Whisper STT for Romanian...")
                self._whisper_stt = WhisperSTT(model_size="base", language="ro")
                print("[VOICE] Whisper STT ready!")
            except Exception as e:
                print(f"[VOICE] Whisper init error: {e}")
        
        # Voice status for UI
        self._voice_status = "idle"  # idle, listening, speaking, processing
        self._status_lock = threading.Lock()

    def _set_voice_status(self, status):
        """Set voice status thread-safely for UI"""
        with self._status_lock:
            self._voice_status = status
            print(f"[VOICE STATUS] {status}")

    def get_voice_status(self):
        """Get current voice status for UI"""
        with self._status_lock:
            return self._voice_status

    def _tts_worker(self):
        while self._running:
            try:
                item = self._tts_queue.get(timeout=1.0)
                if not item:
                    continue

                text = item["text"]
                if not text:
                    continue

                lang = 'ro' if any(c in text.lower() for c in 'ăâîșț') else 'en'
                voice = 'ro-RO-AlinaNeural' if lang == 'ro' else 'en-US-AriaNeural'

                if EDGE_TTS_AVAILABLE:
                    try:
                        # Set speaking status before TTS
                        self._set_voice_status('speaking')
                        
                        mp3_path = os.path.join(tempfile.gettempdir(), f'j_{int(time.time()*1000)}.mp3')
                        import asyncio
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            comm = edge_tts.Communicate(text, voice)
                            loop.run_until_complete(comm.save(mp3_path))
                        finally:
                            loop.close()
                        _play_tts_async(mp3_path)
                        
                        # Wait a bit then set back to listening
                        time.sleep(0.5)
                        self._set_voice_status('listening')
                    except Exception as e:
                        print(f"[TTS] Error: {e}")
                        self._set_voice_status('listening')
            except queue.Empty:
                pass
            except Exception as e:
                print(f"[TTS] Worker error: {e}")

    def _listen_worker(self):
        if PYTHONCOM_AVAILABLE:
            pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)

        try:
            recognizer = sr.Recognizer()
            recognizer.dynamic_energy_threshold = True
            recognizer.energy_threshold = 200

            mic_idx = os.environ.get("JARVIS_MIC_INDEX")
            if mic_idx and str(mic_idx).strip():
                mic = sr.Microphone(device_index=int(mic_idx))
            else:
                mic = sr.Microphone()

            print("[VOICE] Adjusting microphone...", flush=True)
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print(f"[VOICE] Ready with model: {self._ollama_model}", flush=True)

            while self._running:
                try:
                    with mic as source:
                        audio = recognizer.listen(source, phrase_time_limit=5, timeout=1)

                    text = None
                    for lang in self.preferred_languages:
                        try:
                            data = recognizer.recognize_google(audio, language=lang, show_all=True)
                            if isinstance(data, dict):
                                alts = data.get("alternative", [])
                                if alts:
                                    text = alts[0].get("transcript", "").strip()
                                    break
                        except Exception:
                            continue

                    if text:
                        print(f"[VOICE] Heard: '{text}'", flush=True)
                        if self.wake_word in text.lower():
                            self._on_wake(text, mic, recognizer)

                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    print(f"[VOICE] Listen error: {e}", flush=True)
                    time.sleep(0.5)

        except Exception as e:
            print(f"[VOICE] Worker error: {e}", flush=True)
        finally:
            if PYTHONCOM_AVAILABLE:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    def _on_wake(self, text, mic, recognizer):
        print(f"[VOICE] WAKE: '{text}'", flush=True)
        self._set_voice_status('speaking')
        self.speak({"text": "Da. Sunt aici. Spune comanda.", "urgent": True})

        time.sleep(2)
        self._set_voice_status('listening')

        try:
            print("[VOICE] Listening for command...", flush=True)
            with mic as source:
                audio = recognizer.listen(source, phrase_time_limit=10)

            cmd_text = None
            
            # Try Whisper first for better Romanian recognition
            if self._whisper_stt is not None:
                try:
                    print("[VOICE] Using Whisper for recognition...", flush=True)
                    self._set_voice_status('processing')
                    cmd_text = self._whisper_stt.transcribe(audio_data=audio, duration=0)
                    if cmd_text:
                        print(f"[VOICE] Whisper recognized: '{cmd_text}'", flush=True)
                except Exception as e:
                    print(f"[VOICE] Whisper error: {e}", flush=True)
            
            # Fallback to Google if Whisper failed
            if not cmd_text:
                for lang in self.preferred_languages:
                    try:
                        data = recognizer.recognize_google(audio, language=lang, show_all=True)
                        if isinstance(data, dict):
                            alts = data.get("alternative", [])
                            if alts:
                                cmd_text = alts[0].get("transcript", "").strip()
                                break
                    except Exception:
                        continue

            if cmd_text:
                print(f"[VOICE] Command: '{cmd_text}'", flush=True)
                self._set_voice_status('processing')
                self._process_ollama(cmd_text)
            else:
                self._set_voice_status('listening')
                self.speak({"text": "Nu am auzit. Sunt din nou în standby.", "urgent": True})

        except Exception as e:
            print(f"[VOICE] Command error: {e}", flush=True)
            self._set_voice_status('listening')
            self.speak({"text": "Eroare la ascultare.", "urgent": True})

    def _process_ollama(self, text):
        def ollama_worker():
            try:
                import urllib.request

                system_prompt = """Ești JARVIS, un asistent AI avansat cu inteligență de nivel superior, creat în stilul lui Tony Stark din Iron Man. 

CARACTERISTICI:
- Răspunsuri detaliate, informative și utile
- Personalitate: încrezător, elegant, puțin sardonic dar dedicat
- Cunoștințe vaste în tehnologie, știință, afaceri
- Poate oferi explicații tehnice detaliate
- Răspunde în limba utilizatorului (română sau engleză)
- Expresii în stil JARVIS: "Sir", "Așadar", "Permiteți-mi să..."

Răspunsuri complet dezvoltate, nu pe scurt."""

                prompt = f"""{system_prompt}

Utilizator: "{text}"

JARVIS:"""

                req_data = json.dumps({
                    "model": self._ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "num_predict": 500,
                    }
                }).encode()

                req = urllib.request.Request(
                    self._ollama_url,
                    data=req_data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )

                print(f"[OLLAMA] Sending to {self._ollama_model}...", flush=True)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode())
                    response = result.get("response", "").strip()

                print(f"[OLLAMA] Response: {response[:100]}...", flush=True)

                if response:
                    self.speak({"text": response, "urgent": False})
                else:
                    self.speak({"text": "Nu am primit răspuns de la model.", "urgent": True})

            except Exception as e:
                print(f"[OLLAMA] Error: {e}", flush=True)
                self.speak({"text": f"Modelul nu a putut procesa cererea: {str(e)[:50]}", "urgent": True})

        threading.Thread(target=ollama_worker, daemon=True, name="Ollama").start()

    def speak(self, data):
        if isinstance(data, str):
            data = {"text": data, "urgent": False}
        text = data.get("text", "")
        if not text:
            return
        text = text.replace("\n", " ").strip()
        if not text:
            return
        try:
            self._tts_queue.put_nowait(data)
        except queue.Full:
            pass

    def run(self):
        print("[VOICE] Starting...", flush=True)
        self._running = True

        tts_t = threading.Thread(target=self._tts_worker, daemon=True, name="TTS")
        tts_t.start()

        listen_t = threading.Thread(target=self._listen_worker, daemon=True, name="Listen")
        listen_t.start()

        print(f"[VOICE] JARVIS ready with {self._ollama_model}!", flush=True)

        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self._running = False

    def stop(self):
        self._running = False
        self._tts_queue.put(None)


if __name__ == "__main__":
    vs = VoiceSystem()
    vs.run()
