#!/usr/bin/env python3
"""Refresh HA access token for Robi Voice service."""
import json, urllib.request, urllib.parse, os, sys

TOKEN_CACHE = "/home/radxa/stackchan-esphome/xvf3800/ha_token.cache"
AUTH_FILE = "/home/radxa/homeassistant/.storage/auth"
HA_BASE = "http://localhost:8123"

try:
    # Read auth storage
    with open(AUTH_FILE) as f:
        auth = json.load(f)
    
    # Find Robi token
    refresh_tok = None
    for entry in auth["data"].get("refresh_tokens", []):
        if isinstance(entry, dict) and entry.get("client_name") == "Robi":
            refresh_tok = entry.get("token", "")
            break
    
    if not refresh_tok:
        print("ERROR: No Robi token found")
        sys.exit(1)
    
    # Exchange for access token
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_tok
    }).encode()
    
    req = urllib.request.Request(
        f"{HA_BASE}/auth/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        access_token = result.get("access_token", "")
    
    if not access_token:
        print("ERROR: No access token in response")
        sys.exit(1)
    
    # Save to cache
    with open(TOKEN_CACHE, "w") as f:
        f.write(access_token)
    
    os.chmod(TOKEN_CACHE, 0o644)
    print(f"OK: Token refreshed ({access_token[:20]}...)")
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
