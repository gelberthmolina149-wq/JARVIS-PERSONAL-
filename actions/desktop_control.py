"""
actions/desktop_control.py — Control de fondos de pantalla y organizacion segura del escritorio.
"""
from __future__ import annotations
import os
import ctypes
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[desktop_control] {msg}")
    except Exception:
        pass

def is_safe_path(path: Path) -> bool:
    """Verifica acceso seguro para fondos de pantalla e interaccion con directorios."""
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

def set_wallpaper_win(image_path: str) -> bool:
    """Utiliza la API de Windows para establecer el fondo de pantalla de forma nativa."""
    try:
        # SPI_SETDESKWALLPAPER = 20
        # SPIF_UPDATEINIFILE = 1, SPIF_SENDCHANGE = 2
        result = ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        return bool(result)
    except Exception as e:
        print(f"Error calling SystemParametersInfoW: {e}")
        return False

def desktop_control(parameters: dict, player=None, speak=None) -> str:
    """
    Controls the desktop: wallpaper, wallpaper_url, organize, clean, list, stats.
    """
    action = parameters.get("action", "").lower()
    path_str = parameters.get("path", "").strip()
    url = parameters.get("url", "").strip()
    search_name = parameters.get("search_name", "").strip()
    search_path_str = parameters.get("search_path", "desktop").lower().strip()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    home = Path.home()
    desktop_path = home / "Desktop"

    # Validacion de busqueda rapida en directorios comunes
    if action == "task" or search_name:
        # Buscar el archivo en el directorio configurado
        dir_to_search = desktop_path
        if search_path_str == "downloads":
            dir_to_search = home / "Downloads"
        elif search_path_str == "documents":
            dir_to_search = home / "Documents"
        elif search_path_str == "pictures":
            dir_to_search = home / "Pictures"
        elif search_path_str == "home":
            dir_to_search = home

        log(f"Buscando '{search_name}' en '{dir_to_search}'")
        
        matches = []
        try:
            for item in dir_to_search.iterdir():
                if search_name.lower() in item.name.lower():
                    matches.append(item)
            if matches:
                resolved_match = matches[0].resolve()
                return f"Archivo encontrado de forma automatica: '{resolved_match}'."
            else:
                return f"No se encontro ningun archivo que coincida con '{search_name}' en '{dir_to_search}'."
        except Exception as e:
            return f"Error durante la busqueda automatica: {e}"

    if action == "wallpaper":
        if not path_str:
            return "Error: Se requiere el parametro 'path' con la ruta de la imagen local."
        
        image_path = Path(path_str).resolve()
        if not image_path.exists():
            return f"Error: El archivo de imagen '{image_path}' no existe."
        if not is_safe_path(image_path):
            return f"Error de seguridad: Acceso denegado al archivo '{image_path}'."

        if set_wallpaper_win(str(image_path)):
            return f"Fondo de pantalla cambiado exitosamente al archivo local '{image_path}'."
        else:
            return "Error al intentar cambiar el fondo de pantalla mediante el sistema operativo."

    elif action == "wallpaper_url":
        if not url:
            return "Error: Se requiere el parametro 'url' con la imagen a descargar."

        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return f"Error de seguridad: Protocolo '{parsed.scheme}' no permitido. Solo se admite http o https."

        # Guardar temporalmente en el directorio de imagenes del usuario
        pictures_dir = home / "Pictures"
        pictures_dir.mkdir(parents=True, exist_ok=True)
        temp_img_path = pictures_dir / "jarvis_wallpaper_temp.jpg"

        try:
            log(f"Descargando imagen desde {url}...")
            # Forzar cabeceras basicas para evitar bloqueos HTTP
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                with open(temp_img_path, "wb") as out_file:
                    out_file.write(response.read())

            if set_wallpaper_win(str(temp_img_path)):
                return f"Fondo de pantalla descargado y establecido correctamente desde {url}."
            else:
                return "Error al intentar cambiar el fondo de pantalla despues de descargar la imagen."
        except Exception as e:
            return f"Error al descargar o aplicar fondo de pantalla: {e}"

    elif action == "list":
        try:
            items = os.listdir(desktop_path)
            files = [i for i in items if os.path.isfile(desktop_path / i) and not i.lower() in ["desktop.ini"]]
            folders = [i for i in items if os.path.isdir(desktop_path / i)]
            
            res = f"Elementos en el Escritorio ({desktop_path}):\n"
            if folders:
                res += "  Carpetas:\n" + "\n".join(f"    {fold}" for fold in folders) + "\n"
            if files:
                res += "  Archivos:\n" + "\n".join(f"    {f}" for f in files) + "\n"
            if not files and not folders:
                res += "  (Vacio)"
            return res
        except Exception as e:
            return f"Error al listar elementos del Escritorio: {e}"

    elif action == "stats":
        try:
            items = os.listdir(desktop_path)
            total_size = 0
            file_count = 0
            folder_count = 0
            
            for item in items:
                item_path = desktop_path / item
                if item_path.is_file():
                    if item.lower() != "desktop.ini":
                        file_count += 1
                        total_size += item_path.stat().st_size
                elif item_path.is_dir():
                    folder_count += 1
            
            return (
                f"Estadisticas del Escritorio:\n"
                f"  Ruta: {desktop_path}\n"
                f"  Archivos: {file_count}\n"
                f"  Carpetas: {folder_count}\n"
                f"  Tamano total de archivos: {total_size / (1024*1024):.2f} MB ({total_size} bytes)"
            )
        except Exception as e:
            return f"Error al calcular estadisticas: {e}"

    elif action in ["organize", "clean"]:
        # Se omitió por alcance según indicaciones del usuario, pero respondemos de forma elegante
        return f"La accion '{action}' esta temporalmente deshabilitada en la configuracion actual de JARVIS."

    else:
        return f"Error: Accion '{action}' no reconocida en desktop_control."
