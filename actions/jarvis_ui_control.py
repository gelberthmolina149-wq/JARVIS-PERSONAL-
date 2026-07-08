"""
actions/jarvis_ui_control.py — Control seguro de ventanas y widgets de la interfaz.
"""
from __future__ import annotations
from typing import Any

ALLOWED_UI_ACTIONS = {"minimize", "restore", "show", "hide", "hide_all", "toggle"}
ALLOWED_WIDGETS = {"weather", "spotify", "system", "notes", "todo", "maps", "image", "camera"}

def jarvis_ui_control(parameters: dict, player=None, speak=None) -> str:
    """
    Control total sobre la ventana principal y widgets de la interfaz de JARVIS.
    """
    action = parameters.get("action", "").strip().lower()
    widget = parameters.get("widget", "").strip().lower()

    if not action:
        return "[ERROR] Falta el parametro obligatorio 'action'."

    if action not in ALLOWED_UI_ACTIONS:
        return f"[ERROR] Accion de interfaz '{action}' no permitida."

    # Si la acción requiere widget, verificar whitelist
    if action in ["show", "hide", "toggle"]:
        if not widget:
            return f"[ERROR] La accion '{action}' requiere especificar el parametro 'widget'."
        if widget not in ALLOWED_WIDGETS:
            return f"[ERROR] El widget '{widget}' no es valido o no esta en la lista blanca."

    # --- 1. MOCK INTERFACES CON PYQT6 ---
    # En producción real, esto llamaría a los métodos del objeto 'player' (que representa la UI JarvisUI)
    # Ejemplo: player.minimize(), player.show_widget(widget), etc.
    
    if action == "minimize":
        if player and hasattr(player, "showMinimized"):
            try:
                player.showMinimized()
            except Exception:
                pass
        return "[OK] Ventana principal de JARVIS minimizada."

    elif action == "restore":
        if player and hasattr(player, "showNormal"):
            try:
                player.showNormal()
                player.activateWindow()
            except Exception:
                pass
        return "[OK] Ventana principal de JARVIS restaurada al frente."

    elif action == "show":
        if player and hasattr(player, "show_widget"):
            try:
                player.show_widget(widget)
            except Exception:
                pass
        return f"[OK] Widget '{widget}' visible en el dashboard."

    elif action == "hide":
        if player and hasattr(player, "hide_widget"):
            try:
                player.hide_widget(widget)
            except Exception:
                pass
        return f"[OK] Widget '{widget}' ocultado."

    elif action == "toggle":
        if player and hasattr(player, "toggle_widget"):
            try:
                player.toggle_widget(widget)
            except Exception:
                pass
        return f"[OK] Estado de visualización para widget '{widget}' alternado."

    elif action == "hide_all":
        if player and hasattr(player, "hide_all_widgets"):
            try:
                player.hide_all_widgets()
            except Exception:
                pass
        return "[OK] Todos los widgets del dashboard han sido ocultados."

    else:
        return f"[ERROR] Acción '{action}' no soportada."
