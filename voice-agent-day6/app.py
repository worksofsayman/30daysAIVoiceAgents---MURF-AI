from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import assemblyai as aai

app = Flask(__name__)
CORS(app)

# Replace with your AssemblyAI API key
aai.settings.api_key = "da3a32e27e3d43e788b8a69240fbc36b"
transcriber = aai.Transcriber()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe/file', methods=['POST'])
def transcribe_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    audio_file = request.files['file']
    audio_bytes = audio_file.read()

    try:
        transcript = transcriber.transcribe(audio_bytes)
        return jsonify({'transcript': transcript.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
