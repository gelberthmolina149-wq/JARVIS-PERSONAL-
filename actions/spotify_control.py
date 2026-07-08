"""
actions/spotify_control.py — Control de Spotify via Spotipy SDK y fallback seguro a browser.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import webbrowser

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    spotipy = None
    SpotifyOAuth = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[spotify_control] {msg}")
    except Exception:
        pass

def get_spotify_client() -> spotipy.Spotify | None:
    """Intenta cargar credenciales de Spotify y retornar el cliente autenticado."""
    if not spotipy or not SpotifyOAuth:
        return None
        
    config_path = Path("config/api_keys.json")
    if not config_path.exists():
        return None
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            creds = cfg.get("spotify_credentials", {})
            
        client_id = creds.get("client_id")
        client_secret = creds.get("client_secret")
        redirect_uri = creds.get("redirect_uri", "http://localhost:8888/callback")
        scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing"
        
        if not client_id or not client_secret:
            return None
            
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            open_browser=False
        ))
        return sp
    except Exception as e:
        log(f"Error al inicializar Spotipy: {e}")
        return None

def spotify_control(parameters: dict, player=None, speak=None) -> str:
    """
    Control total de Spotify: reproducir, pausar, siguiente, anterior, volumen, etc.
    """
    action = parameters.get("action", "").lower().strip()
    query = parameters.get("query", "").strip()
    sp_type = parameters.get("type", "track").lower().strip()
    value = parameters.get("value", "").strip()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    log(f"Ejecutando accion '{action}'")

    sp = get_spotify_client()

    # Si no hay cliente autenticado, las acciones interactivas caen a fallback de browser
    if not sp:
        log("Spotipy no configurado. Usando modo de reproduccion web fallback.")
        if action == "play" and query:
            q_encoded = urllib.parse.quote(query) if "urllib.parse" in globals() else query
            webbrowser.open(f"https://open.spotify.com/search/{q_encoded}")
            return f"Buscando '{query}' en Spotify Web (Spotipy no configurado)."
        elif action == "play" and not query:
            webbrowser.open("https://open.spotify.com/")
            return "Abriendo Spotify Web."
        else:
            return f"Error: La accion '{action}' requiere configurar credenciales en config/api_keys.json."

    try:
        if action == "play":
            if query:
                # Buscar cancion / playlist / artista
                results = sp.search(q=query, limit=1, type=sp_type)
                items = results.get(f"{sp_type}s", {}).get("items", [])
                if not items:
                    return f"No se encontro ningun {sp_type} coincidente con '{query}'."
                uri = items[0]["uri"]
                name = items[0]["name"]
                
                if sp_type == "track":
                    sp.start_playback(uris=[uri])
                else:
                    sp.start_playback(context_uri=uri)
                return f"Reproduciendo {sp_type} '{name}' en tu dispositivo activo."
            else:
                sp.start_playback()
                return "Reproduccion reanudada."

        elif action == "pause":
            sp.pause_playback()
            return "Reproduccion pausada."

        elif action == "resume":
            sp.start_playback()
            return "Reproduccion reanudada."

        elif action == "next":
            sp.next_track()
            return "Siguiente pista."

        elif action == "previous":
            sp.previous_track()
            return "Pista anterior."

        elif action == "volume":
            if not value:
                return "Error: Se requiere 'value' para ajustar el volumen."
            try:
                vol = int(value)
                # Validacion de seguridad de rango
                if vol < 0 or vol > 100:
                    return "Error: El volumen debe estar en el rango de 0 a 100."
                sp.volume(vol)
                return f"Volumen establecido en {vol}%."
            except ValueError:
                return "Error: El volumen debe ser un valor numerico."

        elif action == "shuffle":
            state = value.lower() in ["true", "1", "yes", "on"]
            sp.shuffle(state)
            return f"Modo aleatorio: {'Activado' if state else 'Desactivado'}."

        elif action == "repeat":
            # repeat state: 'track', 'context', or 'off'
            state = value.lower() if value.lower() in ["track", "context", "off"] else "off"
            sp.repeat(state)
            return f"Modo repeticion establecido en '{state}'."

        elif action == "current":
            curr = sp.currently_playing()
            if not curr or not curr.get("item"):
                return "No hay musica sonando actualmente."
            track_name = curr["item"]["name"]
            artist_name = curr["item"]["artists"][0]["name"]
            return f"Sonando ahora: '{track_name}' de '{artist_name}'."

        elif action == "devices":
            devs = sp.devices()
            devices_list = devs.get("devices", [])
            if not devices_list:
                return "No se encontraron dispositivos Spotify activos conectados."
            res = "Dispositivos disponibles:\n"
            for d in devices_list:
                res += f"  - {d['name']} ({'Activo' if d['is_active'] else 'Inactivo'})\n"
            return res.strip()

        else:
            return f"Error: Accion '{action}' no soportada por el controlador nativo de Spotify."

    except Exception as e:
        return f"Error al interactuar con la API de Spotify: {e}"
