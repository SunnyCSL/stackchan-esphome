#!/usr/bin/env python3
"""Wake word auto-start based on presence."""
import json, urllib.request, urllib.error, urllib.parse
import subprocess, os, sys, time
from datetime import datetime

HA_BASE = "http://localhost:8123"
HA_AUTH_FILE="/home/radxa/stackchan-esphome/xvf3800/.ha_ios_token"
WW_VENV = "/home/radxa/stackchan-esphome/xvf3800/venv-ww"
WW_PIPE = "/home/radxa/stackchan-esphome/xvf3800/ww_pipe.py"
PID_FILE = "/tmp/ww_pipe.pid"
AUDIO_DEVICE = "plughw:1,0"
MODEL = "alexa"
IPHONE_IPS = ["192.168.1.158", "192.168.1.188", "192.168.1.189", "192.168.1.190"]

def get_ha_access_token():
    try:
        with open(HA_AUTH_FILE) as f:
            refresh_token = f.read().strip()
        if not refresh_token:
            return None
        body = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": "https://home-assistant.io/iOS"
        }).encode()
        req = urllib.request.Request(HA_BASE + "/auth/token", data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        resp = urllib.request.urlopen(req, timeout=5)
        result = json.loads(resp.read())
        return result.get("access_token")
    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] HA token error: {e}", file=sys.stderr)
        return None

def get_phone_state_via_api(token):
    try:
        req = urllib.request.Request(
            HA_BASE + "/api/states/person.sunnycsl",
            headers={"Authorization": "Bearer " + token}
        )
        resp = urllib.request.urlopen(req, timeout=5)
        state = json.loads(resp.read())
        return state.get("state", "unknown")
    except Exception as e:
        print(f"[{datetime.now():%H:%M:%S}] HA API error: {e}", file=sys.stderr)
        return "unknown"

def check_network_presence():
    for ip in IPHONE_IPS:
        try:
            resp = subprocess.run(["ping", "-c1", "-W1", ip], capture_output=True, timeout=3)
            if resp.returncode == 0:
                return True
        except:
            continue
    return False

def is_listener_running():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            try:
                os.remove(PID_FILE)
            except:
                pass
    return False

def start_listener():
    if not os.path.exists(WW_PIPE):
        print(f"[{datetime.now():%H:%M:%S}] ERROR: {WW_PIPE} not found", file=sys.stderr)
        return False
    cmd = [WW_VENV + "/bin/python3", WW_PIPE, "--device", AUDIO_DEVICE, "--model", MODEL, "--sample-rate", "16000"]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    print(f"[{datetime.now():%H:%M:%S}] Wake word listener STARTED (PID {proc.pid})")
    return True

def stop_listener():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 15)
            time.sleep(0.5)
            try:
                os.kill(pid, 0)
                os.kill(pid, 9)
            except OSError:
                pass
        except (ProcessLookupError, ValueError, FileNotFoundError):
            pass
        try:
            os.remove(PID_FILE)
        except:
            pass
        print(f"[{datetime.now():%H:%M:%S}] Wake word listener STOPPED")

if __name__ == "__main__":
    running = is_listener_running()
    token = get_ha_access_token()
    state = get_phone_state_via_api(token) if token else "unknown"
    print(f"[{datetime.now():%H:%M:%S}] HA state: {state}")

    if state in ("unknown", "unavailable"):
        on_network = check_network_presence()
        if on_network:
            state = "home"
            print(f"[{datetime.now():%H:%M:%S}] Net presence: iPhone detected on LAN")
    if state == "home" and not running:
        start_listener()
    elif state == "not_home" and running:
        stop_listener()
    else:
        print(f"[{datetime.now():%H:%M:%S}] No action needed (state={state}, running={running})")
