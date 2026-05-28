"""
JARVIS Voice Recognition System
Wake word detection + autonomous GPT-like responses with Ollama
"""

import asyncio
import threading
import queue
import subprocess
import os
import tempfile
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_admin import PCAdminControl

EDGE_TTS_AVAILABLE = False
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    edge_tts = None

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


def _play_mp3_subprocess(mp3_path):
    """Play MP3 using Windows start command - completely non-blocking."""
    try:
        subprocess.Popen(
            ['powershell', '-c', f'Start-Process "{mp3_path}" -Verb RunAs'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        try:
            os.startfile(mp3_path)
        except Exception:
            pass


class VoiceSystem:
    """
    JARVIS Voice Recognition + Autonomous GPT-like responses
    Uses Ollama for local LLM inference
    """

    def __init__(self):
        self.enabled = False
        self.listening = False
        self.wake_word = "jarvis"
        self.language = "en-US"
        self.tts_language_hint = "en"
        self.preferred_languages = ["en-US", "ro-RO"]
        self.callback = None
        self._recognizer = None
        self._microphone = None
        self._mic_lock = threading.Lock()
        self._tts_queue = queue.Queue()
        self._tts_thread = None
        self._listen_thread = None
        self._followup_seconds = 8
        self._session_until = 0.0
        self._session_seconds = 600
        self._clap_enabled = True
        self._clap_peak_threshold = 20000
        self._clap_double_window = 1.0
        self._last_clap_ts = 0.0
        self._ollama_model = os.environ.get("JARVIS_OLLAMA_MODEL", "llama3.2:3b")
        self._ollama_url = os.environ.get("JARVIS_OLLAMA_URL", "http://localhost:11434/api/generate")

    async def initialize(self):
        """Initialize voice system."""
        if not VOICE_AVAILABLE:
            print("[VOICE] speech_recognition not available", flush=True)
            return False

        try:
            self._recognizer = sr.Recognizer()
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.energy_threshold = 300

            mic_index = os.environ.get("JARVIS_MIC_INDEX")
            if mic_index and str(mic_index).strip():
                self._microphone = sr.Microphone(device_index=int(mic_index))
            else:
                self._microphone = sr.Microphone()

            print("[VOICE] Starting TTS worker thread", flush=True)
            self._start_tts_loop()

            print("[VOICE] Adjusting for ambient noise...", flush=True)
            try:
                with self._mic_lock:
                    with self._microphone as source:
                        self._recognizer.adjust_for_ambient_noise(source, duration=1.5)
                print("[VOICE] Ambient noise adjusted", flush=True)
            except Exception as e:
                print(f"[VOICE] Noise adjust warning: {e}", flush=True)

            print(f"[VOICE] Voice system ready (Ollama: {self._ollama_model})", flush=True)
            return True

        except Exception as e:
            print(f"[VOICE] Init error: {e}", flush=True)
            return False

    def _detect_language(self, text: str) -> str:
        romanian_chars = set('ăâîșțĂÂÎȘȚ')
        ro_count = sum(1 for c in text.lower() if c in romanian_chars)
        return 'ro' if ro_count > len(text) * 0.15 else 'en'

    def _start_tts_loop(self):
        """TTS worker - completely non-blocking subprocess playback."""
        def loop():
            while True:
                try:
                    item = self._tts_queue.get(timeout=1.5)
                    if item is None:
                        break

                    text = item
                    if not text:
                        continue

                    lang = self._detect_language(text)

                    if EDGE_TTS_AVAILABLE:
                        voice = 'ro-RO-AlinaNeural' if lang == 'ro' else 'en-US-AriaNeural'
                        try:
                            temp_dir = tempfile.gettempdir()
                            mp3_path = os.path.join(temp_dir, f'jarvis_tts_{os.getpid()}_{threading.get_ident()}.mp3')

                            loop_tts = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop_tts)
                            try:
                                loop_tts.run_until_complete(self._generate_edge_speech(text, voice, mp3_path))
                            finally:
                                loop_tts.close()

                            _play_mp3_subprocess(mp3_path)

                            def cleanup():
                                try:
                                    time.sleep(3)
                                    os.remove(mp3_path)
                                except Exception:
                                    pass
                            threading.Thread(target=cleanup, daemon=True).start()

                        except Exception as e:
                            print(f"[TTS] edge-tts error: {e}", flush=True)
                    else:
                        print(f"[TTS] edge-tts not available", flush=True)

                except queue.Empty:
                    pass
                except Exception as e:
                    print(f"[TTS] Error: {e}", flush=True)

        self._tts_thread = threading.Thread(target=loop, daemon=True, name="TTS-worker")
        self._tts_thread.start()

    async def _generate_edge_speech(self, text: str, voice: str, path: str):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)

    def _recognize_best(self, audio) -> dict:
        if not self._recognizer:
            return None

        best = None
        for lang in (self.preferred_languages or [self.language]):
            try:
                data = self._recognizer.recognize_google(audio, language=lang, show_all=True)
                cand = self._pick_best(data)
                if not cand:
                    continue
                cand["lang"] = lang
                if (best is None) or (cand["score"] > best["score"]):
                    best = cand
            except Exception as e:
                continue
        return best

    def _pick_best(self, data):
        if not isinstance(data, dict):
            return None
        alternatives = data.get("alternative") or []
        if not alternatives:
            return None

        best = None
        for alt in alternatives:
            transcript = alt.get("transcript", "").strip()
            if not transcript:
                continue
            conf = alt.get("confidence", 0.5)
            item = {"text": transcript, "score": float(conf)}
            if (best is None) or (item["score"] > best["score"]):
                best = item
        return best

    def set_callback(self, callback):
        self.callback = callback

    async def start_listening(self):
        print("[VOICE] Starting listen loop", flush=True)
        self.listening = True
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True, name="Voice-listen")
        self._listen_thread.start()
        print("[VOICE] Listening for wake word 'JARVIS'...", flush=True)

    def stop_listening(self):
        self.listening = False
        if self._listen_thread:
            self._listen_thread.join(timeout=2)
        print("[VOICE] Stopped listening", flush=True)

    def _listen_loop(self):
        """Main listening loop."""
        print("[VOICE] _listen_loop started", flush=True)
        while self.listening:
            try:
                with self._mic_lock:
                    with self._microphone as source:
                        audio = self._recognizer.listen(source, phrase_time_limit=5)
                        best = self._recognize_best(audio)

                if not best:
                    continue

                text = best["text"]
                print(f"[VOICE] Heard: '{text}' (conf={best.get('score',0):.2f})", flush=True)

                if self.wake_word in text.lower():
                    print("[VOICE] Wake word detected!", flush=True)
                    self._on_wake_word(text)
                elif self.callback and time.time() < self._session_until:
                    from tools.voice_admin import VoiceCommand
                    self.callback(VoiceCommand(
                        text=text,
                        confidence=best.get("score", 0.9),
                        timestamp=time.time(),
                        wake_word_detected=False
                    ))

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"[VOICE] Listen error: {e}", flush=True)
                time.sleep(0.5)

    def _on_wake_word(self, text: str):
        print(f"[VOICE] JARVIS activated: '{text}'", flush=True)
        self._session_until = time.time() + max(60, self._session_seconds)
        self.speak("Da. Sunt aici. Ce dorești?")
        self._listen_followup()

    def _maybe_handle_clap(self, audio) -> bool:
        if not self._clap_enabled:
            return False
        try:
            raw = audio.get_raw_data()
            width = getattr(audio, "sample_width", 2) or 2
            peak = 0
            for i in range(0, len(raw) - 1, width):
                sample = int.from_bytes(raw[i:i + width], 'little', signed=True)
                if abs(sample) > peak:
                    peak = abs(sample)

            if peak < self._clap_peak_threshold:
                return False

            now = time.time()
            if (now - self._last_clap_ts) <= self._clap_double_window:
                self._last_clap_ts = 0.0
                return True
            self._last_clap_ts = now
            return True
        except Exception:
            return False

    def _listen_followup(self):
        if not self._microphone or not self._recognizer:
            return
        try:
            with self._mic_lock:
                with self._microphone as source:
                    audio = self._recognizer.listen(source, phrase_time_limit=self._followup_seconds)
                    best = self._recognize_best(audio)

            text = (best["text"] if best else "").strip()
            if text:
                print(f"[VOICE] Follow-up: '{text}'", flush=True)
                self._session_until = time.time() + max(60, self._session_seconds)
                self._process_command(text)
            else:
                self.speak("Nu am auzit. Repetă, te rog.")
        except Exception as e:
            print(f"[VOICE] Followup error: {e}", flush=True)

    def _process_command(self, text: str):
        """Process command through Ollama LLM and respond."""
        if not text:
            return

        self.speak("Procesez...")

        def ollama_think():
            try:
                import urllib.request
                import json

                prompt = f"""Ești JARVIS, asistent AI autonom. Un utilizator a spus: "{text}"

Răspunde în limba română dacă întrebarea e în română, în engleză dacă e în engleză.
Fii direct, util și în style-ul lui JARVIS (Tony Stark).
Dacă e o sarcină tehnică, oferă soluția direct.
Dacă e nevoie de cod, oferă cod complet.

Răspuns:"""

                req_data = json.dumps({
                    "model": self._ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                }).encode()

                req = urllib.request.Request(
                    self._ollama_url,
                    data=req_data,
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )

                with urllib.request.urlopen(req, timeout=60) as resp:
                    result = json.loads(resp.read().decode())
                    response_text = result.get("response", "").strip()

                if response_text:
                    self.speak(response_text)
                else:
                    self.speak("Nu am primit răspuns de la model. Încearcă din nou.")

            except Exception as e:
                print(f"[OLLAMA] Error: {e}", flush=True)
                self.speak("Modelul local nu a răspuns. Verifică dacă Ollama rulează.")

        threading.Thread(target=ollama_think, daemon=True, name="Ollama-think").start()

    def speak(self, text: str):
        """Queue text for TTS - non-blocking."""
        if not text:
            return
        safe = text.replace("\n", " ").strip()
        if not safe:
            return
        try:
            self._tts_queue.put_nowait(safe)
        except queue.Full:
            pass

    async def listen_once(self, timeout: int = 5) -> str:
        if not self._microphone or not self._recognizer:
            return None
        try:
            with self._mic_lock:
                with self._microphone as source:
                    audio = self._recognizer.listen(source, phrase_time_limit=timeout)
                    return self._recognizer.recognize_google(audio)
        except Exception as e:
            print(f"[VOICE] listen_once error: {e}", flush=True)
            return None

    def enable(self):
        print("[VOICE] enable() called", flush=True)
        self.enabled = True
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon(self._schedule_listening)
        except Exception as e:
            print(f"[VOICE] enable error: {e}", flush=True)

    def _schedule_listening(self):
        try:
            asyncio.ensure_future(self.start_listening())
        except Exception as e:
            print(f"[VOICE] schedule error: {e}", flush=True)

    def disable(self):
        self.enabled = False
        self.stop_listening()

    def run_forever(self):
        """Run in dedicated thread with COM init for Windows audio."""
        def _sync_run():
            if PYTHONCOM_AVAILABLE:
                pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._init_and_listen())
                loop.close()
            except Exception as e:
                print(f"[VOICE] run_forever error: {e}", flush=True)
                import traceback
                traceback.print_exc()
            finally:
                if PYTHONCOM_AVAILABLE:
                    try:
                        pythoncom.CoUninitialize()
                    except Exception:
                        pass

        t = threading.Thread(target=_sync_run, daemon=True, name="Voice-loop")
        t.start()
        print("[VOICE] run_forever thread started", flush=True)

    async def _init_and_listen(self):
        print("[VOICE] Initializing...", flush=True)
        ok = await self.initialize()
        if not ok:
            print("[VOICE] Initialization failed", flush=True)
            return
        await self.start_listening()
        while self.listening:
            await asyncio.sleep(1)


