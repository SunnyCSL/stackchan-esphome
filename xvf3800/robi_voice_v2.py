#!/usr/bin/env python3
"""
Robi Voice v2 — 3-Layer Architecture
======================================
1. Trigger word detection (本地 keyword — instant)
2. Intent classifier (DeepSeek API — fast & accurate)
   ├─ HA command → HA REST API directly
   └─ Complex conversation → DeepSeek API (Robi persona)
3. TTS output via Wyoming piper → USB speaker
"""
import asyncio, logging, os, sys, tempfile, json, urllib.request, urllib.parse, signal
import aiohttp

logger = logging.getLogger("robi_voice_v2")

# ── Config ──
WHISPER_HOST = "172.17.0.4"
WHISPER_PORT = 10300
PIPER_HOST = "192.168.1.145"
PIPER_PORT = 10200
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

XMOS_CARD = "plughw:1,0"
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
CHANNELS = 1

# Trigger word list (rapid keyword matching)
TRIGGER_WORDS = ["robi", "roby", "okay robi", "okay roby"]

# HA
HA_BASE = "http://localhost:8123"

# DeepSeek
DEEPSEEK_KEY = ""

ROBI_SYSTEM_PROMPT = """你係 Robi，一個智能家居管家。
主人係 Sunny。
語言：繁體中文，口語化粵語。
風格：簡潔、有禮、直接回答。
如果係問候或閒聊，輕鬆回覆就得。如果係問題，直接俾答案。
回覆控制在 50 字內。"""

CLASSIFIER_SYSTEM = """你係 intent classifier。分析用戶句子嘅意圖。

label 定義：
- home_automation：控制家居裝置（開關燈、冷氣溫度、窗簾、風扇、電視、鎖門等）
- conversation：閒聊、問問題、research、要求解釋、傾偈、講故事、問意見

只輸出一個字：home_automation 或 conversation。唔好加任何其他字。"""

HA_COMMAND_PROMPT = """你係 HA command parser。以下係粵語家居控制指令，請輸出對應 HA API call。

可用 service 同 entity_id 格式：
- 燈：service=light.turn_on/turn_off, entity_id=light.yeelink_*
- 冷氣：service=climate.set_temperature/set_hvac_mode, entity_id=climate.*
- 窗簾：service=cover.open_cover/close_cover, entity_id=cover.*
- 電視：service=media_player.turn_on/turn_off, entity_id=media_player.*
- 風扇：service=fan.turn_on/turn_off, entity_id=fan.*
- 全部/所有燈：service=light.turn_off, entity_id=all

只輸出純 JSON，唔可以有 markdown 格式：
{"service": "light.turn_off", "entity_id": "light.yeelink_*", "data": {}}
如果有 entity_id 入面唔肯定，用 * 做 wildcard。
如果完全唔明，輸出 {"error": "你講邊個設備？"}"""


def load_keys() -> str:
    """Load DeepSeek key from .env file."""
    env_path = "/home/radxa/.hermes/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "DEEPSEEK_API_KEY" in line and "=" in line:
                    key = line.split("=", 1)[1].strip("\"'")
                    if key:
                        return key
    return ""


HA_TOKEN_CACHE = "/home/radxa/stackchan-esphome/xvf3800/ha_token.cache"


def get_ha_token() -> str:
    """Read cached HA access token."""
    try:
        if os.path.exists(HA_TOKEN_CACHE):
            with open(HA_TOKEN_CACHE) as f:
                token = f.read().strip()
                if token:
                    return token
        return ""
    except Exception as e:
        logger.error(f"HA token read failed: {e}")
        return ""


async def stt(audio_data: bytes) -> str:
    from wyoming.asr import Transcribe, Transcript
    from wyoming.audio import AudioChunk, AudioStart, AudioStop
    from wyoming.event import async_read_event, async_write_event
    try:
        r, w = await asyncio.wait_for(
            asyncio.open_connection(WHISPER_HOST, WHISPER_PORT), timeout=5
        )
    except asyncio.TimeoutError:
        logger.error("STT connection timeout")
        return ""
    await async_write_event(Transcribe(language="zh").event(), w)
    await async_write_event(
        AudioStart(rate=SAMPLE_RATE, width=SAMPLE_WIDTH, channels=CHANNELS).event(), w
    )
    for i in range(0, len(audio_data), 4096):
        chunk = audio_data[i : i + 4096]
        await async_write_event(
            AudioChunk(rate=SAMPLE_RATE, width=SAMPLE_WIDTH, channels=CHANNELS, audio=chunk).event(), w
        )
    await async_write_event(AudioStop().event(), w)
    text = ""
    try:
        while True:
            ev = await asyncio.wait_for(async_read_event(r), timeout=15)
            if ev is None:
                break
            if ev.type == "transcript":
                text = Transcript.from_event(ev).text
                break  # Got the transcript, stop waiting
    except asyncio.TimeoutError:
        logger.warning("STT response timeout")
    except Exception as e:
        logger.error(f"STT error: {e}")
    finally:
        w.close()
    return text


