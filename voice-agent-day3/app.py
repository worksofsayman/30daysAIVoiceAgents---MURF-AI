from flask import Flask, request, jsonify, render_template, send_file
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Text is required"}), 400

    # Generate TTS audio
    tts = gTTS(text)
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join("static", filename)
    tts.save(filepath)

    return jsonify({"audio_url": f"/static/{filename}"})


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(debug=True)
