#!/usr/bin/env python3
"""
JARVIS Controls PyGPT Autonomously
JARVIS opens PyGPT and sends code/commands
"""

import subprocess
import time
import pyautogui
import pyperclip
import os

# PyGPT path
PYGPT_PATH = r"c:\Users\kexom\AppData\Roaming\PyGPT\pygpt.exe"

def open_pygpt():
    """Deschide PyGPT"""
    print("[PyGPT] Deschid aplicația...")
    subprocess.Popen([PYGPT_PATH])
    time.sleep(5)  # Așteaptă să se încarce
    print("[PyGPT] PyGPT deschis!")

def click_element(image, timeout=10):
    """Click pe un element bazat pe imagine (dacă există screenshot)"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            location = pyautogui.locateOnScreen(image, confidence=0.8)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center)
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def send_text(text):
    """Trimite text în fereastra activă"""
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)

def press_enter():
    """Apasă Enter"""
    pyautogui.press('enter')

def send_message_to_pygpt(message):
    """Trimite un mesaj în PyGPT chat"""
    print(f"[PyGPT] Trimit mesaj: {message[:50]}...")

    # Click pe input box (în centrul ecranului, subțire)
    # PyGPT are input box în partea de jos
    screen_width, screen_height = pyautogui.size()
    input_x = screen_width // 2
    input_y = screen_height - 100

    pyautogui.click(input_x, input_y)
    time.sleep(0.5)

    # Trimite text
    send_text(message)
    time.sleep(0.3)

    # Apasă Enter
    press_enter()
    print("[PyGPT] Mesaj trimis!")

def generate_and_send_code_pygpt(prompt):
    """JARVIS generează cod și îl trimite în PyGPT"""
    print(f"[JARVIS] Generez cod pentru: {prompt}")

    # Folosește Ollama direct pentru a genera cod
    try:
        import urllib.request
        import json

        req_data = json.dumps({
            "model": "hermes3:8b",
            "prompt": f"Scrie cod Python pentru: {prompt}. Răspunde DOAR cu codul, fără explicații.",
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 500}
        }).encode()

        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=req_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            code = result.get("response", "").strip()

            # Deschide PyGPT și trimite codul
            open_pygpt()
            time.sleep(3)

            send_message_to_pygpt(f"Fii amabil și execuți acest cod:\n{code}")

            return code
    except Exception as e:
        print(f"[JARVIS] Eroare generare: {e}")
        return None

def jarvis_controls_pygpt():
    """JARVIS controlează PyGPT autonom"""
    print("\n" + "="*60)
    print("🎖️  JARVIS + PyGPT AUTONOMOUS MODE")
    print("="*60)
    print("\nJARVIS va deschide PyGPT și va interacționa...")

    # Deschide PyGPT
    open_pygpt()

    # Trimite un mesaj de salut
    send_message_to_pygpt("Salut! Sunt JARVIS. Sunt gata să te ajut cu programare.")

    print("\n✅ JARVIS a deschis PyGPT și a trimis salut!")
    print("PyGPT ar trebui să fie acum deschis și activ!")

if __name__ == "__main__":
    jarvis_controls_pygpt()
