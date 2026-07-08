"""
actions/accessibility_overlay.py — Control seguro de la barra flotante de accesibilidad.
"""
from __future__ import annotations
from typing import Any

ALLOWED_OVERLAY_ACTIONS = {"show", "hide", "toggle", "status"}

def accessibility_overlay(parameters: dict, player=None, speak=None) -> str:
    """
    Muestra, oculta o alterna la barra flotante de accesibilidad JARVIS sobre el escritorio.
    """
    action = parameters.get("action", "").strip().lower()

    if not action:
        return "[ERROR] Falta el parametro obligatorio 'action'."

    if action not in ALLOWED_OVERLAY_ACTIONS:
        return f"[ERROR] Accion '{action}' no permitida en la barra de accesibilidad."

    # --- 1. MOCK INTERACTION WITH UI ---
    if action == "show":
        return "[OK] Barra flotante de accesibilidad mostrada en el escritorio."
    elif action == "hide":
        return "[OK] Barra flotante de accesibilidad oculta."
    elif action == "toggle":
        return "[OK] Barra de accesibilidad alternada con éxito."
    elif action == "status":
        return "[INFO] Barra de accesibilidad: Estado actual es Oculta."
    else:
        return f"[ERROR] Accion '{action}' no soportada."
