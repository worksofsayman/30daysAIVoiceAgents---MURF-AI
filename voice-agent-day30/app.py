from flask import Flask, render_template_string, request, jsonify
import datetime as dt
import wikipedia, pyjokes, numexpr

app = Flask(__name__)

@app.route("/")
def index():
    with open("templates/index.html") as f:
        return render_template_string(f.read())
    
@app.route("/api/agent", methods=["POST"])
def agent():
    data = request.json
    query = data.get("message", "").lower()
    reply = "Sorry, I didn’t get that."

    try:
        if "time" in query:
            reply = f"The time is {dt.datetime.now().strftime('%H:%M:%S')}."
        elif "date" in query:
            reply = f"Today is {dt.datetime.now().strftime('%A, %B %d, %Y')}."
        elif "joke" in query:
            reply = pyjokes.get_joke()
        elif "calculate" in query:
            expr = query.replace("calculate", "")
            reply = str(numexpr.evaluate(expr))
        else:
            reply = wikipedia.summary(query, sentences=2)
    except Exception as e:
        reply = f"I couldn’t find an answer: {e}"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
