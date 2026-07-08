"""
actions/google_maps.py — Generacion segura de rutas y mapas en Google Maps.
"""
from __future__ import annotations
import urllib.parse
import webbrowser
from typing import Any

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[google_maps] {msg}")
    except Exception:
        pass

def google_maps(parameters: dict, player=None, speak=None) -> str:
    """
    Shows navigation routes and interactive maps in Google Maps.
    """
    origin = parameters.get("origin", "").strip()
    destination = parameters.get("destination", "").strip()
    mode = parameters.get("mode", "driving").lower().strip() # driving, walking, bicycling, transit

    if not destination:
        # Si no hay destino, mostrar busqueda general en el mapa
        if origin:
            q_encoded = urllib.parse.quote(origin)
            maps_url = f"https://www.google.com/maps/search/?api=1&query={q_encoded}"
            log(f"Abriendo busqueda de ubicacion para '{origin}'...")
            webbrowser.open(maps_url)
            return f"Abriendo mapa buscando la ubicacion '{origin}'."
        else:
            # Mapa general
            webbrowser.open("https://www.google.com/maps")
            return "Abriendo Google Maps."

    # Si hay destino, generar ruta
    orig_encoded = urllib.parse.quote(origin) if origin else ""
    dest_encoded = urllib.parse.quote(destination)
    
    # Validacion del modo de viaje
    if mode not in ["driving", "walking", "bicycling", "transit"]:
        mode = "driving"

    # Construir URL segura oficial de Google Maps
    # Usando el API oficial de redireccionamiento de Google Maps
    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={dest_encoded}&travelmode={mode}"
    if orig_encoded:
        maps_url += f"&origin={orig_encoded}"

    log(f"Abriendo ruta hacia '{destination}' modo '{mode}'...")
    webbrowser.open(maps_url)
    
    route_desc = f"Abriendo Google Maps con la ruta hacia '{destination}'"
    if origin:
        route_desc += f" partiendo de '{origin}'"
    route_desc += f" en modo '{mode}'."
    
    return route_desc
