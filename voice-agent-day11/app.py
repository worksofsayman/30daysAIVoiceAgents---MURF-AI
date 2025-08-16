from flask import Flask, request, jsonify, send_from_directory
import logging

app = Flask(__name__, static_folder="templates")
logging.basicConfig(level=logging.INFO)

# --- Mock AI API Calls ---
def speech_to_text(audio_file):
    if not audio_file:
        raise ValueError("No audio provided")
    return "Hello world"

def llm_call(text):
    if text.strip() == "":
        raise ValueError("Empty text")
    return f"You said: {text}"

def text_to_speech(text):
    if not text:
        raise ValueError("No text for TTS")
    return "BASE64_FAKE_AUDIO_DATA"

# Serve HTML UI
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# API route
@app.route("/process_audio", methods=["POST"])
def process_audio():
    try:
        # Step 1: STT
        try:
            audio_file = request.files.get("audio")
            text = speech_to_text(audio_file)
        except Exception as e:
            logging.error(f"STT Error: {e}")
            return jsonify({"error": "STT_FAILED"}), 500

        # Step 2: LLM
        try:
            ai_response = llm_call(text)
        except Exception as e:
            logging.error(f"LLM Error: {e}")
            return jsonify({"error": "LLM_FAILED"}), 500

        # Step 3: TTS
        try:
            audio_data = text_to_speech(ai_response)
        except Exception as e:
            logging.error(f"TTS Error: {e}")
            return jsonify({"error": "TTS_FAILED"}), 500

        return jsonify({"text": ai_response, "audio": audio_data})

    except Exception as e:
        logging.error(f"Unexpected Server Error: {e}")
        return jsonify({"error": "SERVER_ERROR"}), 500

if __name__ == "__main__":
    app.run(debug=True)
