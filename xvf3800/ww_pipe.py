#!/usr/bin/env python3
"""Wake word listener using arecord pipe (no pyaudio)"""
import numpy as np, sys, time, subprocess, os
from collections import deque

# === CONFIG ===
RATE = 16000
CHUNK = 640  # 640 samples = 40ms @ 16kHz
TARGET_RATE = 16000
RESAMPLE = 1  # No resampling needed
WAKE_WORD = "hey_jarvis"
THRESHOLD = 0.15  # Very low for testing - detect any faint match
DEBOUNCE_S = 2.0
GAIN_REDUCE = 0.33  # ~3x boost, clipped to [-1,1]
LOG_LEVEL = 5  # Print audio stats every N seconds (None = off)

print(f"[{time.strftime('%H:%M:%S')}] Loading model '{WAKE_WORD}'...")
from openwakeword.model import Model
oww = Model(wakeword_models=[WAKE_WORD], inference_framework="onnx")

print(f"[{time.strftime('%H:%M:%S')}] Starting arecord pipe...")
proc = subprocess.Popen(
    ["arecord", "-D", "plughw:1,0", "-f", "S16_LE", "-r", str(RATE), "-c", "1", "-t", "raw"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
)

buf = deque(maxlen=60)
last_detect = 0
detections = 0
last_log = 0
peak_overall = 0
print(f"[{time.strftime('%H:%M:%S')}] Ready! Say '{WAKE_WORD}'...")
print(f"[{time.strftime('%H:%M:%S')}] GAIN_REDUCE={GAIN_REDUCE} THRESHOLD={THRESHOLD}\n")

try:
    while True:
        raw = proc.stdout.read(CHUNK)
        if len(raw) < CHUNK:
            break
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        # Apply gain increase (GAIN_REDUCE < 1 = multiply)
        audio /= GAIN_REDUCE
        # Clip to valid range for model
        audio = np.clip(audio, -1.0, 1.0)
        audio_16k = audio[::RESAMPLE]
        buf.extend(audio_16k)

        if LOG_LEVEL and time.time() - last_log > LOG_LEVEL:
            peak_overall = max(peak_overall, np.max(np.abs(audio)))
            print(f"[{time.strftime('%H:%M:%S')}] Audio peak: {np.max(np.abs(audio)):.4f} | "
                  f"Overall: {peak_overall:.4f} | "
                  f"Buf: {len(buf)} | "
                  f"Detections: {detections}")
            last_log = time.time()

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
