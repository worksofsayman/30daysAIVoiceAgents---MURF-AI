from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/agent", methods=["POST"])
def agent():
    user_input = request.json.get("message", "")
    # Simple AI logic (you can replace with LLM API later)
    response = f"I heard you say: {user_input}. I'm your AI voice agent!"
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
