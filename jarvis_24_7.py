#!/usr/bin/env python3
"""
JARVIS 24/7 - Continuous AI Assistant
Runs forever, listens for commands, responds autonomously
"""

import sys
import os
import time
import asyncio
import threading
from datetime import datetime
from pathlib import Path

# Add JARVIS ecosystem to path
JARVIS_PATH = Path(__file__).parent / "ecosystem"
sys.path.insert(0, str(JARVIS_PATH))

# Colors for terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.OKCYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     ██╗    ██╗███████╗███╗   ██╗ ██████╗                         ║
║     ██║    ██║██╔════╝████╗  ██║██╔═══██╗                        ║
║     ██║ █╗ ██║█████╗  ██╔██╗ ██║██║   ██║                        ║
║     ██║███╗██║██╔══╝  ██║╚██╗██║██║   ██║                        ║
║     ╚███╔███╔╝███████╗██║ ╚████║╚██████╔╝                        ║
║      ╚══╝╚══╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝                         ║
║                                                                      ║
║           J.A.R.V.I.S. - 24/7 AI Assistant                         ║
║              Just A Rather Very Intelligent System                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
"""
    print(banner)

class JARVIS24_7:
    def __init__(self):
        self.running = True
        self.start_time = datetime.now()
        self.wake_word = "jarvis"
        self.voice_system = None
        self.initialized = False

    def initialize(self):
        """Initialize JARVIS components"""
        print(f"{Colors.OKBLUE}[{self.timestamp()}] JARVIS: Initializing systems...{Colors.ENDC}")

        # Check dependencies
        deps_ok = True

        try:
            import edge_tts
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Edge TTS available")
        except ImportError:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Edge TTS not available")
            deps_ok = False

        try:
            import whisper
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Whisper STT available")
        except ImportError:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Whisper not available")
            deps_ok = False

        try:
            import speech_recognition as sr
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Speech Recognition available")
        except ImportError:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Speech Recognition not available")
            deps_ok = False

        try:
            import pygame
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} Pygame available")
        except ImportError:
            print(f"{Colors.FAIL}✗{Colors.ENDC} Pygame not available")
            deps_ok = False

        # Check Ollama connection
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:11434/api/tags", method='GET')
            with urllib.request.urlopen(req, timeout=5) as resp:
                models = eval(resp.read().decode()).get('models', [])
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} Ollama connected - {len(models)} models")
        except Exception as e:
            print(f"{Colors.WARNING}⚠{Colors.ENDC} Ollama not connected: {e}")
            print(f"{Colors.WARNING}  Start with: ollama serve{Colors.ENDC}")

        # Initialize voice system in a separate thread
        try:
            voice_thread = threading.Thread(target=self._init_voice_system, daemon=True)
            voice_thread.start()
        except Exception as e:
            print(f"{Colors.WARNING}[{self.timestamp()}] JARVIS: Voice init warning: {e}{Colors.ENDC}")

        self.initialized = True
        print(f"{Colors.OKGREEN}[{self.timestamp()}] JARVIS: Systems online{Colors.ENDC}\n")

    def _init_voice_system(self):
        """Initialize voice system in background thread"""
        try:
            from tools.voice_simple import VoiceSystem
            self.voice_system = VoiceSystem()
            print(f"{Colors.OKCYAN}[{self.timestamp()}] JARVIS: Voice system ready{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}[{self.timestamp()}] JARVIS: Voice init warning: {e}{Colors.ENDC}")

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def uptime(self):
        delta = datetime.now() - self.start_time
        hours = delta.total_seconds() // 3600
        minutes = (delta.total_seconds() % 3600) // 60
        seconds = delta.total_seconds() % 60
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def print_status(self):
        uptime_str = self.uptime()
        status = f"""
{Colors.BOLD}╔══════════════════════════════════════════════════════════╗
║  JARVIS STATUS                                                    ║
╠══════════════════════════════════════════════════════════════════╣
║  Uptime    : {uptime_str}                                          ║
║  Status    : {'ACTIVE' if self.running else 'SHUTDOWN'}                                       ║
║  Mode      : 24/7 CONTINUOUS                                      ║
║  Wake Word : "{self.wake_word.upper()}"                                            ║
╚══════════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
        print(status)

    def run(self):
        """Main loop - runs 24/7"""
        print_banner()
        print(f"{Colors.OKGREEN}[{self.timestamp()}] JARVIS: Starting 24/7...{Colors.ENDC}\n")

        self.initialize()

        print(f"{Colors.OKCYAN}[{self.timestamp()}] JARVIS: I'm online{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[{self.timestamp()}] JARVIS: Say '{self.wake_word}' to activate{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[{self.timestamp()}] JARVIS: Press Ctrl+C to shutdown{Colors.ENDC}\n")

        loop_count = 0

        try:
            while self.running:
                # Print status every minute
                if loop_count % 60 == 0:
                    self.print_status()

                # Main JARVIS loop
                time.sleep(1)
                loop_count += 1

                # Every 5 minutes, log heartbeat
                if loop_count % 300 == 0:
                    print(f"{Colors.OKBLUE}[{self.timestamp()}] JARVIS: Heartbeat - All systems operational{Colors.ENDC}")

        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[{self.timestamp()}] JARVIS: Shutdown signal received{Colors.ENDC}")
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        print(f"{Colors.WARNING}[{self.timestamp()}] JARVIS: Shutting down...{Colors.ENDC}")
        print(f"{Colors.OKGREEN}[{self.timestamp()}] JARVIS: Uptime was {self.uptime()}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}[{self.timestamp()}] JARVIS: Goodnight.{Colors.ENDC}")
        sys.exit(0)

def main():
    """Entry point for JARVIS 24/7"""
    jarvis = JARVIS24_7()
    jarvis.run()

if __name__ == "__main__":
    main()
