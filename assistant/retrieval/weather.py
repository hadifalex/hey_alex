import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# global variable for temporary storage
LAST_GEOCODE_RESULTS = []


def geocode(location: str, max_results: int = 5):
    params = {"name": location, "count": max_results}
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    data = r.json()

    if not data.get("results"):
        return None

    return data["results"]



def get_weather_from_coords(lat: float, lon: float, name: str):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"
    }

    r = requests.get(WEATHER_URL, params=params, timeout=10)
    data = r.json()

    weather = data.get("current_weather", {})
    temp = weather.get("temperature")
    wind = weather.get("windspeed")

    return {
        "location": name,
        "temp": temp,
        "wind": wind,
    }


def format_options(options):
    lines = []
    for i, opt in enumerate(options, start=1):
        name = opt["name"]
        country = opt.get("country", "")
        admin = opt.get("admin1", "")
        lines.append(f"{i}) {name}, {admin} {country}".strip())
    return "\n".join(lines)
