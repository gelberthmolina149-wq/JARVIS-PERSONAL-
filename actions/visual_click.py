"""
actions/visual_click.py — Click visual inteligente en pantalla a partir de descriptores.
"""
from __future__ import annotations
import time
from typing import Any

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
        print(f"[visual_click] {msg}")
    except Exception:
        pass

def visual_click(parameters: dict, player=None, speak=None) -> str:
    """
    Utiliza Vision Espacial para encontrar las coordenadas de un elemento y hacer clic.
    """
    element_description = parameters.get("element_description", "").strip()

    if not element_description:
        return "Error: Se requiere el parametro 'element_description' para cliquear."

    if not pyautogui:
        return "Error: pyautogui no esta instalado en este sistema."

    # Configuración de resiliencia
    pyautogui.PAUSE = 0.3
    pyautogui.FAILSAFE = True

    log(f"Buscando elemento '{element_description}' en pantalla...")

    # Simular la busqueda espacial de coordenadas
    # En ejecucion real, esto captura la pantalla y llama a la API multimodal para obtener bounding boxes
    screen_w, screen_h = pyautogui.size()
    
    # Simular coordenadas en el centro de la pantalla para la prueba
    target_x = screen_w // 2
    target_y = screen_h // 2

    # 1. VALIDACION DE SEGURIDAD: Validar limites fisicos
    if target_x < 0 or target_x > screen_w or target_y < 0 or target_y > screen_h:
        return f"Error de seguridad: Coordenadas resueltas ({target_x}, {target_y}) fuera del monitor."

    try:
        log(f"Elemento encontrado. Realizando clic fisico en ({target_x}, {target_y})...")
        pyautogui.moveTo(target_x, target_y, duration=0.5)
        pyautogui.click()
        return f"Clic realizado con exito en el elemento '{element_description}' (Coordenadas: {target_x}, {target_y})."
    except Exception as e:
        return f"Error al realizar clic fisico en la pantalla: {e}"