async def deepseek_call(messages: list, max_tokens: int = 50, temperature: float = 0.1) -> str:
    """Generic DeepSeek API caller."""
    if not DEEPSEEK_KEY:
        return ""
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(DEEPSEEK_URL, json=payload,
                headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
                timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.error(f"DeepSeek error {resp.status}")
                    return ""
                data = await resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        logger.error(f"DeepSeek API error: {e}")
        return ""


async def classify_intent(text: str) -> str:
    """Classify intent using DeepSeek API."""
    reply = await deepseek_call([
        {"role": "system", "content": CLASSIFIER_SYSTEM},
        {"role": "user", "content": text}
    ], max_tokens=10, temperature=0.01)
    reply = reply.strip().lower()
    if "home_automation" in reply:
        return "home_automation"
    return "conversation"


async def call_ha(text: str) -> str:
    """Parse and execute HA command via DeepSeek + HA API."""
    token = get_ha_token()
    if not token:
        return "系統錯誤：HA 連接失敗"

    # Step 1: Parse command with DeepSeek
    reply = await deepseek_call([
        {"role": "system", "content": HA_COMMAND_PROMPT},
        {"role": "user", "content": text}
    ], max_tokens=100, temperature=0.05)
    
    if not reply:
        return "唔好意思，我聽唔明"

    # Step 2: Parse JSON response
    try:
        # Strip any markdown code blocks
        clean = reply.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0].strip()
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0].strip()
        cmd = json.loads(clean)
    except (json.JSONDecodeError, IndexError):
        logger.error(f"HA parse failed: {reply}")
        return "我唔係好明你想點控制"

    if "error" in cmd:
        return cmd["error"]

    # Step 3: Call HA API
    try:
        service = cmd["service"]
        entity_id = cmd["entity_id"]
        
        if entity_id == "all":
            # Handle "all" special case
            all_lights = json.dumps({}).encode()
            req = urllib.request.Request(
                f"{HA_BASE}/api/services/{service.replace('.', '/')}",
                data=all_lights,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
            )
        else:
            ha_data = json.dumps({
                "entity_id": entity_id,
                **cmd.get("data", {})
            }).encode()
            req = urllib.request.Request(
                f"{HA_BASE}/api/services/{service.replace('.', '/')}",
                data=ha_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
            )
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=10))
        return "搞掂 ✅"
    except urllib.error.HTTPError as e:
        return f"執行失敗 ({e.code})"
    except Exception as e:
        logger.error(f"HA call failed: {e}")
        return "系統錯誤"


async def converse(text: str) -> str:
    """Complex conversation via DeepSeek."""
    return await deepseek_call([
        {"role": "system", "content": ROBI_SYSTEM_PROMPT},
        {"role": "user", "content": text}
    ], max_tokens=200, temperature=0.7)


async def tts(text: str) -> bytes:
    from wyoming.tts import Synthesize
    from wyoming.audio import AudioChunk, AudioStop
    from wyoming.event import async_read_event, async_write_event
    r, w = await asyncio.open_connection(PIPER_HOST, PIPER_PORT)
    await async_write_event(Synthesize(text=text).event(), w)
    audio = b""
    while True:
        ev = await async_read_event(r)
        if ev is None:
            break
        if ev.type == "audio-chunk":
            audio += AudioChunk.from_event(ev).audio
        if ev.type == "audio-stop":
            break
    w.close()
    return audio


