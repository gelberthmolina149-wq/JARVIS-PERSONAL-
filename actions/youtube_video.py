"""
actions/youtube_video.py — Control de YouTube, busquedas, reproduccion y resúmenes seguros.
"""
from __future__ import annotations
import re
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[youtube_video] {msg}")
    except Exception:
        pass

def is_safe_path(path: Path) -> bool:
    try:
        resolved = path.resolve()
        system_roots = [
            Path("C:/Windows").resolve(),
            Path("C:/Program Files").resolve(),
            Path("C:/Program Files (x86)").resolve(),
            Path("C:/ProgramData").resolve(),
        ]
        for root in system_roots:
            if resolved == root or root in resolved.parents:
                return False
        return True
    except Exception:
        return False

def validate_youtube_url(url: str) -> bool:
    """Verifica si la URL es un dominio oficial de YouTube."""
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc.lower()
    if domain in ["youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be"]:
        return True
    return False

def extract_video_id(url: str) -> str | None:
    """Extrae el VideoID de una URL de YouTube."""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "youtube.com" in url:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        return params.get("v", [None])[0]
    return None

def youtube_video(parameters: dict, player=None, speak=None) -> str:
    """
    Controls YouTube: playing videos, summarizing content, getting video info, or showing trends.
    """
    action = parameters.get("action", "play").lower().strip()
    query = parameters.get("query", "").strip()
    url = parameters.get("url", "").strip()
    region = parameters.get("region", "US").upper().strip()
    save = parameters.get("save", False)

    log(f"Ejecutando accion '{action}'")

    if action == "play":
        if url:
            if not validate_youtube_url(url):
                return "Error de seguridad: La URL proporcionada no pertenece a un dominio de YouTube valido."
            webbrowser.open(url)
            return f"Abriendo video de YouTube directo: {url}."
        elif query:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(search_url)
            return f"Buscando '{query}' en YouTube."
        else:
            return "Error: Para reproducir en YouTube se requiere 'query' o 'url'."

    elif action == "summarize":
        if not url:
            return "Error: Se requiere el parametro 'url' del video de YouTube a resumir."
        if not validate_youtube_url(url):
            return "Error de seguridad: URL no autorizada para resumen."

        video_id = extract_video_id(url)
        if not video_id:
            return "Error: No se pudo extraer el ID del video desde la URL."

        if not YouTubeTranscriptApi:
            return "Error: El modulo 'youtube-transcript-api' no esta instalado en este sistema."

        try:
            log(f"Obteniendo transcripcion para el video '{video_id}'...")
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["es", "en"])
            text = " ".join([t["text"] for t in transcript])
            
            # Limitar longitud de transcripcion para evitar saturar el LLM
            summary_raw = f"Resumen del video ID {video_id}:\n\nTranscripcion extracto:\n{text[:1500]}..."
            
            if save:
                desktop_path = Path.home() / "Desktop" / f"resumen_youtube_{video_id}.txt"
                if is_safe_path(desktop_path):
                    with open(desktop_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    summary_raw += f"\n\nTranscripcion completa guardada en '{desktop_path}'."
                    
            return summary_raw
        except Exception as e:
            return f"Error al generar resumen del video: {e}"

    elif action == "get_info":
        if not url:
            return "Error: Se requiere el parametro 'url' para obtener informacion."
        if not validate_youtube_url(url):
            return "Error de seguridad: URL no autorizada."
        video_id = extract_video_id(url)
        return f"Informacion del video:\n  Video ID: {video_id or 'No detectado'}\n  Enlace: {url}"

    elif action == "trending":
        # Retorna el link a la pagina oficial de tendencias por region
        trend_url = f"https://www.youtube.com/feed/trending?bp=4gINGAEyBndpdGhvdXQ%3D"
        webbrowser.open(trend_url)
        return f"Abriendo seccion de tendencias de YouTube para la region '{region}'."

    else:
        return f"Error: Accion '{action}' no reconocida para youtube_video."
