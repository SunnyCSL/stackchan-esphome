#!/usr/bin/env python3
"""XVF3800 USB mic → arecord 48kHz → downsample 16kHz → openWakeWord → Hermes"""
import subprocess
import numpy as np
import requests
import time
import signal
from scipy import signal as scipy_signal
from openwakeword.model import Model

# Config
ALSA_DEVICE = "hw:1,0"
CAPTURE_RATE = 48000  # XVF3800 USB native rate
TARGET_RATE = 16000   # openWakeWord expects 16kHz
CHUNK_MS = 80
CHUNK_SAMPLES_CAPTURE = CAPTURE_RATE * CHUNK_MS // 1000  # 3840 samples
CHUNK_BYTES = CHUNK_SAMPLES_CAPTURE * 2  # 16-bit = 7680 bytes
HERMES_URL = "http://localhost:5050/wake-word"
MODEL_NAME = "alexa"
THRESHOLD = 0.3
COOLDOWN = 2.0
DEBUG = True  # Print scores every 5s for tuning

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

print(f"🎤 XVF3800 wake word — say '{MODEL_NAME}'", flush=True)
print("Loading model...", flush=True)
oww = Model(wakeword_models=[MODEL_NAME], inference_framework="onnx")
print("✅ Model loaded", flush=True)

last_trigger = 0
running = True

def handle_signal(sig, frame):
    global running
    print("\n👋 Shutting down...", flush=True)
    running = False

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

def downsample(audio_48k):
    """48kHz → 16kHz using scipy resample"""
    target_len = len(audio_48k) * TARGET_RATE // CAPTURE_RATE
    return scipy_signal.resample(audio_48k, target_len)

while running:
    proc = subprocess.Popen(
        ["arecord", "-D", ALSA_DEVICE, "-f", "S16_LE", "-r", str(CAPTURE_RATE),
         "-c", "1", "-t", "raw"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(f"✅ Mic open ({ALSA_DEVICE} @ {CAPTURE_RATE}Hz → {TARGET_RATE}Hz)", flush=True)

    try:
        while running:
            data = proc.stdout.read(CHUNK_BYTES)
            if not data or len(data) < CHUNK_BYTES:
                stderr_out = proc.stderr.read()
                if stderr_out:
                    print(f"⚠️ arecord: {stderr_out.decode()[:200]}", flush=True)
                print("⚠️ Pipe broke — restarting...", flush=True)
                break

            # 48kHz → 16kHz
            audio_48k = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            audio_16k = downsample(audio_48k)

            prediction = oww.predict(audio_16k)
            score = list(prediction.values())[0] if prediction else 0

            if score > THRESHOLD:
                now = time.time()
                if now - last_trigger > COOLDOWN:
                    print(f"🔔 Wake word! (score: {score:.3f})", flush=True)
                    try:
                        r = requests.post(HERMES_URL, json={"wake_word": MODEL_NAME}, timeout=5)
                        print(f"   → Hermes {r.status_code}", flush=True)
                    except Exception as e:
                        print(f"   → Error: {e}", flush=True)
                    last_trigger = now
            
            # Debug: heartbeat + max score
            if DEBUG:
                now_ts = time.time()
                if not hasattr(oww, '_last_debug') or now_ts - oww._last_debug > 5:
                    oww._last_debug = now_ts
                    print(f"   [debug] score={score:.3f} alive", flush=True)

    except BrokenPipeError:
        print("⚠️ Broken pipe — restarting...", flush=True)
    except Exception as e:
        print(f"⚠️ Error: {e} — restarting in 2s...", flush=True)
        time.sleep(2)
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except:
            proc.kill()

print("Stopped.", flush=True)
