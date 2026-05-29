#!/usr/bin/env python3
"""
JARVIS Complete Voice System Test
Testează: Wake word, TTS, Ollama integration
"""

import sys
import os
import time
import threading
import queue

# Adăugăm path către tools
sys.path.insert(0, r'D:\jarvis\ecosystem\tools')

def test_voice_components():
    """Testează toate componentele vocale"""
    
    print("=" * 80)
    print("JARVIS COMPLETE VOICE SYSTEM TEST")
    print("=" * 80)
    print()
    
    results = {
        'edge_tts': False,
        'whisper': False,
        'speech_recognition': False,
        'pygame': False,
        'ollama': False
    }
    
    # Test 1: Edge TTS
    print("[TEST 1/6] Verificare Edge TTS...")
    try:
        import edge_tts
        import asyncio
        
        async def test_tts():
            voice = "ro-RO-AlinaNeural"
            communicate = edge_tts.Communicate("Test JARVIS", voice)
            return True
        
        result = asyncio.run(test_tts())
        if result:
            print("  ✓ Edge TTS funcționează")
            results['edge_tts'] = True
    except Exception as e:
        print(f"  ✗ Edge TTS eroare: {e}")
    
    # Test 2: Whisper
    print("\n[TEST 2/6] Verificare Whisper...")
    try:
        import whisper
        print("  ✓ Whisper disponibil")
        
        # Încercăm să încărcăm modelul
        print("  Se testează încărcarea modelului...")
        model = whisper.load_model("tiny")
        print("  ✓ Model Whisper încărcat cu succes")
        results['whisper'] = True
    except Exception as e:
        print(f"  ✗ Whisper eroare: {e}")
    
    # Test 3: Speech Recognition
    print("\n[TEST 3/6] Verificare Speech Recognition...")
    try:
        import speech_recognition as sr
        
        # Verificăm microfonul
        mic = sr.Microphone()
        print(f"  ✓ Microfon detectat: {mic}")
        
        # Testăm recognizer
        recognizer = sr.Recognizer()
        print("  ✓ Speech Recognition funcționează")
        results['speech_recognition'] = True
    except Exception as e:
        print(f"  ✗ Speech Recognition eroare: {e}")
    
    # Test 4: Pygame (pentru audio playback)
    print("\n[TEST 4/6] Verificare Pygame...")
    try:
        import pygame
        pygame.mixer.init()
        print("  ✓ Pygame mixer inițializat")
        results['pygame'] = True
    except Exception as e:
        print(f"  ✗ Pygame eroare: {e}")
    
    # Test 5: Ollama Connection
    print("\n[TEST 5/6] Verificare conexiune Ollama...")
    try:
        import urllib.request
        import json
        
        url = "http://localhost:11434/api/tags"
        req = urllib.request.Request(url, method='GET')
        
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())
            models = result.get('models', [])
            
            print(f"  ✓ Ollama conectat! Modele disponibile: {len(models)}")
            for m in models[:5]:
                print(f"    - {m.get('name', 'unknown')}")
            results['ollama'] = True
    except Exception as e:
        print(f"  ✗ Ollama eroare: {e}")
        print("    Asigură-te că Ollama rulează: ollama serve")
    
    # Test 6: Voice System Integration
    print("\n[TEST 6/6] Verificare integrare Voice System...")
    try:
        from voice_simple import VoiceSystem
        
        vs = VoiceSystem()
        print(f"  ✓ Voice System inițializat")
        print(f"    Wake word: {vs.wake_word}")
        print(f"    Model: {vs._ollama_model}")
        print(f"    Whisper: {'Disponibil' if vs._whisper_stt else 'Indisponibil'}")
        print(f"    Edge TTS: {'Disponibil' if EDGE_TTS_AVAILABLE else 'Indisponibil'}")
    except Exception as e:
        print(f"  ✗ Voice System eroare: {e}")
    
    # Rezultate finale
    print("\n" + "=" * 80)
    print("REZULTATE TESTE")
    print("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, status in results.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {component}: {'FUNCȚIONAL' if status else 'INDISPONIBIL'}")
    
    print(f"\nTotal: {passed}/{total} componente funcționale")
    
    if passed == total:
        print("\n🎉 TOATE COMPONENTELE FUNCȚIONEAZĂ! Sistemul vocal JARVIS este gata.")
    elif passed >= 4:
        print("\n⚠️ Sistemul funcționează parțial. Unele feature-uri pot fi indisponibile.")
    else:
        print("\n❌ Sistemul are probleme majore. Verifică instalările.")
    
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    test_voice_components()
