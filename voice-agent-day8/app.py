from flask import Flask, request, jsonify, send_from_directory
import requests
from flask_cors import CORS
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import os

app = Flask(__name__)
CORS(app)

# Path to your service account JSON key file
SERVICE_ACCOUNT_FILE = "path/to/your-service-account.json"

# Gemini API URL
GEMINI_API_URL = "https://gemini.googleapis.com/v1/models/text-bison-001:generateText"

# Scopes required for Gemini API
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

# Load credentials from service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/llm/query', methods=['POST'])
def llm_query():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    user_input = data['text']

    # Refresh token if needed
    credentials.refresh(Request())

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credentials.token}"
    }

    payload = {
        "prompt": {"text": user_input},
        "temperature": 0.7,
        "maxOutputTokens": 256
    }

    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({
            "error": "Failed to get response from Gemini API",
            "details": response.text,
            "status_code": response.status_code
        }), 500

    response_json = response.json()
    generated_text = response_json.get("candidates", [{}])[0].get("output", "")

    return jsonify({"response": generated_text})

if __name__ == "__main__":
    app.run(debug=True)
