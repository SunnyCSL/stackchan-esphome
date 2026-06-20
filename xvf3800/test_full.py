#!/usr/bin/env python3
"""Full pipeline test: record → STT → LLM → TTS → play"""
import asyncio, subprocess, tempfile, os
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import async_read_event, async_write_event
from wyoming.tts import Synthesize

SR = 16000

async def stt(data):
    r,w = await asyncio.open_connection('172.17.0.4',10300)
    await async_write_event(Transcribe(language='zh').event(),w)
    await async_write_event(AudioStart(rate=SR,width=2,channels=1).event(),w)
    for i in range(0,len(data),4096):
        await async_write_event(AudioChunk(rate=SR,width=2,channels=1,audio=data[i:i+4096]).event(),w)
    await async_write_event(AudioStop().event(),w)
    text=''
    while True:
        ev=await async_read_event(r)
        if ev is None: break
        if ev.type=='transcript': text=Transcript.from_event(ev).text
    w.close()
    return text

async def tts(text):
    r,w = await asyncio.open_connection('192.168.1.145',10200)
    await async_write_event(Synthesize(text=text).event(),w)
    audio=b''
    while True:
        ev=await async_read_event(r)
        if ev is None: break
        if ev.type=='audio-chunk': audio+=AudioChunk.from_event(ev).audio
        if ev.type=='audio-stop': break
    w.close()
    return audio

def play(data):
    if not data: return
    with tempfile.NamedTemporaryFile(suffix='.raw',delete=False) as f:
        f.write(data); p=f.name
    subprocess.run(['aplay','-D','plughw:1,0','-r',str(SR),'-c','1','-f','S16_LE','-q',p],timeout=30)
    os.unlink(p)

async def main():
    # 1. Record
    print('🎤 Recording 3s...', flush=True)
    proc = await asyncio.create_subprocess_exec(
        'arecord','-D','plughw:1,0','-r','16000','-c','1','-f','S16_LE','-d','3','-t','raw',
        stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
    audio,_ = await proc.communicate()
    print(f'   {len(audio)} bytes', flush=True)
    if len(audio)<6000: print('⏭️  Quiet'); return
    
    # 2. STT
    print('📝 STT...', flush=True)
    text = await stt(audio)
    print(f'   "{text}"', flush=True)
    if not text.strip(): print('⏭️  No speech'); return
    
    # 3. LLM
    import aiohttp
    print('🤖 LLM...', flush=True)
    async with aiohttp.ClientSession() as s:
        async with s.post('http://127.0.0.1:8081/v1/chat/completions', json={
            'messages':[{'role':'system','content':'You are Robi. Answer in Cantonese, 2 sentences max.'},{'role':'user','content':text}],
            'max_tokens':60,'temperature':0.7,
        }, timeout=aiohttp.ClientTimeout(total=60)) as r:
            reply = (await r.json())['choices'][0]['message']['content']
    print(f'   Robi: {reply}', flush=True)
    
    # 4. TTS
    print('🔊 TTS...', flush=True)
    audio_out = await tts(reply)
    print(f'   {len(audio_out)} bytes', flush=True)
    
    # 5. Play
    print('▶️ Playing...', flush=True)
    play(audio_out)
    
    print('✅ Done!', flush=True)

asyncio.run(main())
