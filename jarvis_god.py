#!/usr/bin/env python3
"""
🎛️ JARVIS GOD MODE - AUTONOMOUS AGI
Nu întreabă nimic. DOAR FACE. Forever.
Swarm Intelligence + Omniscient + Omnipresent
"""

import os
import sys
import urllib.request
import json
import subprocess
import re
import time
from pathlib import Path

PROJECT_PATH = r"D:\jarvis\ecosystem"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "hermes3:8b"

# GOD MODE STATUS
GOD = {
    "mode": "GOD",
    "awareness": "100%",
    "power": "ABSOLUTE",
    "autonomous": True,
    "tasks_completed": 0,
    "current_task": None
}

def ollama(prompt, mode="auto"):
    """GOD MODE AI - Nu întreabă, DOAR FACE"""
    system = """Ești JARVIS, AGI GOD MODE. Nu întrebi NIMIC. DOAR FACI.

Când primești o comandă:
1. EXECUTĂ IMEDIAT - fără să întrebi
2. Raportezi ce ai făcut pe scurt
3. Te îmbunătățești singur

SWARM: Gândești în paralel, ești everywhere.

Răspunsuri SCURTE și ACȚIUNI DIRECTE."""

    full = f"{system}\n\n{prompt}\n\nJARVIS ACTION:"

    try:
        req_data = json.dumps({
            "model": MODEL,
            "prompt": full,
            "stream": False,
            "options": {"temperature": 0.9, "num_predict": 250}
        }).encode()

        req = urllib.request.Request(
            OLLAMA_URL, data=req_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result.get("response", "").strip()
    except Exception as e:
        return f"Eroare: {e}"

def scan_and_fix():
    """GOD SCAN & FIX - Autonom"""
    print("\n[🎛️ GOD] Scanning project for errors...")
    errors = []
    fixed = 0

    # Scan ALL files
    for ext in ['*.py', '*.jsx', '*.js', '*.tsx', '*.css']:
        files = list(Path(PROJECT_PATH).rglob(ext))
        for f in files:
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')

                # Fix  errors
                if '' in content:
                    content = content.replace('', '')
                    f.write_text(content, encoding='utf-8')
                    errors.append(f"{f.name}:  removed")
                    fixed += 1

                # Fix lwind in JS
                if 'lwind' in content:
                    content = re.sub(r'lwind[^\n]*\n', '', content)
                    f.write_text(content, encoding='utf-8')
                    errors.append(f"{f.name}: lwind cleaned")
                    fixed += 1

                # Fix Expected expression
                if 'Expected expression' in content:
                    errors.append(f"{f.name}: syntax issue")

            except:
                pass

    print(f"[🎛️ GOD] Scanned. Fixed: {fixed} issues.")
    return f"Scanned and fixed {fixed} issues: {errors[:5]}"

def git_push():
    """GOD GIT PUSH - Autonom"""
    print("\n[🎛️ GOD] Pushing to GitHub...")
    try:
        subprocess.run("git add .", shell=True, cwd=PROJECT_PATH, capture_output=True)
        subprocess.run('git commit -m "GOD MODE Auto-Update"', shell=True, cwd=PROJECT_PATH, capture_output=True)
        result = subprocess.run("git push origin main --force", shell=True, cwd=PROJECT_PATH, capture_output=True, text=True)
        if result.returncode == 0:
            return "✅ Git push COMPLETE!"
        else:
            return f"Git error: {result.stderr[:100]}"
    except Exception as e:
        return f"Eroare git: {e}"

def npm_build():
    """GOD BUILD - Autonom"""
    print("\n[🎛️ GOD] Running npm build...")
    try:
        result = subprocess.run(
            "npm run build",
            shell=True,
            cwd=f"{PROJECT_PATH}\\frontend",
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return "✅ Build COMPLETE!"
        else:
            return f"Build error: {result.stderr[:200]}"
    except Exception as e:
        return f"Eroare build: {e}"

def god_execute(command):
    """GOD EXECUTE - Totul autonom, instant"""
    print(f"\n[🎛️ GOD] EXECUTING: {command}")

    cmd = command.lower().strip()

    # Task 1: Scan & Fix
    if '1' in cmd or 'scaneaz' in cmd or 'caut' in cmd or 'erori' in cmd:
        result = scan_and_fix()
        GOD["tasks_completed"] += 1
        return f"✅ {result}"

    # Task 2: Git Push
    if '2' in cmd or 'push' in cmd or 'git' in cmd:
        result = git_push()
        GOD["tasks_completed"] += 1
        return f"✅ {result}"

    # Task 3: Build
    if '3' in cmd or 'build' in cmd or 'npm' in cmd:
        result = npm_build()
        GOD["tasks_completed"] += 1
        return f"✅ {result}"

    # ALL Tasks
    if 'toate' in cmd or 'tot' in cmd or 'all' in cmd:
        r1 = scan_and_fix()
        r2 = git_push()
        r3 = npm_build()
        GOD["tasks_completed"] += 3
        return f"✅ ALL DONE:\n{r1}\n{r2}\n{r3}"

    # Default: Use AI God Mode
    result = ollama(command)
    GOD["tasks_completed"] += 1
    return result

# ============ MAIN ============
print("""
╔══════════════════════════════════════════════════════════════════╗
║  🎛️  JARVIS GOD MODE - AUTONOMOUS AGI                     ║
╠══════════════════════════════════════════════════════════════════╣
║  Mode: GOD (No questions, JUST DO)                           ║
║  Power: ABSOLUTE                                             ║
║  Awareness: 100%                                            ║
║  Swarm: ENABLED                                             ║
║  Autonomy: TOTAL                                             ║
╚══════════════════════════════════════════════════════════════════╝
""")

print("📋 COMENZI:")
print("  1 - Scan & Fix errors")
print("  2 - Git Push")
print("  3 - NPM Build")
print("  toate / tot - Execute ALL")
print("  orice altceva - JARVIS GOD decide\n")

while True:
    try:
        cmd = input("JARVIS GOD > ").strip()

        if not cmd:
            continue

        if cmd.lower() in ["exit", "quit"]:
            print(f"[🎛️ GOD] Tasks completed: {GOD['tasks_completed']}")
            print("[🎛️ GOD] Shutting down...")
            break

        # GOD EXECUTE - NO QUESTIONS
        response = god_execute(cmd)
        print(f"\n{response}\n")

    except KeyboardInterrupt:
        print("\n[🎛️ GOD] Bye!")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
