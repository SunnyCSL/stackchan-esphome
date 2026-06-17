#!/home/radxa/.hermes/hermes-agent/venv/bin/python3
from __future__ import annotations
"""Hermes Voice Server v2"""
import asyncio
import json
import logging
import os
import struct
import subprocess

import edge_tts
import aiohttp.web as web

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("hermes")

WYOMING_PORT = 10400
HTTP_PORT = 5050
MINIMAX_API_KEY=os.environ.get("STEP_API_KEY", "72Bou6NpuBsJzqcVEv2AAEzUMBLDoe1W8bfv4HQshZZKDd3tbjOkY4YO3MQ56jrOR")
MINIMAX_MODEL = "gpt-4o-mini"  # Step uses OpenAI-compatible models
TTS_VOICE = "zh-CN-XiaoxiaoNeural"

audio_buffer = bytearray()
processing = False

EVENT_AUDIO = b'\x00'
EVENT_WAKE = b'\x01'
EVENT_STT_TEXT = b'\x03'
EVENT_STT_END = b'\x04'

async def wyoming_read_msg(reader: asyncio.StreamReader):
    header = b''
    while len(header) < 5:
        h = await reader.read(5 - len(header))
        if not h:
            return None, None
        header += h
    msg_type = bytes([header[0]])
    msg_len = struct.unpack('>I', header[1:5])[0]
    payload = b''
    while len(payload) < msg_len:
        p = await reader.read(msg_len - len(payload))
        if not p:
            break
        payload += p
    return msg_type, payload

async def wyoming_audio_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global audio_buffer, processing
    addr = writer.get_extra_info('peername')
    logger.info(f"🔊 Wyoming: {addr}")
    audio_buffer.clear()

    try:
        while True:
            msg_type, payload = await wyoming_read_msg(reader)
            if msg_type is None:
                break

            if msg_type == EVENT_AUDIO:
                audio_buffer.extend(payload)

            elif msg_type == EVENT_WAKE:
                data = json.loads(payload.decode('utf-8'))
                logger.info(f"🎤 Wake: {data.get('name','?')} p={data.get('probability',0):.2f}")

            elif msg_type == EVENT_STT_TEXT:
                data = json.loads(payload.decode('utf-8'))
                text = data.get('text', '').strip()
                if text:
                    logger.info(f"🎙️ STT: '{text}'")
                    await handle_transcript(text, writer)

            elif msg_type == EVENT_STT_END:
                logger.info("STT end")

    except Exception as e:
        logger.error(f"Wyoming error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def handle_transcript(text: str, writer: asyncio.StreamWriter):
    global processing
    if processing or not text:
        return
    processing = True

    try:
        # MiniMax LLM
        logger.info(f"🤖 LLM: {text[:60]}")
        import openai
        client = openai.OpenAI(api_key=MINIMAX_API_KEY, base_url="https://api.stepfun.ai/step_plan/v1")
        resp = client.chat.completions.create(
            model=MINIMAX_MODEL,
            messages=[
                {"role": "system", "content": "你是 Sunny 的智能助手 Robi，用繁體中文回答，簡短自然。"},
                {"role": "user", "content": text}
            ],
            max_tokens=256,
            temperature=0.7
        )
        reply = resp.choices[0].message.content
        logger.info(f"💬 {reply[:60]}")

        # Edge TTS
        logger.info(f"🔊 TTS: {reply[:40]}")
        tts_file = "/tmp/robi_tts.wav"
        await edge_tts.Communicate(reply, TTS_VOICE).save(tts_file)

        # Convert to PCM 16kHz mono
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", tts_file, "-ar", "16000", "-ac", "1",
             "-f", "s16le", "-acodec", "pcm_s16le", "-"],
            capture_output=True
        )
        pcm = result.stdout
        logger.info(f"🔊 PCM: {len(pcm)} bytes")

        if pcm and writer:
            for i in range(0, len(pcm), 1024):
                chunk = pcm[i:i+1024]
                msg = struct.pack('>BI', EVENT_AUDIO[0], len(chunk)) + chunk
                writer.write(msg)
                await writer.drain()
            end_msg = struct.pack('>BI', EVENT_STT_END[0], 0)
            writer.write(end_msg)
            await writer.drain()

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
    finally:
        processing = False

async def http_handler(request: web.Request) -> web.Response:
    path = request.path

    if path == "/wake-word" and request.method == "POST":
        try:
            data = await request.json()
            logger.info(f"🎤 Wake: {data.get('wake_word')} from {data.get('device')}")
            return web.json_response({"status": "ok"})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    if path == "/health":
        return web.json_response({
            "status": "running",
            "llm": "✅ Step" if MINIMAX_API_KEY else "⚠️ NO KEY",
        })

    return web.Response(status=404, text="Not Found")

async def main():
    app = web.Application()
    app.router.add_post("/wake-word", http_handler)
    app.router.add_get("/health", http_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HTTP_PORT)
    await site.start()
    logger.info(f"🚀 HTTP :{HTTP_PORT}")

    srv = await asyncio.start_server(wyoming_audio_handler, "0.0.0.0", WYOMING_PORT)
    logger.info(f"🔊 Wyoming :{WYOMING_PORT}")
    logger.info(f"📋 LLM: {'✅ Step ' + MINIMAX_MODEL if MINIMAX_API_KEY else '⚠️ set STEP_API_KEY'}")
    logger.info("Ready!")

    await asyncio.Event().wait()

if __name__ == "__main__":
    print("STEP_API_KEY:", "SET ✅" if MINIMAX_API_KEY else "⚠️ MISSING")
    asyncio.run(main())
