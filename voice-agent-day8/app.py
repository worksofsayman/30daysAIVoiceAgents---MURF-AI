from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # load .env file if exists

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # get your API key from environment

# Gemini API endpoint (using your project & location)
PROJECT_ID = "day8-murf-ai"
LOCATION = "us-central1"
GEMINI_API_URL = (
    f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/"
    f"{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/text-bison@001:predict"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/llm/query', methods=['POST'])
def llm_query():
    try:
        data = request.get_json(force=True)
        if not data or 'text' not in data:
            return jsonify({"error": "Missing 'text' in request body"}), 400

        user_input = data['text']

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY
        }

        payload = {
            "instances": [{"content": user_input}],
            "parameters": {"temperature": 0.7, "maxOutputTokens": 256}
        }

        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)

        print("Gemini API status:", response.status_code)
        print("Gemini API response:", response.text)

        if response.status_code != 200:
            return jsonify({
                "error": "Failed to get response from Gemini API",
                "details": response.text,
                "status_code": response.status_code
            }), 500

        response_json = response.json()
        predictions = response_json.get("predictions", [])
        generated_text = ""
        if predictions and isinstance(predictions, list):
            generated_text = predictions[0].get("content", "")

        return jsonify({"response": generated_text})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
