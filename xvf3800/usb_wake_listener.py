#!/usr/bin/env python3
"""Wake word listener using XVF3800 USB audio (Jieli bridge)"""
import pyaudio
import numpy as np
from openwakeword.model import Model
import time
from collections import deque
import signal

# Config
RATE = 48000
CHUNK = 1280
CHANNELS = 1
DEVICE_INDEX = None  # auto-detect card 1

# Find device index for "USB Composite Device"
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if "USB Composite" in info.get("name", "") and info.get("maxInputChannels", 0) > 0:
        DEVICE_INDEX = i
        print(f"Found: {info['name']} (index {i}, {int(info['defaultSampleRate'])}Hz)")
        break
p.terminate()

if DEVICE_INDEX is None:
    print("Error: USB Composite Device not found!")
    exit(1)

# Resample: 48000 → 16000 (3:1)
resample_factor = 3

print("Loading wake word model (okay_nabu)...")
oww = Model(wakeword_models=["okay_nabu"], inference_framework="onnx")
print("Model loaded!")

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=DEVICE_INDEX,
                frames_per_buffer=CHUNK)

print(f"\n🎤 Listening for 'Okay Nabu'... (Ctrl+C to stop)\n")

running = True
def handler(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, handler)

buffer = deque(maxlen=50)
detections = 0

while running:
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        audio_16k = audio[::resample_factor]
        buffer.extend(audio_16k)
        
        if len(buffer) >= 30:
            prediction = oww.predict(np.array(buffer, dtype=np.float32))
            score = 0.0
            if isinstance(prediction, dict):
                for k, v in prediction.items():
                    if "nabu" in k.lower():
                        score = float(np.max(v)) if hasattr(v, '__len__') else float(v)
                        break
            
            if score > 0.5:
                detections += 1
                print(f"🎤 WAKE WORD #{detections}! (score: {score:.3f})")
                buffer.clear()
                
    except Exception as e:
        print(f"Err: {e}")
        time.sleep(0.1)

stream.stop_stream()
stream.close()
p.terminate()
print(f"\nDone. Detections: {detections}")