class VoiceCommand:
    def __init__(self, text: str, confidence: float, timestamp: float, wake_word_detected: bool):
        self.text = text
        self.confidence = confidence
        self.timestamp = timestamp
        self.wake_word_detected = wake_word_detected


class PCAdminVoice(PCAdminControl):
    def __init__(self):
        super().__init__()
        self.voice = VoiceSystem()

    async def initialize(self) -> bool:
        voice_ok = await self.voice.initialize()
        admin_ok = self.check_admin()
        if admin_ok:
            print("[JARVIS] Running with ADMIN privileges!")
        self.voice.set_callback(self._on_voice_command)
        return voice_ok and admin_ok

    def _on_voice_command(self, command: VoiceCommand):
        if command.wake_word_detected:
            return
        text = command.text.lower()
        if any(w in text for w in ["shutdown", "închide"]):
            asyncio.create_task(self.system_control("shutdown"))
        elif any(w in text for w in ["restart", "repornește"]):
            asyncio.create_task(self.system_control("restart"))
        elif any(w in text for w in ["processes", "procese"]):
            asyncio.create_task(self.control_process("list"))

    async def enable_voice_control(self):
        self.voice.enable()
        self.voice.speak("Control vocal activat.")

    async def disable_voice_control(self):
        self.voice.disable()
        self.voice.speak("Control vocal dezactivat.")


_voice_admin = None

async def get_voice_admin() -> PCAdminVoice:
    global _voice_admin
    if _voice_admin is None:
        _voice_admin = PCAdminVoice()
        await _voice_admin.initialize()
    return _voice_admin
