"""
actions/open_app.py — Abre cualquier aplicación en Windows.

Estrategias (en orden):
1. Mapa de aliases conocidos (Spotify, Chrome, WhatsApp, etc.)
2. os.startfile si es una ruta existente
3. subprocess con el nombre directo
4. Búsqueda en Program Files / AppData
5. Winget / Windows Store
6. Abrir como URL en el navegador (fallback final)
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# ── Mapa de aliases → comando o ruta ─────────────────────────────────────────
_APP_MAP: dict[str, str] = {
    # Navegadores
    "chrome":           "chrome.exe",
    "google chrome":    "chrome.exe",
    "firefox":          "firefox.exe",
    "edge":             "msedge.exe",
    "microsoft edge":   "msedge.exe",
    "brave":            "brave.exe",
    "opera":            "opera.exe",

    # Comunicación
    "whatsapp":         "WhatsApp.exe",
    "telegram":         "Telegram.exe",
    "discord":          "Discord.exe",
    "zoom":             "Zoom.exe",
    "teams":            "ms-teams:",
    "microsoft teams":  "ms-teams:",
    "slack":            "slack.exe",
    "skype":            "skype:",

    # Música / Video
    "spotify":          "spotify.exe",
    "vlc":              "vlc.exe",
    "youtube":          "https://www.youtube.com",
    "netflix":          "https://www.netflix.com",
    "twitch":           "https://www.twitch.tv",

    # Productividad
    "notepad":          "notepad.exe",
    "bloc de notas":    "notepad.exe",
    "word":             "winword.exe",
    "excel":            "excel.exe",
    "powerpoint":       "powerpnt.exe",
    "outlook":          "outlook.exe",
    "onenote":          "onenote.exe",
    "teams":            "teams.exe",
    "notion":           "Notion.exe",
    "obsidian":         "Obsidian.exe",

    # Desarrollo
    "vscode":           "code.exe",
    "vs code":          "code.exe",
    "visual studio code": "code.exe",
    "visual studio":    "devenv.exe",
    "terminal":         "wt.exe",
    "windows terminal": "wt.exe",
    "powershell":       "powershell.exe",
    "cmd":              "cmd.exe",
    "git bash":         "git-bash.exe",
    "cursor":           "cursor.exe",
    "pycharm":          "pycharm64.exe",
    "android studio":   "studio64.exe",
    "postman":          "Postman.exe",

    # Sistema
    "explorador":       "explorer.exe",
    "explorer":         "explorer.exe",
    "file explorer":    "explorer.exe",
    "configuracion":    "ms-settings:",
    "configuración":    "ms-settings:",
    "settings":         "ms-settings:",
    "panel de control": "control.exe",
    "control panel":    "control.exe",
    "administrador de tareas": "taskmgr.exe",
    "task manager":     "taskmgr.exe",
    "calculadora":      "calc.exe",
    "calculator":       "calc.exe",
    "paint":            "mspaint.exe",
    "wordpad":          "wordpad.exe",
    "recortes":         "SnippingTool.exe",
    "snipping tool":    "SnippingTool.exe",
    "camara":           "microsoft.windows.camera:",
    "cámara":           "microsoft.windows.camera:",
    "camera":           "microsoft.windows.camera:",

    # Juegos
    "steam":            "steam.exe",
    "epic games":       "EpicGamesLauncher.exe",
    "epic":             "EpicGamesLauncher.exe",
    "xbox":             "xbox:",
    "minecraft":        "Minecraft.exe",

    # Utilidades
    "7zip":             "7zFM.exe",
    "winrar":           "WinRAR.exe",
    "vlc":              "vlc.exe",
    "obs":              "obs64.exe",
    "obs studio":       "obs64.exe",
    "audacity":         "audacity.exe",
    "gimp":             "gimp-2.10.exe",
    "photoshop":        "Photoshop.exe",
    "premiere":         "Adobe Premiere Pro.exe",
    "after effects":    "AfterFX.exe",
    "blender":          "blender.exe",
    "figma":            "Figma.exe",

    # Búsquedas web como fallback
    "google":           "https://www.google.com",
    "gmail":            "https://mail.google.com",
    "google drive":     "https://drive.google.com",
    "google maps":      "https://maps.google.com",
    "github":           "https://github.com",
    "chatgpt":          "https://chat.openai.com",
    "openai":           "https://openai.com",
    "amazon":           "https://www.amazon.com",
    "mercadolibre":     "https://www.mercadolibre.com",
}

# Directorios donde buscar ejecutables
_SEARCH_DIRS: list[str] = [
    os.environ.get("LOCALAPPDATA", ""),
    os.environ.get("PROGRAMFILES", "C:\\Program Files"),
    os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
    os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
]


def _launch(target: str) -> bool:
    """Intenta lanzar un target (exe, url, protocolo). Retorna True si tuvo éxito."""
    try:
        # URL o protocolo de Windows (ms-settings:, spotify:, etc.)
        if target.startswith("http") or ":" in target and not target.endswith(".exe"):
            os.startfile(target)
            return True

        # Ejecutable directo
        subprocess.Popen(
            [target],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return True
    except Exception:
        return False


def _find_exe_in_dirs(app_name: str) -> str | None:
    """Busca un .exe que contenga el nombre de la app en los directorios de instalación."""
    search_name = app_name.lower().replace(" ", "")
    for base_dir in _SEARCH_DIRS:
        if not base_dir or not os.path.isdir(base_dir):
            continue
        try:
            for root, dirs, files in os.walk(base_dir):
                # No bajar demasiado profundo
                depth = root.replace(base_dir, "").count(os.sep)
                if depth > 4:
                    dirs.clear()
                    continue
                for f in files:
                    if f.lower().endswith(".exe") and search_name in f.lower().replace(" ", ""):
                        return os.path.join(root, f)
        except PermissionError:
            continue
    return None


def _open_as_web_search(app_name: str) -> bool:
    """Abre una búsqueda de Google como último recurso."""
    url = f"https://www.google.com/search?q={app_name.replace(' ', '+')}"
    try:
        os.startfile(url)
        return True
    except Exception:
        return False


def open_app(parameters: dict, response: Any = None, player: Any = None, speak=None) -> str:
    """
    Abre cualquier aplicación en Windows.

    Args:
        parameters: dict con clave 'app_name' (str).
        response: no usado (compatibilidad).
        player: JarvisUI (para write_log).
        speak: función TTS (opcional).

    Returns:
        Mensaje de resultado para Gemini.
    """
    app_name: str = parameters.get("app_name", "").strip()
    if not app_name:
        return "No especificaste qué aplicación abrir, señor."

    def log(msg: str):
        if player:
            try:
                player.write_log(msg)
            except Exception:
                pass
        try:
            print(f"[open_app] {msg}")
        except UnicodeEncodeError:
            print(f"[open_app] {msg.encode('ascii', errors='replace').decode()}")

    log(f"🚀 Abriendo: {app_name}")

    # ── Estrategia 1: Alias map ───────────────────────────────────────────
    key = app_name.lower().strip()
    target = _APP_MAP.get(key)
    if target and _launch(target):
        return f"Abriendo {app_name}, señor."

    # ── Estrategia 2: Alias parcial (contiene la palabra clave) ──────────
    for alias, cmd in _APP_MAP.items():
        if alias in key or key in alias:
            if _launch(cmd):
                return f"Abriendo {app_name}, señor."

    # ── Estrategia 3: Ruta existente ──────────────────────────────────────
    if os.path.exists(app_name):
        if _launch(app_name):
            return f"Abriendo {app_name}, señor."

    # ── Estrategia 4: subprocess directo con el nombre ────────────────────
    exe_name = app_name if app_name.endswith(".exe") else app_name + ".exe"
    if _launch(exe_name):
        return f"Abriendo {app_name}, señor."

    # ── Estrategia 5: Búsqueda en directorios de instalación ─────────────
    found = _find_exe_in_dirs(app_name)
    if found:
        log(f"✅ Encontrado en: {found}")
        if _launch(found):
            return f"Abriendo {app_name} desde {found}, señor."

    # ── Estrategia 6: Windows Store (ms-get:) ─────────────────────────────
    try:
        store_target = f"ms-windows-store://search/?query={app_name.replace(' ', '%20')}"
        os.startfile(store_target)
        return f"No encontré {app_name} instalado. Abriendo la Windows Store para buscarlo, señor."
    except Exception:
        pass

    # ── Estrategia 7: Búsqueda web como último recurso ───────────────────
    _open_as_web_search(app_name)
    return f"No encontré {app_name} instalado. Busqué en Google para que puedas descargarlo, señor."
