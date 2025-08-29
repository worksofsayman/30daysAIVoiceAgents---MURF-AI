from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# ---------- Weather Function ----------
def get_weather(city):
    try:
        # Geocoding to lat/lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url, timeout=8).json()

        if not geo_response.get("results"):
            return {"error": f"City '{city}' not found"}

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        # Weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url, timeout=8).json()

        if "current_weather" not in weather_response:
            return {"error": "Weather data not available"}

        current = weather_response["current_weather"]
        return {
            "city": city.title(),
            "temperature": current["temperature"],
            "windspeed": current["windspeed"],
            "weathercode": current["weathercode"],
        }

    except Exception as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}


# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    query = data.get("query", "").lower().strip()

    if query.startswith("weather"):
        # Extract city name
        if ":" in query:
            city = query.split(":", 1)[1].strip()
        else:
            city = query.replace("weather", "").strip()

        if not city:
            return jsonify({"error": "No city provided"}), 400

        result = get_weather(city)
        return jsonify(result), 200

    return jsonify({"response": "❓ Special skill not recognized"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
