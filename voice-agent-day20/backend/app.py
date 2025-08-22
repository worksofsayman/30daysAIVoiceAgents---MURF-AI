import asyncio
import base64
import json
import math
import struct
import wave
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from websockets.client import connect as ws_connect

# Murf credentials
MURF_API_KEY = ""  # leave blank to use mock mode
MURF_WS_URL = "wss://api.murf.ai/v1/speech/ws"
MURF_VOICE_ID = "en-US-amber"  # pick a valid voice ID from Murf docs

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str

class TTSResponse(BaseModel):
    audio_base64: str
    used_provider: str


# -------------------------
# Mock mode: simple sine WAV
# -------------------------
def generate_sine_wave_wav_base64(duration_sec=1.5, freq_hz=440.0, rate=16000):
    n_samples = int(duration_sec * rate)
    buf = BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(rate)
        for n in range(n_samples):
            t = n / rate
            # fade out to avoid click
            amplitude = int(
                32767 * 0.5 * (1.0 - (n / n_samples)) * math.sin(2 * math.pi * freq_hz * t)
            )
            wf.writeframes(struct.pack("<h", amplitude))
    raw = buf.getvalue()
    return base64.b64encode(raw).decode("utf-8")


# -------------------------
# Real Murf WebSocket call
# -------------------------
async def murf_tts_base64(text: str) -> str:
    url = f"{MURF_WS_URL}?api_key={MURF_API_KEY}"

    payload = {
        "event": "convert",
        "voiceId": MURF_VOICE_ID,
        "text": text,
        "format": "base64"
    }

    async with ws_connect(url, ping_interval=20) as ws:
        await ws.send(json.dumps(payload))

        audio_b64 = None
        async for message in ws:
            try:
                data = json.loads(message)
            except Exception:
                continue

            if data.get("event") == "audio" and "audio" in data:
                audio_b64 = data["audio"]
                break
            elif data.get("event") in {"error", "failed"}:
                raise HTTPException(status_code=502, detail=f"Murf error: {data}")

        if not audio_b64:
            raise HTTPException(status_code=502, detail="No audio received from Murf.")
        return audio_b64


@app.post("/api/tts", response_model=TTSResponse)
async def tts_endpoint(req: TTSRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    if not MURF_API_KEY:
        # mock mode
        audio_b64 = generate_sine_wave_wav_base64()
        return TTSResponse(audio_base64=audio_b64, used_provider="mock")

    # real Murf call
    audio_b64 = await murf_tts_base64(text)
    return TTSResponse(audio_base64=audio_b64, used_provider="murf")
