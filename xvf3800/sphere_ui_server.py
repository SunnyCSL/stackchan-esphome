#!/home/radxa/.hermes/hermes-agent/venv/bin/python3
"""Sphere UI Voice Server — press-to-talk web interface"""
import asyncio
import logging
import os
import struct
import subprocess
import aiohttp.web as web
import edge_tts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("sphere")

STEP_API_KEY=os.environ.get("STEP_API_KEY", "72Bou6NpuBsJzqcVEv2AAEzUMBLDoe1W8bfv4HQshZZKDd3tbjOkY4YO3MQ56jrOR")
TTS_VOICE = "zh-HK-HiuGaaiNeural"
HTTP_PORT = 8080
HTTPS_PORT = 8443
SSL_CERT = "/home/radxa/.caddy/ssl/sphere.crt"
SSL_KEY = "/home/radxa/.caddy/ssl/sphere.key"

html = """<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Robi — Sphere Voice</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: #0a0a0f;
  color: #e0e0f0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
#sphere {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #2a2a4a, #0a0a1a);
  border: 3px solid #3a3a6a;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 0 40px rgba(80,80,200,0.2), inset 0 0 30px rgba(50,50,150,0.1);
  position: relative;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}
#sphere:active, #sphere.listening {
  background: radial-gradient(circle at 30% 30%, #3a3a6a, #1a1a3a);
  border-color: #6a6aaa;
  box-shadow: 0 0 60px rgba(100,100,255,0.4), inset 0 0 40px rgba(80,80,200,0.2);
  transform: scale(0.97);
}
#sphere.wave::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #6a6aaa;
  animation: ripple 1.2s ease-out infinite;
}
@keyframes ripple {
  0%   { transform: scale(1);   opacity: 0.8; }
  100% { transform: scale(1.5); opacity: 0; }
}
#sphere_icon {
  font-size: 48px;
  transition: opacity 0.15s;
}
.wave #sphere_icon { opacity: 0; }
#hint {
  margin-top: 24px;
  font-size: 14px;
  color: #6a6a8a;
  text-align: center;
  min-height: 20px;
}
#response {
  position: absolute;
  bottom: 80px;
  left: 16px;
  right: 16px;
  text-align: center;
  font-size: 15px;
  color: #a0a0c0;
  min-height: 48px;
  padding: 12px 16px;
  background: rgba(30,30,60,0.6);
  border-radius: 12px;
  backdrop-filter: blur(8px);
  word-break: break-word;
  display: none;
}
#response.show { display: block; }
#response .llm-text { margin-bottom: 8px; line-height: 1.5; }
#response .tts-status { font-size: 12px; color: #5a5a7a; }
#text_fallback {
  position: absolute;
  bottom: 20px;
  display: flex;
  gap: 8px;
  width: 90%;
  max-width: 400px;
}
#text_input {
  flex: 1;
  background: rgba(30,30,60,0.8);
  border: 1px solid #3a3a6a;
  border-radius: 24px;
  padding: 12px 18px;
  color: #e0e0f0;
  font-size: 15px;
  outline: none;
}
#text_input:focus { border-color: #6a6aaa; }
#text_send {
  background: #3a3a6a;
  border: none;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  color: #e0e0f0;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
</head>
<body>

<div id="sphere" ontouchstart="startRecording()" ontouchend="stopRecording()" onclick="toggleRecording()">
  <div id="sphere_icon">🎤</div>
</div>
<div id="hint">按住說話</div>
<div id="response"><div class="llm-text"></div><div class="tts-status"></div></div>

<div id="text_fallback">
  <input type="text" id="text_input" placeholder="或者打字..." onkeydown="if(event.key==='Enter')sendText()">
  <button id="text_send" onclick="sendText()">➤</button>
</div>

<script>
const sphere = document.getElementById('sphere');
const hint = document.getElementById('hint');
const response = document.getElementById('response');
const llmText = response.querySelector('.llm-text');
const ttsStatus = response.querySelector('.tts-status');
const textInput = document.getElementById('text_input');

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let recognition = null;
let stream = null;

// Speech recognition (browser built-in)
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = 'zh-HK';
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.onresult = (e) => {
    const text = e.results[0][0].transcript;
    logger('🎤 STT: ' + text);
    sendTextToServer(text);
  };
  recognition.onerror = (e) => {
    logger('❌ STT error: ' + e.error);
    resetUI();
  };
  recognition.onend = () => { if (isRecording) recognition.start(); };
}

function logger(msg) { console.log(msg); }

async function startRecording() {
  if (isRecording) return;
  isRecording = true;
  audioChunks = [];
  sphere.classList.add('listening', 'wave');
  hint.textContent = '鬆開停止';

  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
    mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunks.push(e.data); };
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      await sendAudio(blob);
    };
    mediaRecorder.start();
  } catch (e) {
    logger('Mic error: ' + e);
    resetUI();
  }
}

function stopRecording() {
  if (!isRecording) return;
  isRecording = false;
  sphere.classList.remove('listening', 'wave');
  hint.textContent = '處理中...';
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
  if (stream) stream.getTracks().forEach(t => t.stop());
}

function toggleRecording() { /* desktop click fallback */ }

function resetUI() {
  sphere.classList.remove('listening', 'wave');
  hint.textContent = '按住說話';
  isRecording = false;
  audioChunks = [];
}

async function sendAudio(blob) {
  try {
    const formData = new FormData();
    formData.append('audio', blob, 'recording.webm');
    llmText.textContent = '🎤 辨識中...';
    ttsStatus.textContent = '';
    response.classList.add('show');

    const resp = await fetch('/voice', { method: 'POST', body: formData });
    const data = await resp.json();
    handleResponse(data);
  } catch (e) {
    llmText.textContent = '❌ 錯誤: ' + e.message;
    ttsStatus.textContent = '';
    setTimeout(resetUI, 2000);
  }
}

async function sendText() {
  const text = textInput.value.trim();
  if (!text) return;
  textInput.value = '';
  llmText.textContent = '🤖 思考中...';
  ttsStatus.textContent = '';
  response.classList.add('show');

  try {
    const resp = await fetch('/text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await resp.json();
    handleResponse(data);
  } catch (e) {
    llmText.textContent = '❌ 錯誤: ' + e.message;
    setTimeout(resetUI, 2000);
  }
}

let audioQueue = [];
let isPlaying = false;

function handleResponse(data) {
  if (data.error) {
    llmText.textContent = '❌ ' + data.error;
    setTimeout(resetUI, 3000);
    return;
  }
  llmText.textContent = '🤖 ' + data.reply;
  ttsStatus.textContent = '🔊 播放語音...';

  // Play TTS audio
  if (data.audio_url) {
    const audio = new Audio(data.audio_url);
    audio.onended = () => {
      ttsStatus.textContent = '✅ 完成';
      setTimeout(resetUI, 1500);
    };
    audio.onerror = () => {
      ttsStatus.textContent = '❌ 播放失敗';
      setTimeout(resetUI, 2000);
    };
    audio.play().catch(e => {
      ttsStatus.textContent = '❌ ' + e.message;
      setTimeout(resetUI, 2000);
    });
  } else {
    ttsStatus.textContent = '';
    setTimeout(resetUI, 3000);
  }
}
</script>
</body>
</html>"""

