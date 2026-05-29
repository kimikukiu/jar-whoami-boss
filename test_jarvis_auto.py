#!/usr/bin/env python3
"""
JARVIS Auto-Test - Trimite mesaj automat
"""

import urllib.request
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "hermes3:8b"

def chat(message):
    system_prompt = """Ești JARVIS, asistentul AI suprem. Răspunzi scurt, elegant, în română.
Expresii: "Sir", "Așadar"."""

    full_prompt = f"{system_prompt}\n\n{message}\n\nJARVIS:"

    try:
        req_data = json.dumps({
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.8, "num_predict": 200}
        }).encode()

        req = urllib.request.Request(
            OLLAMA_URL,
            data=req_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        print("JARVIS: Trimite cerere la hermes3:8b...")
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result.get("response", "").strip()
    except Exception as e:
        return f"Eroare: {e}"

print("=" * 60)
print("🎖️  JARVIS Auto-Test")
print("=" * 60)

# Trimite salut
print("\nJARVIS: Așteaptă răspuns de la hermes3:8b...\n")

questions = [
    "Bună! Ce poți să faci?",
    "Salut JARVIS! Cum te simți?",
    "Spune-mi despre tine."
]

for q in questions:
    print(f"Tu: {q}")
    response = chat(q)
    print(f"JARVIS: {response}\n")
    time.sleep(1)

print("\n✅ Test complet!")
