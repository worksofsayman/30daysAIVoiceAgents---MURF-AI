from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
app = FastAPI()

MURF_API_KEY = os.getenv("MURF_API_KEY")

class TextInput(BaseModel):
    text: str

@app.post("/generate-audio")
async def generate_audio(input: TextInput):
    if not MURF_API_KEY:
        raise HTTPException(status_code=500, detail="Murf API key is missing")

    headers = {
        "Authorization": f"Bearer {MURF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "voice": "en-US-Wavenet-D",  # example voice
        "text": input.text,
        "speed": 1.0,
        "pitch": 1.0
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://api.murf.ai/v1/speech/generate", json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

    data = response.json()
    audio_url = data.get("audio_url")
    
    if not audio_url:
        raise HTTPException(status_code=500, detail="No audio_url found in response")

    return {"audio_url": audio_url}
