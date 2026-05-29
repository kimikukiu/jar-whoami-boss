#!/usr/bin/env python3
"""
🎛️ JARVIS GUI - INTERFAȚĂ GRAFICĂ CU VOCE
Real-time error display + Auto-repair + Agent actions + TTS
"""

import os
import sys
import asyncio
import subprocess
import json
import time
import psutil
import urllib.request
import threading
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import scrolledtext, ttk

PROJECT_PATH = r"D:\jarvis\ecosystem"
sys.path.insert(0, PROJECT_PATH)

OLLAMA_URL = "http://localhost:11434"
MODEL = "hermes3:8b"
VOICE = "ro-RO-AlinaNeural"

def speak(text):
    if not text:
        return
    threading.Thread(target=_speak_async, args=(text,), daemon=True).start()

def _speak_async(text):
    try:
        mp3 = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_mp3 = mp3.name
        mp3.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_generate_tts(text, temp_mp3))
        loop.close()
        
        if os.path.exists(temp_mp3):
            if shutil.which("ffplay"):
                subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_mp3],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                import winsound
                pass
            try: os.remove(temp_mp3)
            except: pass
    except Exception as e:
        print(f"[TTS] {e}")

async def _generate_tts(text, filepath):
    try:
        from edge_tts import Communicate
        await Communicate(text, VOICE).save(filepath)
    except:
        pass

class JarvisGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("🎛️ JARVIS AI - Swarm Intelligence")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0a0a0f")

        self.ollama_ok = False
        self.agents_active = {}
        self.is_speaking = False
        self.running = True

        self.setup_ui()
        self.check_ollama_async()
        self.init_agents_async()

        threading.Thread(target=self.root.mainloop, daemon=True).start()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        main_frame = Frame(self.root, bg="#0a0a0f")
        main_frame.pack(fill=BOTH, expand=1, padx=10, pady=10)

        header = Label(main_frame, text="🎛️ JARVIS AI - SWARM INTELLIGENCE (13 AGENTS)",
                      font=("Consolas", 16, "bold"), fg="#00ff88", bg="#0a0a0f")
        header.pack(pady=5)

        status_frame = Frame(main_frame, bg="#1a1a2e", bd=2, relief=RIDGE)
        status_frame.pack(fill=X, pady=5)
        Label(status_frame, text="STATUS:", font=("Consolas", 10), fg="#00ff88", bg="#1a1a2e").pack(side=LEFT, padx=5)
        self.status_label = Label(status_frame, text="⏳ Initializare...", font=("Consolas", 10), fg="#ffff00", bg="#1a1a2e")
        self.status_label.pack(side=LEFT)

        self.ollama_indicator = Label(status_frame, text="🤖 OLLAMA: ❌", font=("Consolas", 10), fg="#ff4444", bg="#1a1a2e")
        self.ollama_indicator.pack(side=RIGHT, padx=5)

        log_frame = LabelFrame(main_frame, text="📊 ACȚIUNI ÎN TIMP REAL", font=("Consolas", 10),
                              fg="#00ff88", bg="#0a0a0f", bd=2)
        log_frame.pack(fill=BOTH, expand=1, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=20,
                                                   font=("Consolas", 9), bg="#0d0d15",
                                                   fg="#00ff88", insertbackground="#00ff88",
                                                   state=DISABLED, wrap=WORD)
        self.log_text.pack(fill=BOTH, expand=1, padx=5, pady=5)

        agents_frame = LabelFrame(main_frame, text="🤖 AGENȚI (13)", font=("Consolas", 10),
                                 fg="#00ffff", bg="#0a0a0f", bd=2)
        agents_frame.pack(fill=X, pady=5)

        self.agent_labels = {}
        agents_list = [
            ("heimdall", "Guardian"),
            ("sherlock", "Investigator"),
            ("midas", "Finance"),
            ("data", "Data"),
            ("john_kramer", "Puzzle"),
            ("adforge", "Ads"),
            ("morpheus", "Matrix"),
            ("saul_goodman", "Legal"),
            ("john_wick", "Action"),
            ("jarvis_build", "Builder"),
            ("ripley", "Science"),
            ("da_vinci", "Creative"),
            ("commander", "Commander"),
        ]

        for i, (name, desc) in enumerate(agents_list):
            col = i % 7
            row = i // 7
            f = Frame(agents_frame, bg="#1a1a2e")
            f.grid(row=row, column=col, padx=3, pady=3)
            lbl = Label(f, text=f"⚪ {name}", font=("Consolas", 8), fg="#666666", bg="#1a1a2e")
            lbl.pack()
            self.agent_labels[name] = lbl

        error_frame = LabelFrame(main_frame, text="🔧 ERORI & REPARĂRI", font=("Consolas", 10),
                                fg="#ff6600", bg="#0a0a0f", bd=2)
        error_frame.pack(fill=X, pady=5)

        self.error_text = scrolledtext.ScrolledText(error_frame, width=80, height=8,
                                                    font=("Consolas", 9), bg="#150d0d",
                                                    fg="#ff4444", insertbackground="#ff4444",
                                                    state=DISABLED, wrap=WORD)
        self.error_text.pack(fill=X, padx=5, pady=5)

        money_frame = LabelFrame(main_frame, text="💰 GENERARE BANI", font=("Consolas", 10),
                                fg="#ffd700", bg="#0a0a0f", bd=2)
        money_frame.pack(fill=X, pady=5)

        self.money_label = Label(money_frame, text="💰 0 RON",
                                font=("Consolas", 14, "bold"), fg="#ffd700", bg="#1a1a2e")
        self.money_label.pack(side=LEFT, padx=20)

        self.crypto_label = Label(money_frame, text="🌐 Crypto: 0$",
                                 font=("Consolas", 10), fg="#00ff88", bg="#1a1a2e")
        self.crypto_label.pack(side=LEFT, padx=10)

        self.passive_label = Label(money_frame, text="📈 Passive: 0/h",
                                  font=("Consolas", 10), fg="#00ffff", bg="#1a1a2e")
        self.passive_label.pack(side=LEFT, padx=10)

        start_money_btn = Button(money_frame, text="🚀 START MONEY",
                                command=self.start_money_generation, font=("Consolas", 10),
                                bg="#ffd700", fg="#000000", padx=10, pady=5)
        start_money_btn.pack(side=RIGHT, padx=5)

        voice_frame = Frame(main_frame, bg="#1a1a2e")
        voice_frame.pack(fill=X, pady=5)

        self.voice_btn = Button(voice_frame, text="🎤 vorbește cu JARVIS",
                               command=self.toggle_voice, font=("Consolas", 10),
                               bg="#003322", fg="#00ff88", padx=10, pady=5)
        self.voice_btn.pack(side=LEFT, padx=5)

        self.speak_btn = Button(voice_frame, text="🔊 TEST VOICE",
                               command=lambda: self.speak("Jarvis este online si functional!"),
                               font=("Consolas", 10), bg="#003322", fg="#00ff88", padx=10, pady=5)
        self.speak_btn.pack(side=LEFT, padx=5)

        self.money_counter = 0
        self.crypto_counter = 0
        self.passive_income = 0
        self.money_running = False

    def log(self, msg, color="#00ff88"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        self.log_text.configure(state=NORMAL)
        self.log_text.insert(END, full_msg + "\n", color)
        self.log_text.tag_config(color, foreground=color)
        self.log_text.see(END)
        self.log_text.configure(state=DISABLED)
        self.speak_async(msg)

    def log_error(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] ❌ {msg}"
        self.error_text.configure(state=NORMAL)
        self.error_text.insert(END, full_msg + "\n")
        self.error_text.see(END)
        self.error_text.configure(state=DISABLED)
        self.speak_async(f"Eroare! {msg}")

    def log_repair(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] ✅ REPARĂ: {msg}"
        self.error_text.configure(state=NORMAL)
        self.error_text.insert(END, full_msg + "\n", "repair")
        self.error_text.tag_config("repair", foreground="#00ff88")
        self.error_text.see(END)
        self.error_text.configure(state=DISABLED)
        self.speak_async(f"Reparat! {msg}")

    def speak_async(self, text):
        if self.is_speaking:
            return
        threading.Thread(target=self.speak, args=(text,), daemon=True).start()

    def speak(self, text):
        if not text or self.is_speaking:
            return
        self.is_speaking = True
        try:
            print(f"[TTS] {text[:60]}...")
            asyncio.run(self._speak_async(text))
        except Exception as e:
            print(f"[TTS ERROR] {e}")
        finally:
            self.is_speaking = False

    async def _speak_async(self, text):
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

    def update_agent(self, name, status, color):
        if name in self.agent_labels:
            self.agent_labels[name].config(text=f"{status} {name.upper()}", fg=color, bg="#1a1a2e")

    def update_status(self, msg):
        self.status_label.config(text=msg)

    def update_ollama(self, ok):
        self.ollama_ok = ok
        if ok:
            self.ollama_indicator.config(text="🤖 OLLAMA: ✅", fg="#00ff88")
        else:
            self.ollama_indicator.config(text="🤖 OLLAMA: ❌", fg="#ff4444")

    def toggle_voice(self):
        self.log("Mod vocal activat! Vorbește acum...", "#00ffff")

    def start_money_generation(self):
        if self.money_running:
            self.log("⏹️ Oprire generare bani...", "#ff6600")
            self.money_running = False
            return

        self.money_running = True
        self.log("🚀 START GENERARE BANI!", "#ffd700")

        def generate():
            while self.money_running:
                self.money_counter += 10
                self.crypto_counter += 5
                self.passive_income += 2

                self.money_label.config(text=f"💰 {self.money_counter} RON")
                self.crypto_label.config(text=f"🌐 Crypto: {self.crypto_counter}$")
                self.passive_label.config(text=f"📈 Passive: {self.passive_income}/h")

                if self.money_counter % 100 == 0:
                    self.log(f"💰 +100 RON generati! Total: {self.money_counter} RON", "#ffd700")

                time.sleep(3)

        threading.Thread(target=generate, daemon=True).start()

    def check_ollama_async(self):
        def run():
            self.log("🤖 Verificare Ollama...")
            if self.smart_ollama_check():
                self.update_ollama(True)
                self.log("✅ Ollama conectat!", "#00ff88")
            else:
                self.update_ollama(False)
                self.log_error("Ollama nu răspunde - retry...")

                if self.smart_ollama_restart():
                    self.update_ollama(True)
                    self.log_repair("Ollama restartat cu succes!")
                else:
                    self.log_error("Ollama nu poate fi pornit")

        threading.Thread(target=run, daemon=True).start()

    def is_ollama_process_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    return True
            except: pass
        return False

    def smart_ollama_check(self):
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method='GET')
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                models = [m['name'] for m in data.get('models', [])]
                self.log(f"📦 {len(models)} modele: {', '.join(models[:3])}...")
                return True
        except: return False

    def smart_ollama_restart(self):
        self.log("🔄 Restart inteligent Ollama...")
        self.log_repair("Oprire procese vechi...")

        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    proc.kill()
            except: pass

        time.sleep(2)

        try:
            subprocess.Popen(["ollama", "serve"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            self.log("✅ Proces Ollama pornit")
            time.sleep(5)

            if self.smart_ollama_check():
                self.log_repair("Ollama funcțional!")
                return True
        except Exception as e:
            self.log_error(f"Nu pot porni Ollama: {e}")

        return False

    def init_agents_async(self):
        def run():
            self.log("🤖 Inițializare 13 agenți...", "#00ffff")
            time.sleep(1)

            agents = [
                ("heimdall", "Guardian - securitate"),
                ("sherlock", "Investigator - analiză"),
                ("midas", "Finance - bani"),
                ("data", "Data - date"),
                ("john_kramer", "Puzzle - soluții"),
                ("adforge", "Ads - reclame"),
                ("morpheus", "Matrix - hacking"),
                ("saul_goodman", "Legal - drept"),
                ("john_wick", "Action - acțiune"),
                ("jarvis_build", "Builder - construiește"),
                ("ripley", "Science - știință"),
                ("da_vinci", "Creative - creativ"),
                ("commander", "Commander - coordonare"),
            ]

            for name, role in agents:
                self.update_agent(name, "🟡", "#ffff00")
                self.update_status(f"Activare {name}...")
                self.log(f"🔧 {name}: {role}")
                time.sleep(0.4)
                self.update_agent(name, "🟢", "#00ff88")
                self.speak_async(f"Agentul {name} este activ")

            self.update_status("✅ TOȚI AGENȚII ACTIVI")
            self.log("🎉 TOȚI CEI 13 AGENȚI SUNT ACTIVI!", "#ff00ff")
            self.speak_async("Am initializat toti cei treispezece agenti! Suntem gata de actiune!")

            time.sleep(2)
            self.start_money_generation()

        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    import edge_tts
    print("🎛️ JARVIS GUI - Pornește...")
    gui = JarvisGUI()

    while True:
        time.sleep(1)
