#!/usr/bin/env python3
"""
Robi Voice — Radxa + XMOS USB + Wyoming STT/TTS + Local LLM
Pipeline: USB mic → Wyoming STT → Local llama-server → Wyoming TTS → USB speaker
"""
import asyncio, logging, os, tempfile
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import async_read_event, async_write_event
from wyoming.tts import Synthesize

logger = logging.getLogger("robi_voice")

# ── Config ──
WHISPER_HOST = "172.17.0.4"
WHISPER_PORT = 10300
PIPER_HOST = "192.168.1.145"
PIPER_PORT = 10200
LLAMA_URL = "http://127.0.0.1:8081/v1/chat/completions"

XMOS_CARD = "plughw:1,0"
SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
CHANNELS = 1

ROBI_PROMPT = """你係 Robi，一個智能家居管家。
你嘅主人係 Sunny。
語言：繁體中文、口語化粵語。
風格：簡潔、有禮、直接回答。如果唔明就問清楚。"""


async def stt(audio_data: bytes) -> str:
    """Wyoming STT via faster-whisper."""
    r, w = await asyncio.open_connection(WHISPER_HOST, WHISPER_PORT)
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
    while True:
        ev = await async_read_event(r)
        if ev is None:
            break
        if ev.type == "transcript":
            text = Transcript.from_event(ev).text
    w.close()
    return text


async def converse(text: str) -> str:
    """Local llama-server (nemotron-nano-4b)."""
    import aiohttp
    payload = {
        "messages": [
            {"role": "system", "content": ROBI_PROMPT},
            {"role": "user", "content": text},
        ],
        "max_tokens": 60,
        "temperature": 0.7,
    }
    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            LLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            if resp.status != 200:
                err = await resp.text()
                logger.error(f"LLM error {resp.status}: {err[:200]}")
                return f"系統錯誤 ({resp.status})"
            data = await resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")


async def tts(text: str) -> bytes:
    """Wyoming TTS via piper."""
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
    """Record from XMOS USB mic."""
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
    out, _ = await proc.communicate()
    return out


def play(audio_data: bytes):
    """Play through XMOS USB speaker."""
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


async def main_loop():
    """Continuous loop: listen → transcribe → think → speak."""
    print("=" * 50)
    print("🎙️  Robi Voice — XMOS USB + Local LLM + Wyoming")
    print("=" * 50)

    # Test connections
    for name, host, port in [
        ("Whisper", WHISPER_HOST, WHISPER_PORT),
        ("Piper", PIPER_HOST, PIPER_PORT),
        ("Llama", "127.0.0.1", 8081),
    ]:
        try:
            r, w = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=3
            )
            w.close()
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")

    print("\n🎤 Ready! (recording 4s chunks)\n")

    while True:
        try:
            print("🔴 Recording 4s...", end=" ", flush=True)
            audio = await record(4.0)
            print(f"({len(audio)} bytes)")

            if len(audio) < 8000:
                print("⏭️  Too quiet")
                continue

            print("📝 Transcribing...", end=" ", flush=True)
            text = await stt(audio)
            print(f'"{text}"')

            if not text or len(text.strip()) < 1:
                print("⏭️  No speech")
                continue

            print("🤖 Robi thinking...", end=" ", flush=True)
            reply = await converse(text)
            print(reply)

            if reply:
                print("🔊 Speaking...", end=" ", flush=True)
                tts_audio = await tts(reply)
                play(tts_audio)
                print("✅")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main_loop())
