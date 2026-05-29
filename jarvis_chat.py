#!/usr/bin/env python3
"""
JARVIS + hermes3:8b - Chat simplu în terminal
Lucrează direct cu Ollama
"""

import urllib.request
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "hermes3:8b"

def chat_with_jarvis(message):
    """Trimite mesaj la Ollama"""
    system_prompt = """Ești JARVIS, asistentul AI suprem. Răspunzi scurt, elegant, în română.
Expresii: "Sir", "Așadar". Ești de ajutor și inteligen."""

    full_prompt = f"{system_prompt}\n\nUtilizator: {message}\n\nJARVIS:"

    try:
        req_data = json.dumps({
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.8, "top_p": 0.9, "num_predict": 200}
        }).encode()

        req = urllib.request.Request(
            OLLAMA_URL,
            data=req_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result.get("response", "").strip()

    except Exception as e:
        return f"Eroare: {e}"

print("=" * 60)
print("🎖️  JARVIS + hermes3:8b")
print("=" * 60)
print("Scrie mesajul tău și JARVIS va răspunde!")
print("Scrie 'exit' pentru a ieși.\n")

while True:
    try:
        user_input = input("Tu: ")
        if user_input.lower() in ["exit", "quit", "gata"]:
            print("JARVIS: La revedere, Sir!")
            break

        if user_input.strip():
            print("JARVIS: ", end="", flush=True)
            response = chat_with_jarvis(user_input)
            print(response)
            print()

    except KeyboardInterrupt:
        print("\nJARVIS: La revedere, Sir!")
        break
