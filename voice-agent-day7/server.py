import os
import time
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

if not ASSEMBLYAI_API_KEY or not MURF_API_KEY:
    raise RuntimeError("Set ASSEMBLYAI_API_KEY and MURF_API_KEY in environment.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSEMBLY_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
ASSEMBLY_TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"
MURF_TTS_URL = "https://api.murf.ai/v1/speech/generate"

async def upload_to_assemblyai(audio_bytes: bytes) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY}
    async with httpx.AsyncClient() as client:
        res = await client.post(ASSEMBLY_UPLOAD_URL, headers=headers, content=audio_bytes)
        res.raise_for_status()
        return res.json()["upload_url"]

async def transcribe_audio(audio_url: str, timeout=60) -> str:
    headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(ASSEMBLY_TRANSCRIPT_URL, headers=headers, json={"audio_url": audio_url})
        resp.raise_for_status()
        transcript_id = resp.json()["id"]

        start = time.time()
        while True:
            status_resp = await client.get(f"{ASSEMBLY_TRANSCRIPT_URL}/{transcript_id}", headers=headers)
            status_resp.raise_for_status()
            data = status_resp.json()

            if data["status"] == "completed":
                return data["text"]
            if data["status"] == "error":
                raise RuntimeError(data.get("error", "Unknown transcription error"))
            if time.time() - start > timeout:
                raise TimeoutError("Transcription timed out.")
            await asyncio.sleep(1)

async def generate_murf_voice(text: str, voice_id: str = "en-US-natalie") -> str:
    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "voiceId": voice_id,
        "text": text,
        "format": "MP3"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(MURF_TTS_URL, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        if "audioFile" not in data:
            raise RuntimeError("Murf API did not return audio file URL.")
        return data["audioFile"]

@app.post("/tts/echo")
async def tts_echo(audio: UploadFile = File(...), voice_id: str = "en-US-natalie"):
    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(400, "Empty audio file.")

        audio_url = await upload_to_assemblyai(audio_bytes)
        text = await transcribe_audio(audio_url)
        murf_audio_url = await generate_murf_voice(text, voice_id)

        return JSONResponse({
            "transcript": text,
            "murf_audio_url": murf_audio_url
        })

    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok"}
