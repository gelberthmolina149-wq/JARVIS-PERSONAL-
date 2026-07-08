"""
actions/computer_control.py — Control directo de interfaz de usuario mediante teclado y mouse en Windows.
"""
from __future__ import annotations
import time
from typing import Any
from pathlib import Path

try:
    import pyautogui
except ImportError:
    pyautogui = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[computer_control] {msg}")
    except Exception:
        pass

def is_safe_path(path: Path) -> bool:
    """Verifica que no se escriba en carpetas criticas de sistema para screenshots."""
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

def computer_control(parameters: dict, player=None, speak=None) -> str:
    """
    Direct computer control: type, click, double_click, right_click, hotkey, press, scroll, move, screenshot, wait, clear_field.
    """
    action = parameters.get("action", "").lower()
    text = parameters.get("text", "")
    x = parameters.get("x")
    y = parameters.get("y")
    keys = parameters.get("keys", "")
    key = parameters.get("key", "")
    direction = parameters.get("direction", "down").lower()
    amount = parameters.get("amount", 3)
    seconds = parameters.get("seconds")
    path_str = parameters.get("path", "")
    clear_first = parameters.get("clear_first", True)

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    if not pyautogui:
        return "Error: pyautogui no esta instalado en este sistema."

    # Configuración de resiliencia
    pyautogui.PAUSE = 0.3
    pyautogui.FAILSAFE = True

    # Obtener resolucion de pantalla
    screen_w, screen_h = pyautogui.size()

    # Validacion de coordenadas
    if x is not None and y is not None:
        try:
            x_int = int(x)
            y_int = int(y)
            if x_int < 0 or x_int > screen_w or y_int < 0 or y_int > screen_h:
                return f"Error: Coordenadas ({x_int}, {y_int}) fuera de los limites de pantalla ({screen_w}x{screen_h})."
        except (ValueError, TypeError):
            return "Error: Coordenadas X e Y deben ser enteros validos."

    log(f"Ejecutando accion '{action}'")

    if action == "type":
        if not text:
            return "Error: Falta el parametro 'text' para escribir."
        pyautogui.write(text, interval=0.05)
        return f"Texto escrito en pantalla: '{text[:30]}'."

    elif action == "click":
        if x is not None and y is not None:
            pyautogui.click(int(x), int(y))
            return f"Clic izquierdo realizado en ({x}, {y})."
        else:
            pyautogui.click()
            return "Clic izquierdo realizado en la posicion actual del cursor."

    elif action == "double_click":
        if x is not None and y is not None:
            pyautogui.doubleClick(int(x), int(y))
            return f"Doble clic realizado en ({x}, {y})."
        else:
            pyautogui.doubleClick()
            return "Doble clic realizado en la posicion actual."

    elif action == "right_click":
        if x is not None and y is not None:
            pyautogui.rightClick(int(x), int(y))
            return f"Clic derecho realizado en ({x}, {y})."
        else:
            pyautogui.rightClick()
            return "Clic derecho realizado en la posicion actual."

    elif action == "hotkey":
        if not keys:
            return "Error: Se requiere el parametro 'keys' (ej: 'ctrl+c')."
        # Desarmar keys combinadas por "+"
        key_list = [k.strip() for k in keys.split("+")]
        pyautogui.hotkey(*key_list)
        return f"Combinacion de teclas presionada: {keys}."

    elif action == "press":
        if not key:
            return "Error: Se requiere el parametro 'key' (ej: 'enter')."
        pyautogui.press(key)
        return f"Tecla presionada: '{key}'."

    elif action == "scroll":
        # amount determina la cantidad de 'clicks' de scroll
        # pyautogui.scroll toma valores positivos (arriba) o negativos (abajo)
        scroll_clicks = int(amount) * 100
        if direction == "up":
            pyautogui.scroll(scroll_clicks)
        else:
            pyautogui.scroll(-scroll_clicks)
        return f"Scroll realizado: {direction} ({amount} unidades)."

    elif action == "move":
        if x is not None and y is not None:
            pyautogui.moveTo(int(x), int(y), duration=0.3)
            return f"Cursor movido a ({x}, {y})."
        else:
            return "Error: La accion 'move' requiere coordenadas X e Y."

    elif action == "screenshot":
        # Validar ruta destino
        if not path_str:
            path_obj = Path.home() / "Desktop" / f"screenshot_{int(time.time())}.png"
        else:
            path_obj = Path(path_str).resolve()

        if not is_safe_path(path_obj):
            return f"Error de seguridad: Acceso denegado a la ruta destino de captura '{path_obj}'."

        try:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            screenshot = pyautogui.screenshot()
            screenshot.save(str(path_obj))
            return f"Captura de pantalla guardada en '{path_obj}'."
        except Exception as e:
            return f"Error al guardar captura de pantalla: {e}"

    elif action == "wait":
        if seconds is None:
            seconds = 1.0
        try:
            wait_time = float(seconds)
            time.sleep(wait_time)
            return f"Espera completada ({wait_time} segundos)."
        except (ValueError, TypeError):
            return "Error: El parametro 'seconds' debe ser un numero valido."

    elif action == "clear_field":
        # Estrategia estandar para limpiar un campo de texto
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.press("backspace")
        return "Campo de entrada limpiado con Ctrl+A y Backspace."

    else:
        return f"Error: Accion '{action}' no reconocida en computer_control."
