import math
import requests
from .config import CITY_COORDINATES


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=2)
        if r.status_code != 200: return None
        return r.json()
    except Exception:
        return None


def get_nearest_city_name(lat, lng):
    closest_city = "Detected Location"
    min_dist = float('inf')
    for city, (c_lat, c_lng) in CITY_COORDINATES.items():
        dist = math.sqrt((lat - c_lat)**2 + (lng - c_lng)**2)
        if dist < min_dist:
            min_dist = dist
            closest_city = city
    if min_dist < 0.5: return closest_city
    return "GPS Location"


def get_weather_health_analysis(lat, lng):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=uv_index_max&timezone=auto"
        response = requests.get(url, timeout=3)
        data = response.json()
        current = data.get("current", {})
        daily = data.get("daily", {})
        return {
            "temp": current.get("temperature_2m", 0),
            "humidity": current.get("relative_humidity_2m", 0),
            "uv": daily.get("uv_index_max", [0])[0] if daily.get("uv_index_max") else 0
        }
    except Exception:
        return None
