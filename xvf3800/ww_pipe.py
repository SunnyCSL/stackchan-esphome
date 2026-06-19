#!/usr/bin/env python3
"""Wake word listener using arecord pipe (no pyaudio)"""
import numpy as np, sys, time, subprocess, os
from collections import deque

# === CONFIG ===
RATE = 48000
CHUNK = 1280 * 2  # 2560 bytes = 1280 samples @ S16_LE
TARGET_RATE = 16000
RESAMPLE = RATE // TARGET_RATE
WAKE_WORD = "alexa"
THRESHOLD = 0.5
DEBOUNCE_S = 2.0

print(f"[{time.strftime('%H:%M:%S')}] Loading model '{WAKE_WORD}'...")
from openwakeword.model import Model
oww = Model(wakeword_models=[WAKE_WORD], inference_framework="onnx")

print(f"[{time.strftime('%H:%M:%S')}] Starting arecord pipe...")
proc = subprocess.Popen(
    ["arecord", "-D", "hw:1,0", "-f", "S16_LE", "-r", str(RATE), "-c", "1", "-t", "raw"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
)

buf = deque(maxlen=60)
last_detect = 0
detections = 0
print(f"[{time.strftime('%H:%M:%S')}] Ready! Say '{WAKE_WORD}'...\n")

try:
    while True:
        raw = proc.stdout.read(CHUNK)
        if len(raw) < CHUNK:
            break
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        audio_16k = audio[::RESAMPLE]
        buf.extend(audio_16k)

        if len(buf) >= 30:
            pred = oww.predict(np.array(buf, dtype=np.float32))
            for k, v in pred.items():
                if isinstance(v, np.ndarray) and len(v) > 0:
                    score = float(np.max(v))
                else:
                    score = float(v)
                
                if score > THRESHOLD and time.time() - last_detect > DEBOUNCE_S:
                    detections += 1
                    ts = time.strftime('%H:%M:%S')
                    print(f"[{ts}] 🎤 WAKE WORD #{detections}! ({k}: {score:.3f})")
                    last_detect = time.time()
                    buf.clear()

except KeyboardInterrupt:
    pass
finally:
    proc.terminate()
    proc.wait()
    print(f"\n[{time.strftime('%H:%M:%S')}] Done. {detections} detections.")
