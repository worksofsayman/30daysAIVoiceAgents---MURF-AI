from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__)
app = Flask(__name__, static_folder=".", static_url_path="")

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")
# ---------------------- CORS ----------------------
@app.after_request
def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.route("/health", methods=["GET"])
def health():
    return "ok", 200


# ---------------- Persona Stylizers ----------------
def quick_answer(text: str) -> str:
    """
    Tiny rule-based fallback so we don't need external APIs.
    Produces a short, neutral answer to wrap with persona style.
    """
    t = (text or "").strip().lower()
    if not t:
        return "I didn't catch that. Could you repeat?"

    greetings = ("hi", "hello", "hey", "yo", "hola")
    if any(g in t.split() for g in greetings):
        return "Hello! Ask me anything and I'll assist."

    if t.endswith("?"):
        if "how" in t:
            return "Here are the steps: define the goal, outline steps, execute, then iterate."
        if "what" in t:
            return "In short: it depends on context—can you narrow it down?"
        if "why" in t:
            return "Because it optimizes outcomes under given constraints."
        if "when" in t:
            return "When prerequisites are ready and stakeholders aligned."
        if "where" in t:
            return "Where it best fits your resources and needs."

    if any(w in t for w in ("help", "guide", "steps", "explain", "tutorial")):
        return "Start simple, test often, gather feedback, and refine."

    if any(w in t for w in ("name", "who are you")):
        return "I'm your persona-driven voice agent."

    return "Got it. Here's a concise take tailored to your request."


def stylize_pirate(text: str) -> str:
    repl = f"Arrr! {quick_answer(text)} Yo-ho! Stay the course, matey."
    return repl


def stylize_cowboy(text: str) -> str:
    return f"Howdy, partner. {quick_answer(text)} Saddle up—I've got your back."


def stylize_robot(text: str) -> str:
    return f"[SYSTEM]: {quick_answer(text)} [CONFIDENCE: HIGH]"


def stylize_detective(text: str) -> str:
    return f"Case notes updated. Clues indicate: {quick_answer(text)} What's our next lead?"


def stylize_professor(text: str) -> str:
    return f"Accordingly, let's break it down: {quick_answer(text)} We can explore nuances further."


def stylize_custom(text: str, desc: str) -> str:
    desc = (desc or "custom persona").strip()
    return f"As a {desc}, {quick_answer(text)}"


PERSONAS = {
    "Pirate": stylize_pirate,
    "Cowboy": stylize_cowboy,
    "Robot": stylize_robot,
    "Detective": stylize_detective,
    "Professor": stylize_professor,
}


# --------------------- API ------------------------
@app.route("/respond", methods=["POST", "OPTIONS"])
def respond():
    if request.method == "OPTIONS":
        return "", 204

    try:
        data = request.get_json(force=True) or {}
    except Exception:
        return jsonify(error="Invalid JSON"), 400

    text = (data.get("text") or "").strip()
    persona = (data.get("persona") or "Robot").strip()
    custom_desc = (data.get("customPersona") or "").strip()

    if not text:
        return jsonify(error="Field 'text' is required"), 400

    # Choose stylizer
    if persona == "Custom":
        response_text = stylize_custom(text, custom_desc)
        persona_used = f"Custom ({custom_desc or 'unspecified'})"
    else:
        stylizer = PERSONAS.get(persona, stylize_robot)
        response_text = stylizer(text)
        persona_used = persona if persona in PERSONAS else "Robot"

    return jsonify(
        persona=persona_used,
        response=response_text,
        timestamp=datetime.utcnow().isoformat() + "Z",
    ), 200


# ------------------- Entry Point -------------------
if __name__ == "__main__":
    # Run: python app.py
    # Then open index.html (frontend) which calls http://127.0.0.1:5000
    app.run(host="127.0.0.1", port=5000, debug=False)
