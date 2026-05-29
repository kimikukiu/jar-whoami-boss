#!/usr/bin/env python3
"""
JARVIS - Self-Repairing AI Agent
Primește comenzi și își repară/actualizează singur proiectul
"""

import os
import sys
import urllib.request
import json
import subprocess
import re
from pathlib import Path

# Config
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "hermes3:8b"
PROJECT_PATH = r"D:\jarvis\ecosystem"

def chat_ollama(message):
    """Trimite mesaj la Ollama"""
    system_prompt = """Ești JARVIS, un agent AI autonom. Analizezi cod, găsești erori și le repari.
Când primești o comandă:
1. Înțelegi ce trebuie făcut
2. Identifici fișierele afectate
3. Repari sau actualizezi codul
4. Raportezi ce ai făcut

Răspunzi scurt și la obiect. Expresii: "Sir", "Așadar"."""

    full_prompt = f"{system_prompt}\n\n{message}\n\nJARVIS:"

    try:
        req_data = json.dumps({
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 300}
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
        return f"Eroare Ollama: {e}"

def find_and_fix_errors():
    """Găsește și repară erorile din proiect"""
    print("\n[JARVIS] Scanez proiectul pentru erori...")

    errors_found = []
    fixed_count = 0

    # Python files
    py_files = list(Path(PROJECT_PATH).rglob("*.py"))
    print(f"[JARVIS] Găsite {len(py_files)} fișiere Python")

    for py_file in py_files[:20]:  # Primele 20
        try:
            content = py_file.read_text(encoding='utf-8')

            # Verifică erori comune
            if "" in content:
                errors_found.append(f"{py_file}: Conține '' (probabil Tailwind invalid)")
                content = content.replace("", "")
                py_file.write_text(content, encoding='utf-8')
                fixed_count += 1

            if "Expected expression" in content:
                errors_found.append(f"{py_file}: Syntax error")

        except Exception as e:
            errors_found.append(f"{py_file}: {e}")

    # JS/JSX files
    js_files = list(Path(PROJECT_PATH).rglob("*.jsx")) + list(Path(PROJECT_PATH).rglob("*.js"))
    print(f"[JARVIS] Găsite {len(js_files)} fișiere JS/JSX")

    for js_file in js_files[:20]:
        try:
            content = js_file.read_text(encoding='utf-8')

            if "" in content or "lwind" in content:
                errors_found.append(f"{js_file}: Conține directive Tailwind invalide")
                # Remove lwind directives
                content = re.sub(r'lwind[^\n]*\n', '', content)
                content = re.sub(r'[^\n]*\n', '', content)
                js_file.write_text(content, encoding='utf-8')
                fixed_count += 1

        except Exception as e:
            errors_found.append(f"{js_file}: {e}")

    return errors_found, fixed_count

def execute_command(command):
    """Execută o comandă dată de utilizator"""
    print(f"\n[JARVIS] Execut: {command}")

    # Comenzi speciale
    if "scaneaz" in command.lower() or "caută erori" in command.lower():
        errors, fixed = find_and_fix_errors()
        response = f"Am găsit {len(errors)} erori și am reparat {fixed}."
        return response

    if "git push" in command.lower() or "push" in command.lower():
        try:
            subprocess.run("git add .", shell=True, cwd=PROJECT_PATH)
            subprocess.run('git commit -m "JARVIS Auto-Update"', shell=True, cwd=PROJECT_PATH)
            subprocess.run("git push origin main --force", shell=True, cwd=PROJECT_PATH, capture_output=True)
            return "Push efectuat cu succes!"
        except Exception as e:
            return f"Eroare git: {e}"

    if "build" in command.lower() or "npm run build" in command.lower():
        try:
            result = subprocess.run("npm run build", shell=True, cwd=f"{PROJECT_PATH}\\frontend", capture_output=True, text=True)
            if result.returncode == 0:
                return "Build reușit!"
            else:
                return f"Build failed: {result.stderr[:200]}"
        except Exception as e:
            return f"Eroare build: {e}"

    if "update" in command.lower():
        # Folosește AI pentru a decide ce actualizări să faci
        prompt = f"Utilizatorul vrea să actualizeze proiectul. Comanda: {command}. Ce fișiere trebuie modificate?"
        response = chat_ollama(prompt)
        return response

    # Pentru alte comenzi, folosește AI
    return chat_ollama(command)

def main():
    print("\n" + "="*60)
    print("🎖️  JARVIS - SELF-REPAIRING AGENT")
    print("="*60)
    print(f"Project: {PROJECT_PATH}")
    print(f"Model: {MODEL}")
    print("\nComenzi disponibile:")
    print("  - 'scanează erori' / 'caută erori' - repară erorile")
    print("  - 'git push' - face push la GitHub")
    print("  - 'build' - face npm run build")
    print("  - orice altă comandă - JARVIS decide ce face")
    print("\nScrie comanda ta:")
    print("="*60 + "\n")

    while True:
        try:
            user_input = input("Tu: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "gata"]:
                print("JARVIS: La revedere, Sir!")
                break

            print("\n[JARVIS] Procesez...")
            response = execute_command(user_input)
            print(f"\nJARVIS: {response}\n")

        except KeyboardInterrupt:
            print("\n\nJARVIS: La revedere, Sir!")
            break
        except Exception as e:
            print(f"\n[JARVIS] Eroare: {e}\n")

if __name__ == "__main__":
    main()
