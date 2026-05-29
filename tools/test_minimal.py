#!/usr/bin/env python3
"""Minimal JARVIS test"""
import sys
print("1. Starting...", flush=True)

import pyaudio
print("2. pyaudio imported", flush=True)

import speech_recognition as sr
print("3. speech_recognition imported", flush=True)

import pygame
print("4. pygame about to init...", flush=True)
pygame.mixer.init()
print("5. pygame mixer init OK", flush=True)

print("6. All imports OK! Starting main loop...")

# Test listen
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=512)
print("7. Audio stream opened! Listening...")

frames = []
for i in range(10):  # 10 iterations = ~1 second
    try:
        data = stream.read(512, exception_on_overflow=False)
        frames.append(data)
        print(f"8. Frame {i} captured, total bytes: {len(b''.join(frames))}")
    except Exception as e:
        print(f"Error: {e}")
        break

stream.stop_stream()
stream.close()
p.terminate()

audio_data = b''.join(frames)
print(f"9. Recording complete! {len(audio_data)} bytes")

# Test transcribe
if len(audio_data) > 1000:
    print("10. Testing transcription...")
    r = sr.Recognizer()
    audio = sr.AudioData(audio_data, 16000, 2)
    try:
        text = r.recognize_google(audio, language="ro-RO")
        print(f"11. Recognized: {text}")
    except Exception as e:
        print(f"12. Transcription error: {e}")
else:
    print("10. Audio too short, skipping transcription")

print("13. TEST COMPLETE!")
