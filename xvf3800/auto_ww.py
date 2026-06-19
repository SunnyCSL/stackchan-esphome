#!/usr/bin/env python3
"""
Wake word auto-start based on Sunny's iPhone presence.
Queries HA recorder SQLite DB for device_tracker.iphone state.
Runs via cron every minute.
"""
import sqlite3, subprocess, os, sys, time
from datetime import datetime

HA_DB = "/home/radxa/homeassistant/home-assistant_v2.db"
WW_VENV = "/home/radxa/stackchan-esphome/xvf3800/venv-ww"
WW_PIPE = "/home/radxa/stackchan-esphome/xvf3800/ww_pipe.py"
PID_FILE = "/tmp/ww_pipe.pid"
AUDIO_DEVICE = "plughw:1,0"
MODEL = "alexa"

def get_phone_state():
    """Get latest device_tracker.iphone state from HA SQLite DB (read-only)."""
    try:
        db = sqlite3.connect(f'file:{HA_DB}?mode=ro', uri=True)
        cur = db.execute("""
            SELECT sm.entity_id, s.state, s.last_updated_ts 
            FROM states s 
            JOIN states_meta sm ON s.metadata_id = sm.metadata_id 
            WHERE sm.entity_id = 'device_tracker.iphone'
            ORDER BY s.last_updated_ts DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        db.close()
        if row:
            return row[1]  # state: 'home' or 'not_home'
    except Exception as e:
        print(f"DB error: {e}", file=sys.stderr)
    return "unknown"

def is_listener_running():
    """Check PID file and process."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            os.remove(PID_FILE)
    return False

def start_listener():
    """Start wake word listener in background."""
    if not os.path.exists(WW_PIPE):
        print(f"ERROR: {WW_PIPE} not found", file=sys.stderr)
        return False
    cmd = [
        f"{WW_VENV}/bin/python3", WW_PIPE,
        "--device", AUDIO_DEVICE,
        "--model", MODEL,
        "--sample-rate", "16000"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(PID_FILE, 'w') as f:
        f.write(str(proc.pid))
    print(f"[{datetime.now():%H:%M:%S}] Wake word listener STARTED (PID {proc.pid})")
    return True

def stop_listener():
    """Stop wake word listener."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 15)
            time.sleep(0.5)
            try:
                os.kill(pid, 0)
                os.kill(pid, 9)  # Force kill
            except OSError:
                pass
        except (ProcessLookupError, ValueError):
            pass
        os.remove(PID_FILE)
        print(f"[{datetime.now():%H:%M:%S}] Wake word listener STOPPED")

if __name__ == "__main__":
    state = get_phone_state()
    running = is_listener_running()
    
    if state == "home" and not running:
        start_listener()
    elif state == "not_home" and running:
        stop_listener()
    elif state == "unknown" and running:
        # Phone state unknown - keep running for 10 min grace period, then stop
        pass  # TODO: add grace period logic
    # else: no change needed (state == "home" + running, or state == "not_home" + not running)
