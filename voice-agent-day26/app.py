from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

NEWS_API_KEY = "your_newsapi_key"
WEATHER_API_KEY = "85b84653b9e28ceef13a0d5e4c8dae27"

# ---------------- Geocode city for OpenWeatherMap ----------------
def geocode_city(city):
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        r = requests.get(url, timeout=5).json()
        if r.get("results"):
            # Use city name and exact country to improve accuracy
            return r["results"][0]["name"]
    except:
        return None
    return None

# ---------------- Multi-skill handler ----------------
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    query = data.get("query", "").lower()

    # ---------- Weather ----------
    if "weather" in query:
        city = query.replace("weather", "").replace(":", "").strip()
        if not city:
            return jsonify({"error": "Please provide a city name, e.g., 'weather: Mumbai'."})

        city_name = geocode_city(city) or city
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("main"):
            return jsonify({
                "city": city_name,
                "temperature": res["main"]["temp"],
                "windspeed": res["wind"]["speed"]
            })
        else:
            return jsonify({"error": f"Couldn't fetch weather for {city_name}. Check city spelling."})

    # ---------- News ----------
    elif "news" in query:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        articles = res.get("articles", [])[:3]
        if articles:
            return jsonify({"news": [a["title"] for a in articles]})
        else:
            return jsonify({"error": "Couldn't fetch news right now."})

    # ---------- Joke ----------
    elif "joke" in query:
        res = requests.get("https://official-joke-api.appspot.com/random_joke").json()
        return jsonify({"joke": f"{res['setup']} ... {res['punchline']}"})

    # ---------- General fallback ----------
    else:
        return jsonify({"response": "I can provide weather, news, jokes, or general info. Try 'weather: Delhi' or 'news'."})

# ---------- Root ----------
@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
