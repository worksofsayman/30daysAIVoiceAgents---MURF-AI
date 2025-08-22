from flask import Flask, render_template, request, Response
import time

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream", methods=["POST"])
def stream_response():
    user_input = request.json.get("transcript", "")
    fake_reply = f"You said: {user_input}. This is a simulated streaming LLM reply!"

    def generate():
        for word in fake_reply.split():
            yield word + " "
            time.sleep(0.2)  # delay to simulate streaming

    return Response(generate(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True)