async def record(duration: float = 4.0) -> bytes:
    """Record from XMOS USB mic. Kills stale arecord first."""
    # Kill any stale arecord from previous cycles
    proc_kill = await asyncio.create_subprocess_exec(
        "killall", "-9", "arecord",
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL
    )
    await proc_kill.wait()
    await asyncio.sleep(0.5)  # Let ALSA release the device
    
    print("🔴 Recording...", end=" ", flush=True)
    proc = await asyncio.create_subprocess_exec(
        "arecord",
        "-D", XMOS_CARD,
        "-r", str(SAMPLE_RATE),
        "-c", "1",
        "-f", "S16_LE",
        "-d", str(int(duration)),
        "-t", "raw",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    print(f"({len(out)} bytes)")
    if err:
        print(f"  stderr: {err.decode()[:100]}")
    return out


def play(audio_data: bytes):
    if not audio_data:
        return
    with tempfile.NamedTemporaryFile(suffix=".raw", delete=False) as f:
        f.write(audio_data)
        p = f.name
    try:
        import subprocess
        subprocess.run(
            ["aplay", "-D", XMOS_CARD, "-r", str(SAMPLE_RATE), "-c", "1", "-f", "S16_LE", p],
            check=True, timeout=60,
        )
    except Exception as e:
        logger.error(f"aplay: {e}")
    finally:
        os.unlink(p)


def match_trigger(text: str) -> bool:
    """Quick keyword trigger matching (flexible, handles STT variations)."""
    t = text.lower().strip()
    # Exact prefix match
    for tw in TRIGGER_WORDS:
        if t.startswith(tw):
            return True
    # Also check contains (for STT variations)
    for tw in ["robi", "roby", "攞你", "老皮", "奴隸筆", "蘿蔔", "諾比", "路比", "盧比"]:
        if tw in t:
            return True
    return False


def strip_trigger(text: str) -> str:
    """Remove trigger word from start of text."""
    t = text.strip()
    for tw in sorted(TRIGGER_WORDS, key=len, reverse=True):
        if t.lower().startswith(tw):
            return t[len(tw):].strip()
    # For contains match, strip first occurrence
    for tw in ["robi", "roby"]:
        idx = t.lower().find(tw)
        if idx >= 0:
            return t[:idx].strip() + " " + t[idx+len(tw):].strip()
    return t


async def speak(text: str):
    if not text:
        return
    print(f"🔊 {text}")
    audio = await tts(text)
    play(audio)


async def main_loop():
    global DEEPSEEK_KEY
    DEEPSEEK_KEY = load_keys()

    print("=" * 50)
    print("🎙️  Robi Voice v2 — 3-Layer Architecture")
    print(f"   Trigger: {TRIGGER_WORDS[0]}  |  Classify: DeepSeek  |  Conv: DeepSeek")
    print("=" * 50)

    # Health check
    for name, host, port in [
        ("Whisper", WHISPER_HOST, WHISPER_PORT),
        ("Piper", PIPER_HOST, PIPER_PORT),
    ]:
        try:
            r, w = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=3)
            w.close()
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")

    # Check HA
    ha_token = get_ha_token()
    print(f"{'✅' if ha_token else '❌'} HA API")

    # Check DeepSeek
    if DEEPSEEK_KEY:
        print(f"✅ DeepSeek API ({DEEPSEEK_KEY[:8]}...{DEEPSEEK_KEY[-4:]})")
    else:
        print("❌ DeepSeek API — no key")

    print(f"\n🎤 Say \"{TRIGGER_WORDS[0]}\" to start... (4s cycles)\n")

    while True:
        try:
            audio = await record(4.0)
            if len(audio) < 8000:
                continue

            text = await stt(audio)
            if not text or len(text.strip()) < 1:
                continue
            print(f'👂 "{text}"')

            # Fast keyword trigger check
            if not match_trigger(text):
                print("⏭️  No trigger")
                continue

            # Strip trigger word
            cmd_text = strip_trigger(text)
            if not cmd_text:
                await speak("係？")
                continue

            print(f"🔍 Classifying...")
            intent = await classify_intent(cmd_text)
            print(f"→ {intent}")

            if intent == "home_automation":
                print(f"🔧 HA: {cmd_text}")
                reply = await call_ha(cmd_text)
            else:
                print(f"💬 DeepSeek: {cmd_text}")
                reply = await converse(cmd_text)

            await speak(reply or "唔好意思")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Cleanup handler for systemd stop
    def cleanup(*args):
        import subprocess
        subprocess.run(["killall", "-9", "arecord"], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    
    asyncio.run(main_loop())
