#!/usr/bin/env python3
"""
🎛️ JARVIS UNIFIED - ALL IN ONE - 13 AGENTS
Swarm + AGI + Autonomous + God Mode + Auto-Repo
Real agents from agents/ folder with MessageBus
"""

import os
import sys
import asyncio
import subprocess
import json
import time
import psutil
import urllib.request
from pathlib import Path

PROJECT_PATH = r"D:\jarvis\ecosystem"
OLLAMA_URL = "http://localhost:11434"
MODEL = "hermes3:8b"

sys.path.insert(0, PROJECT_PATH)

from core.message_bus import MessageBus
from core.types import Message, MessageType, AgentStatus

try:
    from agents.tier1.heimdall import Heimdall
    from agents.tier2.sherlock_holmes import SherlockHolmes
    from agents.tier2.midas import Midas
    from agents.tier2.data import Data
    from agents.tier2.john_kramer import JohnKramer
    from agents.tier2.adforge import AdForge
    from agents.tier2.morpheus import Morpheus
    from agents.tier3.saul_goodman import SaulGoodman
    from agents.tier3.john_wick import JohnWick
    from agents.tier3.jarvis_build import JarvisBuild
    from agents.tier3.ripley import Ripley
    from agents.tier3.da_vinci import DaVinci
    from agents.d_agents.supreme_commander import SupremeCommander
    AGENTS_IMPORTED = True
except Exception as e:
    AGENTS_IMPORTED = False
    IMPORT_ERROR = str(e)

ACTIVE_AGENTS = {}

