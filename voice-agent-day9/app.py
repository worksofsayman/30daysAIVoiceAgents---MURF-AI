import os
import re
import time
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

def mock_transcribe_audio(audio_file):
    # Mock transcription for free-tier or testing
    return "Hello, this is a mocked transcription."

def query_llm(prompt):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    for attempt in range(3):
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
        if resp.status_code == 429:
            wait = 2 ** attempt
            print(f"LLM Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
            continue
        if resp.status_code == 401:
            raise Exception("Unauthorized: Check your OpenAI API key.")
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    raise Exception("Failed LLM request after retries due to rate limiting")

def split_text(text, max_chars=3000):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks, current = [], ""
    for sent in sentences:
        if len(current) + len(sent) + 1 <= max_chars:
            current += sent + " "
        else:
            if current:
                chunks.append(current.strip())
            current = sent + " "
    if current:
        chunks.append(current.strip())
    return chunks

def generate_murf_audio(text_chunk):
    url = "https://api.murf.ai/v1/speech/generate"
    headers = {
        "Authorization": f"Bearer {MURF_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text_chunk,
        "voice": "en_us_murf_male_001",
        "speed": 1.0
    }
    for attempt in range(3):
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code == 429:
            wait = 2 ** attempt
            print(f"Murf Rate limited. Retrying in {wait}s...")
            time.sleep(wait)
            continue
        if resp.status_code == 401:
            raise Exception("Unauthorized: Check your Murf API key.")
        resp.raise_for_status()
        return resp.json().get("audioUrl")
    raise Exception("Failed Murf request after retries due to rate limiting")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/llm/query', methods=['POST'])
def llm_query():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({"error": "No audio file provided"}), 400

    try:
        # MOCKED transcription — replace with actual when you get access
        transcription = mock_transcribe_audio(audio_file)

        if not transcription:
            return jsonify({"error": "Transcription failed"}), 500

        llm_response = query_llm(transcription)
        chunks = split_text(llm_response, max_chars=3000)
        murf_audio_url = generate_murf_audio(chunks[0])

        return jsonify({
            "transcription": transcription,
            "llmResponse": llm_response,
            "audioFileUrl": murf_audio_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on port 3000 to avoid default 5000 conflicts
    app.run(debug=True, port=3000)
