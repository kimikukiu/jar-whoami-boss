#!/usr/bin/env python3
"""
JARVIS - Direct Ollama Integration
Configurează și pornește JARVIS cu Ollama
"""

import os
import sys
import urllib.request
import json

# Verifică Ollama
print("=" * 60)
print("🎖️  JARVIS + OLLAMA CONFIGURATION")
print("=" * 60)

# 1. Verifică Ollama
print("\n[1] Verificare Ollama...")
try:
    req = urllib.request.Request("http://localhost:11434/api/tags", method='GET')
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
        models = data.get('models', [])
        print(f"✅ Ollama conectat! {len(models)} modele găsite:")
        for m in models:
            print(f"   - {m['name']}")
except Exception as e:
    print(f"❌ Ollama nu e conectat: {e}")
    print("\nPornesc Ollama...")
    os.system('start cmd /c "ollama serve"')
    sys.exit(1)

# 2. Selectează cel mai bun model
best_model = None
for m in models:
    name = m['name'].lower()
    if 'hermes3' in name:
        best_model = m['name']
        break
    elif 'qwen3' in name and 'abliterated' in name:
        best_model = m['name']

if not best_model and models:
    best_model = models[0]['name']

print(f"\n[2] Model selectat: {best_model}")

# 3. Creează config pentru JARVIS
config = {
    "ollama_url": "http://localhost:11434",
    "model": best_model,
    "voice": "ro-RO-AlinaNeural",
    "wake_word": "jarvis"
}

config_path = r"D:\jarvis\ecosystem\config\ollama.json"
os.makedirs(os.path.dirname(config_path), exist_ok=True)

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"\n[3] Config salvat: {config_path}")

# 4. Pornește JARVIS
print(f"\n[4] Pornesc JARVIS cu modelul: {best_model}")
print("=" * 60)
print("\n✅ JARVIS e gata! Vorbește 'JARVIS' pentru a-l activa!")
print("=" * 60)