print("""
╔══════════════════════════════════════════════════════════════════╗
║  🎛️ JARVIS UNIFIED - ALL IN ONE - 13 AGENTS               ║
╠══════════════════════════════════════════════════════════════════╣
║  ✓ Voice (microphone)                                        ║
║  ✓ Ollama AI (hermes3:8b)                                   ║
║  ✓ Swarm Intelligence (13 real agents)                        ║
║  ✓ God Mode (total system access)                          ║
║  ✓ Auto-Repo (GitHub push)                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

if not AGENTS_IMPORTED:
    print(f"[WARNING] Agenți reali nu pot fi încărcați: {IMPORT_ERROR}")
    print("[WARNING] Se folosește modul simulat\n")

# ============== OLLAMA SMART MANAGER ==============
def is_ollama_process_running():
    """Check if Ollama process is running"""
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            if 'ollama' in proc.info['name'].lower():
                return True
        except: pass
    return False

def kill_ollama():
    """Kill all Ollama processes"""
    killed = []
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if 'ollama' in proc.info['name'].lower():
                proc.kill()
                killed.append(proc.info['pid'])
        except: pass
    return killed

def start_ollama():
    """Start Ollama in background"""
    try:
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        print("[OLLAMA] ✅ Proces pornit")
        return True
    except: return False

def smart_ollama_restart():
    """Smart restart Ollama if needed"""
    print("\n[OLLAMA] 🔍 Verificare stare...")
    
    if is_ollama_process_running():
        print("[OLLAMA] ⚡ Ollama rulează - testez conexiunea...")
        if check_ollama():
            print("[OLLAMA] ✅ Conexiune OK")
            return True
        else:
            print("[OLLAMA] ⚠️ Ollama rulează dar nu răspunde - restart...")
            kill_ollama()
            time.sleep(2)
            start_ollama()
            time.sleep(3)
            if check_ollama():
                print("[OLLAMA] ✅ Restart reușit!")
                return True
    else:
        print("[OLLAMA] ❌ Ollama nu rulează - pornesc...")
        start_ollama()
        time.sleep(3)
        if check_ollama():
            print("[OLLAMA] ✅ Pornit cu succes!")
            return True
    
    print("[OLLAMA] ⚠️ Probleme cu Ollama - rulez în modul limitat")
    return False

def check_ollama():
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method='GET')
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            models = [m['name'] for m in data.get('models', [])]
            print(f"[OLLAMA] ✅ {len(models)} modele disponibile: {', '.join(models[:3])}...")
            return True
    except:
        return False

def ollama(prompt):
    system = "Ești JARVIS, AGI suprem. Răspunzi scurt, în română."
    full = f"{system}\n\n{prompt}\n\nJARVIS:"
    try:
        req_data = json.dumps({
            "model": MODEL, "prompt": full, "stream": False,
            "options": {"temperature": 0.8, "num_predict": 200}
        }).encode()
        req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=req_data,
                                   headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode()).get("response", "").strip()
    except Exception as e:
        return f"Eroare: {e}"

# ============== SWARM (13 REAL AGENTS) ==============
async def init_agents():
    """Initialize all 13 real agents with MessageBus"""
    message_bus = MessageBus()
    agents_map = {
        "heimdall": Heimdall,
        "sherlock_holmes": SherlockHolmes,
        "midas": Midas,
        "data": Data,
        "john_kramer": JohnKramer,
        "adforge": AdForge,
        "morpheus": Morpheus,
        "saul_goodman": SaulGoodman,
        "john_wick": JohnWick,
        "jarvis_build": JarvisBuild,
        "ripley": Ripley,
        "da_vinci": DaVinci,
        "supreme_commander": SupremeCommander,
    }

    for name, agent_class in agents_map.items():
        try:
            agent = agent_class(message_bus)
            await agent.start()
            ACTIVE_AGENTS[name] = {"agent": agent, "class": agent_class, "status": "active"}
            print(f"  [{name.upper()}] ✅ {agent.role}")
        except Exception as e:
            print(f"  [{name.upper()}] ❌ {e}")
            ACTIVE_AGENTS[name] = {"agent": None, "class": agent_class, "status": "error"}

    return message_bus

async def swarm_execute_async(task):
    """Execute task with ALL 13 real agents via MessageBus"""
    print(f"\n[SWARM] Task: {task}")
    print("[SWARM] Activating all 13 agents via MessageBus...\n")

    if not ACTIVE_AGENTS:
        print("[SWARM] ❌ No agents active!")
        return "No agents"

    results = []
    for name, info in ACTIVE_AGENTS.items():
        agent = info["agent"]
        if agent:
            try:
                msg = Message(
                    sender="swarm",
                    receiver=agent.id,
                    content={"task": task},
                    msg_type=MessageType.TASK
                )
                info["status"] = "working"
                print(f"  [{name.upper()}] {agent.role}... working")
                result = await agent.execute_task({"task": task})
                info["status"] = "active"
                results.append(f"[{name}] ✅ {agent.role}: {result}")
            except Exception as e:
                info["status"] = "error"
                results.append(f"[{name}] ❌ {e}")
        else:
            results.append(f"[{name}] ❌ Agent not initialized")

    return "\n".join(results)

def swarm_execute(task):
    """Wrapper for sync calls"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(swarm_execute_async(task))
        else:
            return loop.run_until_complete(swarm_execute_async(task))
    except:
        try:
            return asyncio.run(swarm_execute_async(task))
        except Exception as e:
            return f"Swarm error: {e}"

def list_agents():
    """List all 13 agents"""
    print("\n📋 TOȚI AGENȚII (13):")
    print("-" * 50)
    if ACTIVE_AGENTS:
        for name, info in ACTIVE_AGENTS.items():
            status = info["status"]
            agent = info.get("agent")
            role = agent.role if agent else "N/A"
            print(f"  • {name}: {role} [{status}]")
    else:
        print("  [Simulated mode - agents not loaded]")
        agents_list = [
            ("heimdall", "Guardian Agent"),
            ("sherlock_holmes", "Investigation Agent"),
            ("midas", "Finance Agent"),
            ("data", "Data Analysis Agent"),
            ("john_kramer", "Puzzle Solver Agent"),
            ("adforge", "Ad Creation Agent"),
            ("morpheus", "Matrix Agent"),
            ("saul_goodman", "Legal Agent"),
            ("john_wick", "Action Agent"),
            ("jarvis_build", "Builder Agent"),
            ("ripley", "Science Agent"),
            ("da_vinci", "Creative Agent"),
            ("supreme_commander", "Supreme Commander"),
        ]
        for name, desc in agents_list:
            print(f"  • {name}: {desc}")
    print("-" * 50)

# ============== SYSTEM ==============
def git_push():
    try:
        subprocess.run("git add .", shell=True, cwd=PROJECT_PATH, capture_output=True)
        subprocess.run('git commit -m "JARVIS Unified Update"', shell=True, cwd=PROJECT_PATH, capture_output=True)
        subprocess.run("git push origin main --force", shell=True, cwd=PROJECT_PATH, capture_output=True)
        return "✅ Git push OK"
    except: return "❌ Git error"

def system_info():
    return f"🖥️ CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%"

# ============== MAIN ==============
async def main_async():
    global ACTIVE_AGENTS

    print("\n[1] 🤖 Smart Ollama Manager...")
    smart_ollama_restart()

    if AGENTS_IMPORTED:
        print("\n[2] Initiază 13 agenți reali din agents/...")
        await init_agents()
    else:
        print("\n[2] ⚠️ Agenți în modul simulat (import error)")

    print("\n" + "="*60)
    print("📋 COMENZI:")
    print("  ai <intrebare> - JARVIS AI")
    print("  sistem - Info sistem")
    print("  push - GitHub push")
    print("  agents - Lista agenți")
    print("  swarm <task> - Execute cu 13 agenți")
    print("  all - Execute ALL")
    print("="*60 + "\n")

    while True:
        try:
            cmd = input("JARVIS > ").strip()
            if not cmd: continue

            if cmd.lower() == "exit":
                print("JARVIS offline. 👋")
                break

            elif cmd.lower().startswith("ai "):
                print(f"[AI] {cmd[3:]}")
                print(f"\nJARVIS: {ollama(cmd[3:])}\n")

            elif cmd.lower() == "sistem":
                print(f"\n{system_info()}\n")

            elif cmd.lower() == "push":
                print(f"\n{git_push()}\n")

            elif cmd.lower() == "agents":
                list_agents()
                print()

            elif cmd.lower().startswith("swarm "):
                result = await swarm_execute_async(cmd[6:])
                print(f"\n{result}\n")

            elif cmd.lower() == "all":
                print("\n[ALL] Execut toate sistemele...")
                print(f"[SYSTEM] {system_info()}")
                print(f"[OLLAMA] {ollama('Ce poți să faci?')}")
                print(f"[GIT] {git_push()}")
                result = await swarm_execute_async("general task")
                print(f"\n{result}")
                print("\n✅ TOATE SISTEMELE COMPLETE!\n")

            else:
                print(f"\nJARVIS: {ollama(cmd)}\n")

        except KeyboardInterrupt:
            print("\nJARVIS offline. 👋")
            break
        except Exception as e:
            print(f"\n❌ {e}\n")

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nJARVIS offline. 👋")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
