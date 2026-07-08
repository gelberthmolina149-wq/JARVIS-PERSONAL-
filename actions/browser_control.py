"""
actions/browser_control.py — Control de navegador web activo en Windows.
"""
from __future__ import annotations
import urllib.parse
import webbrowser
import time
from typing import Any

try:
    import pygetwindow as gw
except ImportError:
    gw = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

# Escribir logs limpios sin emojis problemáticos para evitar caídas de cp1252 en Windows
def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[browser_control] {msg}")
    except Exception:
        pass

def get_active_browser_window() -> Any:
    """Busca una ventana activa que coincida con navegadores conocidos."""
    if not gw:
        return None
    
    browsers = ["chrome", "edge", "firefox", "brave", "opera", "browser", "navegador"]
    try:
        windows = gw.getAllWindows()
        for w in windows:
            title = w.title.lower()
            if any(b in title for b in browsers):
                return w
    except Exception as e:
        log(f"Error al listar ventanas: {e}")
    return None

def browser_control(parameters: dict, player=None, speak=None) -> str:
    """
    Controla el navegador activo del usuario (Chrome, Edge, Firefox, etc.) sin abrir uno nuevo.
    """
    action = parameters.get("action", "").lower()
    url = parameters.get("url", "").strip()
    query = parameters.get("query", "").strip()
    direction = parameters.get("direction", "down").lower()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    # Configuración de seguridad para pyautogui
    if pyautogui:
        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True

    # 1. Validaciones de Seguridad de URL
    if url:
        parsed = urllib.parse.urlparse(url)
        # Forzar protocolo si falta
        if not parsed.scheme:
            url = "https://" + url
            parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return f"Error de seguridad: Protocolo '{parsed.scheme}' no permitido. Solo se admite http o https."

    log(f"Ejecutando accion: {action}")

    # Encontrar ventana de navegador si aplica
    browser_win = get_active_browser_window()

    if action == "go_to":
        if not url:
            return "Error: La accion 'go_to' requiere un 'url'."
        
        if browser_win:
            try:
                log(f"Navegador detectado: '{browser_win.title}'. Enfocando...")
                browser_win.activate()
                time.sleep(0.3)
                if pyautogui:
                    pyautogui.hotkey("ctrl", "l")
                    time.sleep(0.2)
                    pyautogui.write(url)
                    pyautogui.press("enter")
                    return f"Navegando a {url} en la ventana activa."
            except Exception as e:
                log(f"No se pudo enfocar la ventana activa ({e}). Abriendo en navegador predeterminado.")
        
        # Fallback a apertura normal
        webbrowser.open(url)
        return f"Abriendo {url} en un nuevo navegador."

    elif action == "search":
        if not query:
            return "Error: La accion 'search' requiere un 'query'."
        
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        if browser_win:
            try:
                log(f"Navegador detectado: '{browser_win.title}'. Enfocando para buscar...")
                browser_win.activate()
                time.sleep(0.3)
                if pyautogui:
                    pyautogui.hotkey("ctrl", "l")
                    time.sleep(0.2)
                    pyautogui.write(search_url)
                    pyautogui.press("enter")
                    return f"Buscando '{query}' en la ventana activa."
            except Exception as e:
                log(f"No se pudo usar la ventana activa ({e}). Abriendo busqueda por defecto.")
        
        webbrowser.open(search_url)
        return f"Abriendo busqueda para '{query}' en nuevo navegador."

    elif action == "new_tab":
        if browser_win:
            try:
                browser_win.activate()
                time.sleep(0.2)
                if pyautogui:
                    pyautogui.hotkey("ctrl", "t")
                    if url:
                        time.sleep(0.3)
                        pyautogui.write(url)
                        pyautogui.press("enter")
                    return f"Nueva pestana abierta" + (f" con {url}" if url else "") + "."
            except Exception as e:
                log(f"Error al abrir pestana en ventana activa: {e}")
        
        # Fallback
        if url:
            webbrowser.open_new_tab(url)
            return f"Abriendo {url} en nueva pestana."
        else:
            return "Error: No hay navegador activo enfocado para abrir nueva pestana vacia."

    elif action == "close_tab":
        if browser_win:
            try:
                browser_win.activate()
                time.sleep(0.2)
                if pyautogui:
                    pyautogui.hotkey("ctrl", "w")
                    return "Pestana cerrada en el navegador activo."
            except Exception as e:
                return f"Error al cerrar pestana: {e}"
        return "Error: No se encontro ningun navegador activo para cerrar pestana."

    elif action == "scroll":
        if browser_win:
            try:
                browser_win.activate()
                time.sleep(0.2)
                if pyautogui:
                    if direction == "up":
                        pyautogui.press("pageup")
                        return "Scrolleando hacia arriba."
                    else:
                        pyautogui.press("pagedown")
                        return "Scrolleando hacia abajo."
            except Exception as e:
                return f"Error al scrollear: {e}"
        return "Error: No se encontro ningun navegador activo para scrollear."

    else:
        return f"Error: Accion '{action}' no reconocida para browser_control."
