"""
actions/weather_report.py — Reporte del clima en tiempo real.

Usa Open-Meteo (API gratuita, sin key) + Nominatim para geocodificación.
Fallback a wttr.in si Open-Meteo falla.
"""
from __future__ import annotations
import json
from typing import Any

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

# Códigos WMO de condición climática → descripción en español
_WMO_CODES: dict[int, str] = {
    0:  "despejado",
    1:  "mayormente despejado",
    2:  "parcialmente nublado",
    3:  "nublado",
    45: "con niebla",
    48: "con niebla helada",
    51: "llovizna ligera",
    53: "llovizna moderada",
    55: "llovizna intensa",
    61: "lluvia ligera",
    63: "lluvia moderada",
    65: "lluvia intensa",
    71: "nieve ligera",
    73: "nieve moderada",
    75: "nieve intensa",
    77: "granizo",
    80: "chubascos ligeros",
    81: "chubascos moderados",
    82: "chubascos intensos",
    85: "nevada ligera",
    86: "nevada intensa",
    95: "tormenta eléctrica",
    96: "tormenta con granizo",
    99: "tormenta severa con granizo",
}

# Ciudades frecuentes con coordenadas pre-cargadas para evitar geocodificación
_CITY_COORDS: dict[str, tuple[float, float]] = {
    "lima":            (-12.0464, -77.0428),
    "buenos aires":    (-34.6037, -58.3816),
    "bogota":          (4.7110,   -74.0721),
    "bogotá":          (4.7110,   -74.0721),
    "santiago":        (-33.4489, -70.6693),
    "mexico":          (19.4326,  -99.1332),
    "ciudad de mexico":(19.4326,  -99.1332),
    "madrid":          (40.4168,  -3.7038),
    "barcelona":       (41.3851,  2.1734),
    "miami":           (25.7617,  -80.1918),
    "new york":        (40.7128,  -74.0060),
    "nueva york":      (40.7128,  -74.0060),
    "london":          (51.5074,  -0.1278),
    "paris":           (48.8566,  2.3522),
    "caracas":         (10.4806,  -66.9036),
    "quito":           (-0.1807,  -78.4678),
    "montevideo":      (-34.9011, -56.1645),
    "asuncion":        (-25.2867, -57.6470),
    "asunción":        (-25.2867, -57.6470),
    "la paz":          (-16.5000, -68.1193),
    "guadalajara":     (20.6597,  -103.3496),
    "monterrey":       (25.6866,  -100.3161),
}


def _geocode(city: str) -> tuple[float, float, str] | None:
    """Geocodifica una ciudad. Retorna (lat, lon, nombre_display) o None."""
    key = city.lower().strip()

    # Cache rápido
    if key in _CITY_COORDS:
        lat, lon = _CITY_COORDS[key]
        return lat, lon, city.title()

    # Nominatim (OpenStreetMap, gratuito)
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "json", "limit": 1}
        headers = {"User-Agent": "JARVIS-AI/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"].split(",")[0]
    except Exception:
        pass
    return None


def _fetch_open_meteo(lat: float, lon: float) -> dict | None:
    """Consulta Open-Meteo y retorna datos procesados."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude":  lat,
            "longitude": lon,
            "current":   [
                "temperature_2m", "apparent_temperature", "relative_humidity_2m",
                "wind_speed_10m", "weathercode", "precipitation"
            ],
            "timezone": "auto",
            "wind_speed_unit": "kmh",
        }
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        c = data.get("current", {})
        return {
            "temp":       round(c.get("temperature_2m", 0), 1),
            "feels_like": round(c.get("apparent_temperature", 0), 1),
            "humidity":   c.get("relative_humidity_2m", 0),
            "wind":       round(c.get("wind_speed_10m", 0), 1),
            "code":       c.get("weathercode", 0),
            "rain":       c.get("precipitation", 0),
        }
    except Exception:
        return None


def _fetch_wttr(city: str) -> str | None:
    """Fallback a wttr.in en formato JSON."""
    try:
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"
        resp = requests.get(url, timeout=6)
        data = resp.json()
        cc = data["current_condition"][0]
        temp    = cc.get("temp_C", "?")
        feels   = cc.get("FeelsLikeC", "?")
        humidity = cc.get("humidity", "?")
        wind    = cc.get("windspeedKmph", "?")
        desc    = cc.get("weatherDesc", [{}])[0].get("value", "")
        return (
            f"En {city}: {temp}°C (sensación {feels}°C), "
            f"{desc.lower()}, humedad {humidity}%, viento {wind} km/h."
        )
    except Exception:
        return None


def weather_action(parameters: dict, player: Any = None, speak=None) -> str:
    """
    Obtiene el reporte del clima para una ciudad.

    Args:
        parameters: dict con 'city' (str).
        player: JarvisUI (para write_log).
        speak: función TTS (opcional).

    Returns:
        Reporte en lenguaje natural para que Gemini lo verbalice.
    """
    if not _HAS_REQUESTS:
        return "El módulo 'requests' no está instalado. Instálalo con: pip install requests"

    city: str = parameters.get("city", "Lima").strip()
    if not city:
        city = "Lima"

    def log(msg: str):
        if player:
            try:
                player.write_log(msg)
            except Exception:
                pass

    log(f"🌤 Consultando clima para: {city}")

    # Geocodificación
    geo = _geocode(city)
    if geo is None:
        # Fallback directo a wttr.in
        result = _fetch_wttr(city)
        if result:
            return result
        return f"No pude obtener el clima para '{city}'. Verifica el nombre de la ciudad."

    lat, lon, display_name = geo

    # Open-Meteo
    weather = _fetch_open_meteo(lat, lon)
    if weather:
        condition = _WMO_CODES.get(weather["code"], "condición desconocida")
        temp      = weather["temp"]
        feels     = weather["feels_like"]
        humidity  = weather["humidity"]
        wind      = weather["wind"]
        rain      = weather["rain"]

        parts = [
            f"En {display_name} el clima está {condition}.",
            f"Temperatura {temp}°C, sensación térmica {feels}°C.",
            f"Humedad {humidity}%,",
            f"viento a {wind} km/h.",
        ]
        if rain and rain > 0:
            parts.append(f"Hay {rain} mm de precipitación.")

        summary = " ".join(parts)
        log(f"☁ {summary}")
        return summary

    # Fallback a wttr.in
    result = _fetch_wttr(city)
    if result:
        log(f"☁ {result}")
        return result

    return f"No pude obtener información del clima para {city} en este momento."