async def handle_voice(request):
    """Receive audio blob, transcribe via browser Web Speech API (client-side),
       then send text to LLM and return TTS URL."""
    try:
        reader = await request.multipart()
        field = await reader.next()
        if field is None:
            return web.json_response({"error": "no audio"}, status=400)

        # Read the audio file
        audio_data = bytearray()
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            audio_data.extend(chunk)

        # Convert webm/opus to wav using ffmpeg
        import tempfile, uuid, os
        webm_path = f"/tmp/voice_{uuid.uuid4().hex}.webm"
        wav_path = f"/tmp/voice_{uuid.uuid4().hex}.wav"
        with open(webm_path, 'wb') as f:
            f.write(audio_data)

        # ffmpeg: webm (opus) -> 16kHz mono wav
        result = subprocess.run([
            "ffmpeg", "-y", "-i", webm_path,
            "-ar", "16000", "-ac", "1",
            "-c:a", "pcm_s16le", wav_path
        ], capture_output=True)

        os.unlink(webm_path)

        if result.returncode != 0:
            logger.error(f"ffmpeg error: {result.stderr.decode()}")
            return web.json_response({"error": "audio conversion failed"}, status=500)

        # For now: return TTS directly without STT (browser does STT client-side)
        # This endpoint receives already-transcribed audio, just do LLM+TTS
        return web.json_response({"status": "ok", "note": "use /text endpoint with transcribed text"})

    except Exception as e:
        logger.error(f"Voice error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_text(request):
    """Text input -> LLM -> TTS -> return audio URL"""
    try:
        data = await request.json()
        text = data.get("text", "").strip()
        if not text:
            return web.json_response({"error": "empty text"}, status=400)

        logger.info(f"🤖 LLM: {text[:60]}")

        # LLM via Step API
        import openai
        client = openai.OpenAI(
            api_key=STEP_API_KEY,
            base_url="https://api.stepfun.ai/step_plan/v1"
        )
        resp = client.chat.completions.create(
            model="step-3.5-flash",
            messages=[
                {"role": "system", "content": "你是 Sunny 的智能助手 Robi，用繁體中文回答，簡短自然，廣東話優先。"},
                {"role": "user", "content": text}
            ],
            max_tokens=256,
            temperature=0.7
        )
        reply = (resp.choices[0].message.content or "").strip()
        if not reply:
            return web.json_response({"error": "empty response from LLM"}, status=502)
        logger.info(f"💬 {reply[:60]}")

        # TTS
        import tempfile, uuid, os
        tts_file = f"/tmp/tts_{uuid.uuid4().hex}.wav"
        await edge_tts.Communicate(reply, TTS_VOICE).save(tts_file)

        # Convert to mp3 for browser compatibility
        mp3_file = f"/tmp/tts_{uuid.uuid4().hex}.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-i", tts_file,
            "-codec:a", "libmp3lame", "-q:a", "2",
            mp3_file
        ], capture_output=True)

        os.unlink(tts_file)

        audio_url = f"/audio/{os.path.basename(mp3_file)}"
        return web.json_response({"reply": reply, "audio_url": audio_url})

    except Exception as e:
        logger.error(f"Text error: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def handle_ca_cert(request):
    """Serve CA certificate for iPhone installation"""
    path = "/home/radxa/.caddy/ssl/ca.crt"
    if not os.path.exists(path):
        return web.Response(status=404, text="CA cert not found")
    return web.FileResponse(path, headers={"Content-Disposition": "attachment; filename=Robi_Local_CA.crt"})

async def handle_audio_file(request):
    """Serve generated TTS audio files"""
    filename = request.match_info['filename']
    path = f"/tmp/{filename}"
    if not os.path.exists(path):
        return web.Response(status=404)
    return web.FileResponse(path)

async def handle_index(request):
    return web.Response(text=html, content_type='text/html')

async def main():
    import ssl as ssl_mod

    ssl_ctx = ssl_mod.SSLContext(ssl_mod.PROTOCOL_TLS_SERVER)
    ssl_ctx.load_cert_chain(SSL_CERT, SSL_KEY)

    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_post('/voice', handle_voice)
    app.router.add_post('/text', handle_text)
    app.router.add_get('/audio/{filename}', handle_audio_file)
    app.router.add_get('/ca', handle_ca_cert)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", HTTPS_PORT, ssl_context=ssl_ctx)
    await site.start()
    logger.info(f"🌐 Sphere UI: https://0.0.0.0:{HTTPS_PORT}")
    logger.info(f"📋 POST /text {{text}} -> LLM+TTS")
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("STEP_API_KEY:", "SET ✅" if STEP_API_KEY else "⚠️ MISSING")
    asyncio.run(main())
