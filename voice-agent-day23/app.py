from flask import Flask, render_template, request, jsonify, send_file
import openai
import os
import pyttsx3

openai.api_key = "YOUR_OPENAI_API_KEY"

app = Flask(__name__)
chat_history = []

# Text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_msg = data["message"]
    chat_history.append({"role": "user", "content": user_msg})

    # GPT API call
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_history
    )
    reply = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})

    # Save chat history
    with open("chat_history.txt", "a") as f:
        f.write(f"User: {user_msg}\nBot: {reply}\n\n")

    # Generate TTS audio
    audio_file = "static/reply.mp3"
    engine.save_to_file(reply, audio_file)
    engine.runAndWait()

    return jsonify({"reply": reply, "audio_url": f"/{audio_file}"})

if __name__ == "__main__":
    app.run(debug=True)
