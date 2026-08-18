import requests

def get_weather(lat: float, lon: float):
    """
    Fetches current weather for a point using Open-Meteo (free, no API key).
    Returns temperature, precipitation, and a simple risk flag for riding conditions.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,precipitation,weather_code,wind_speed_10m,is_day",
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})

        precipitation = current.get("precipitation", 0)
        wind_speed = current.get("wind_speed_10m", 0)
        weather_code = current.get("weather_code", 0)
        is_day = current.get("is_day", 1)

        # Simple risk flag for two-wheeler riders
        risky_conditions = []
        if precipitation > 0.5:
            risky_conditions.append("rain")
        if wind_speed > 30:
            risky_conditions.append("strong wind")
        if weather_code in [45, 48]:  # fog codes
            risky_conditions.append("fog")

        return {
            "temperature_c": current.get("temperature_2m"),
            "precipitation_mm": precipitation,
            "wind_speed_kmh": wind_speed,
            "is_night": is_day == 0,
            "risky_conditions": risky_conditions,
            "available": True,
        }
    except requests.RequestException:
        return {"available": False}