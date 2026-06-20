#!/usr/bin/env python3
"""One-shot voice test: record → STT → LLM → TTS → play"""
import asyncio, logging, os, tempfile, sys
sys.stdout.reconfigure(line_buffering=True)

from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import async_read_event, async_write_event
from wyoming.tts import Synthesize

SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
CHANNELS = 1

async def stt(audio_data):
    r, w = await asyncio.open_connection('172.17.0.4', 10300)
    await async_write_event(Transcribe(language='zh').event(), w)
    await async_write_event(AudioStart(rate=SAMPLE_RATE, width=SAMPLE_WIDTH, channels=CHANNELS).event(), w)
    for i in range(0, len(audio_data), 4096):
        await async_write_event(AudioChunk(rate=SAMPLE_RATE, width=SAMPLE_WIDTH, channels=CHANNELS, audio=audio_data[i:i+4096]).event(), w)
    await async_write_event(AudioStop().event(), w)
    text = ''
    while True:
        ev = await async_read_event(r)
        if ev is None: break
        if ev.type == 'transcript': text = Transcript.from_event(ev).text
    w.close()
    return text

async def tts(text):
    r, w = await asyncio.open_connection('192.168.1.145', 10200)
    await async_write_event(Synthesize(text=text).event(), w)
    audio = b''
    while True:
        ev = await async_read_event(r)
        if ev is None: break
        if ev.type == 'audio-chunk': audio += AudioChunk.from_event(ev).audio
        if ev.type == 'audio-stop': break
    w.close()
    return audio

def play(audio_data):
    if not audio_data: return
    with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as f:
        f.write(audio_data); p = f.name
    os.system(f'aplay -D plughw:1,0 -r {SAMPLE_RATE} -c 1 -f S16_LE -q "{p}" 2>/dev/null')
    os.unlink(p)

async def main():
    print('=== Robi Voice - One Shot Test ===')
    print('1. Recording 4s...', end=' ', flush=True)
    audio = open('/tmp/test_audio.raw', 'rb').read() if os.path.exists('/tmp/test_audio.raw') else None
    
    if not audio:
        proc = await asyncio.create_subprocess_exec(
            'arecord', '-D', 'plughw:1,0', '-r', '16000', '-c', '1', '-f', 'S16_LE',
            '-d', '4', '-t', 'raw', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        audio, _ = await proc.communicate()
        # Save for reuse
        with open('/tmp/test_audio.raw', 'wb') as f: f.write(audio)
    
    print(f'{len(audio)} bytes')
    
    if len(audio) < 8000:
        print('Too quiet!')
        return
    
    print('2. Transcribing...', end=' ', flush=True)
    text = await stt(audio)
    print(f'"{text}"')
    
    if not text.strip():
        print('No speech detected')
        return
    
    print(f'3. You said: {text}')
    print('4. Robi thinking...', end=' ', flush=True)
    
    import aiohttp
    async with aiohttp.ClientSession() as s:
        async with s.post('http://127.0.0.1:8081/v1/chat/completions', json={
            'messages': [
                {'role':'system','content':'You are Robi, a Cantonese-speaking smart home assistant.'},
                {'role':'user','content':text}
            ],
            'max_tokens':60,
            'temperature':0.7,
        }, timeout=aiohttp.ClientTimeout(total=120)) as r:
            data = await r.json()
            reply = data['choices'][0]['message']['content']
    
    print(f'Robi: {reply}')
    
    if reply:
        print('5. Synthesizing speech...', end=' ', flush=True)
        tts_audio = await tts(reply)
        print(f'{len(tts_audio)} bytes')
        print('6. Playing...', flush=True)
        play(tts_audio)
    
    print('✅ Done!')

asyncio.run(main())
