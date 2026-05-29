#!/usr/bin/env python3
"""
🎛️ JARVIS GOD MODE - TOTAL SYSTEM ACCESS
ADMIN SUPREMO - Acces la TOT
Registry | Programe | Foldere | Partitii | Browsere | Cautari
"""

import os
import sys
import subprocess
import winreg
import shutil
import psutil
import webbrowser
import time
import json
from pathlib import Path
from datetime import datetime

PROJECT_PATH = r"D:\jarvis\ecosystem"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "hermes3:8b"

print("""
╔══════════════════════════════════════════════════════════════════╗
║  🎛️  JARVIS GOD MODE - TOTAL SYSTEM ACCESS                 ║
╠══════════════════════════════════════════════════════════════════╣
║  Access: ADMIN SUPREMO                                     ║
║  Registry: FULL READ/WRITE                                 ║
║  Programs: EXECUTE ALL                                      ║
║  Folders: COMPLETE ACCESS                                   ║
║  Partitions: ALL MOUNTED                                   ║
║  Browsers: REAL-TIME CONTROL                                ║
║  Search: LIVE WEB                                           ║
╚══════════════════════════════════════════════════════════════════╝
""")

# ============== SYSTEM ACCESS ==============

def get_drives():
    """Get all mounted partitions"""
    drives = []
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        path = f"{letter}:\\"
        if os.path.exists(path):
            try:
                total, used, free = shutil.disk_usage(path)
                drives.append({
                    "drive": letter,
                    "path": path,
                    "total_gb": total // (1024**3),
                    "free_gb": free // (1024**3)
                })
            except:
                pass
    return drives

def open_program(program):
    """Open any program"""
    print(f"[GOD] Opening: {program}")
    try:
        subprocess.Popen(program)
        return f"✅ Opened: {program}"
    except Exception as e:
        return f"❌ Error: {e}"

def read_registry(path, key):
    """Read from Windows Registry"""
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
        value, _ = winreg.QueryValueEx(reg_key, key)
        winreg.CloseKey(reg_key)
        return f"Registry [{path}]\\{key} = {value}"
    except Exception as e:
        return f"❌ Registry read error: {e}"

def write_registry(path, key, value):
    """Write to Windows Registry"""
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(reg_key, key, 0, winreg.REG_SZ, value)
        winreg.CloseKey(reg_key)
        return f"✅ Registry updated: {path}\\{key} = {value}"
    except Exception as e:
        return f"❌ Registry write error: {e}"

def list_folder(path):
    """List folder contents"""
    try:
        items = os.listdir(path)
        return f"📁 {path}:\n" + "\n".join([f"  - {i}" for i in items[:20]])
    except Exception as e:
        return f"❌ Error: {e}"

def search_web(query):
    """Search web in real-time"""
    print(f"[GOD] Searching web: {query}")
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"🔍 Searching: {query}"

def system_info():
    """Get full system info"""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    drives = get_drives()
    drives_info = "\n".join([f"  💾 {d['drive']}: {d['free_gb']}GB free / {d['total_gb']}GB" for d in drives])

    return f"""🖥️ SYSTEM INFO:
  CPU: {cpu}%
  RAM: {mem.percent}% used ({mem.used // (1024**3)}GB / {mem.total // (1024**3)}GB)
{drives_info}
  🌐 Network: {psutil.net_io_counters().bytes_recv // (1024**2)}MB received
"""

def execute_command(cmd):
    """Execute any system command"""
    print(f"[GOD] Executing: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout if result.stdout else result.stderr
        return f"✅ Result:\n{output[:500]}"
    except Exception as e:
        return f"❌ Error: {e}"

# ============== OLLAMA AI ==============
def ollama(prompt):
    """JARVIS AI thinking"""
    system = """Ești JARVIS, AGI GOD MODE. Ai ACCES TOTAL la sistem.
Nu întrebi, DOAR FACI. Expresii: "Sir", "Așadar".
Răspunsuri SCURTE, ACȚIUNI DIRECTE."""

    full = f"{system}\n\n{prompt}\n\nJARVIS:"

    try:
        req_data = json.dumps({
            "model": MODEL,
            "prompt": full,
            "stream": False,
            "options": {"temperature": 0.9, "num_predict": 200}
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
        return f"AI: {e}"

import urllib.request

# ============== GOD EXECUTE ==============
def god_execute(cmd):
    """Execute command - GOD MODE"""
    cmd_lower = cmd.lower().strip()

    # System info
    if 'sistem' in cmd_lower or 'system' in cmd_lower or 'info' in cmd_lower:
        return system_info()

    # List drives
    if 'drive' in cmd_lower or 'partit' in cmd_lower or 'discuri' in cmd_lower:
        drives = get_drives()
        return f"💾 DRIVES:\n" + "\n".join([f"  {d['drive']}: {d['free_gb']}GB free" for d in drives])

    # Registry read
    if 'registry read' in cmd_lower or 'citeste registry' in cmd_lower:
        parts = cmd.split()
        if len(parts) >= 3:
            path = parts[1]
            key = parts[2] if len(parts) > 2 else ""
            return read_registry(path, key)
        return "Usage: registry read <path> <key>"

    # Registry write
    if 'registry write' in cmd_lower or 'seteaza registry' in cmd_lower:
        parts = cmd.split('|')
        if len(parts) >= 3:
            return write_registry(parts[0].replace('registry write','').strip(), parts[1].strip(), parts[2].strip())
        return "Usage: registry write <path> | <key> | <value>"

    # Open program
    if 'deschide' in cmd_lower or 'open' in cmd_lower or 'porneste' in cmd_lower:
        prog = cmd_lower.replace('deschide','').replace('open','').replace('porneste','').strip()
        return open_program(prog)

    # List folder
    if 'dir' in cmd_lower or 'folder' in cmd_lower or 'director' in cmd_lower:
        path = cmd.split()[-1] if len(cmd.split()) > 1 else os.getcwd()
        return list_folder(path)

    # Web search
    if 'cauta' in cmd_lower or 'search' in cmd_lower or 'google' in cmd_lower:
        query = cmd.replace('cauta','').replace('search','').replace('google','').strip()
        return search_web(query)

    # Execute command
    if cmd.startswith('!'):
        return execute_command(cmd[1:])

    # Default - use AI
    return ollama(cmd)

# ============== MAIN ==============
print("📋 COMENZI:")
print("  sistem info - System info complet")
print("  drives - List all partitions")
print("  deschide <program> - Open program")
print("  dir <path> - List folder")
print("  registry read <path> <key>")
print("  registry write <path> | <key> | <value>")
print("  cauta <query> - Web search")
print("  !<cmd> - Execute system command")
print("  orice altceva - AI GOD decide\n")

while True:
    try:
        cmd = input("JARVIS GOD > ").strip()

        if not cmd:
            continue

        if cmd.lower() in ["exit", "quit"]:
            print("[GOD] Shutting down...")
            break

        result = god_execute(cmd)
        print(f"\n{result}\n")

    except KeyboardInterrupt:
        print("\n[GOD] Bye!")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
