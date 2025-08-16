import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import base64
from openai import OpenAI

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory chat history store
chat_history_store = {}

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY env variable not set")

client = OpenAI(api_key=openai_api_key)

# Dummy STT function
async def speech_to_text(audio_bytes: bytes) -> str:
    # Replace with real STT if needed
    return "hello from user"

# Query LLM with new OpenAI API
async def query_llm(messages):
    # messages is list of dicts with 'role' and 'content'
    openai_messages = [{"role": m["role"], "content": m["text"]} for m in messages]

    response = await client.chat.completions.acreate(
        model="gpt-4o-mini",
        messages=openai_messages,
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message.content

# Dummy TTS function
async def text_to_speech(text: str) -> bytes:
    # Replace with real TTS
    return b"RIFF$\x00\x00\x00WAVEfmt "

@app.post("/agent/chat/{session_id}")
async def chat(session_id: str, audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    user_text = await speech_to_text(audio_bytes)

    if session_id not in chat_history_store:
        chat_history_store[session_id] = []

    chat_history_store[session_id].append({"role": "user", "text": user_text})

    messages = chat_history_store[session_id]
    assistant_text = await query_llm(messages)

    chat_history_store[session_id].append({"role": "assistant", "text": assistant_text})

    audio_response = await text_to_speech(assistant_text)

    audio_b64 = base64.b64encode(audio_response).decode("utf-8")

    return JSONResponse({
        "transcript": user_text,
        "response": assistant_text,
        "audio": audio_b64
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
