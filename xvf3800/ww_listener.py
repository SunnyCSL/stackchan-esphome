#!/usr/bin/env python3
"""Persistent wake word listener - XVF3800 USB audio → openWakeWord"""
import pyaudio, numpy as np, time, sys, os
from collections import deque

# === CONFIG ===
RATE = 48000
CHUNK = 1280
TARGET_RATE = 16000
RESAMPLE = RATE // TARGET_RATE  # 3
WAKE_WORD = "alexa"  # Options: alexa, hey_mycroft, hey_jarvis, hey_rhasspy
THRESHOLD = 0.5
DEBOUNCE_S = 2.0  # Minimum seconds between detections

# === Find USB audio device ===
p = pyaudio.PyAudio()
dev_idx = None
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    name = str(info.get("name", ""))
    ch = info.get("maxInputChannels", 0)
    if "USB Composite" in name and ch > 0:
        dev_idx = i
        print(f"[{time.strftime('%H:%M:%S')}] Device: {name} (idx={i}, {int(info['defaultSampleRate'])}Hz)")
        break
p.terminate()

if dev_idx is None:
    print("FATAL: No USB audio device found!")
    sys.exit(1)

# === Load model ===
print(f"[{time.strftime('%H:%M:%S')}] Loading model '{WAKE_WORD}'...")
from openwakeword.model import Model
oww = Model(wakeword_models=[WAKE_WORD], inference_framework="onnx")
print(f"[{time.strftime('%H:%M:%S')}] Ready! Listening...")

# === Audio stream ===
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                input=True, input_device_index=dev_idx,
                frames_per_buffer=CHUNK)

buf = deque(maxlen=60)  # ~1.5s buffer
last_detect = 0

print(f"[{time.strftime('%H:%M:%S')}] Say '{WAKE_WORD}'...\n")

try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        audio_16k = audio[::RESAMPLE]
        buf.extend(audio_16k)

        if len(buf) >= 30:
            pred = oww.predict(np.array(buf, dtype=np.float32))
            for k, v in pred.items():
                if isinstance(v, np.ndarray):
                    score = float(np.max(v))
                else:
                    score = float(v)
                
                if score > 0.2:  # Show any score above 0.2
                    ts = time.strftime('%H:%M:%S')
                    marker = "🎤" if score > THRESHOLD else "  "
                    print(f"[{ts}] {marker} {k}: {score:.3f}")
                
                if score > THRESHOLD and time.time() - last_detect > DEBOUNCE_S:
                    print(f"[{time.strftime('%H:%M:%S')}] 🎤🎤🎤 WAKE WORD DETECTED! ({k}: {score:.3f})")
                    last_detect = time.time()
                    buf.clear()

except KeyboardInterrupt:
    print(f"\n[{time.strftime('%H:%M:%S')}] Stopped.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
