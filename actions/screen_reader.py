"""
actions/screen_reader.py — Lector de pantalla seguro para accesibilidad y extraccion de informacion.
"""
from __future__ import annotations
import re
from typing import Any

try:
    import pygetwindow as gw
except ImportError:
    gw = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[screen_reader] {msg}")
    except Exception:
        pass

# Palabras clave de secretos a omitir de forma activa
_SECRET_TERMS = ["api_key", "password", "token", "secret", "contraseña", "jwt"]

def sanitize_read_text(text: str) -> str:
    """Remueve de forma proactiva lineas o bloques que contengan credenciales expuestas."""
    lines = text.splitlines()
    clean_lines = []
    
    # Expresiones regulares para capturar llaves de APIs comunes
    api_key_regex = re.compile(r'\b[A-Za-z0-9_\-]{20,60}\b')

    for line in lines:
        line_lower = line.lower()
        if any(term in line_lower for term in _SECRET_TERMS):
            clean_lines.append("[FILTRADO POR SEGURIDAD]")
            continue
        # Ofuscar si parece una clave
        if api_key_regex.search(line) and ("key" in line_lower or "api" in line_lower):
            clean_lines.append("[LLAVE DE API FILTRADA]")
            continue
        clean_lines.append(line)
        
    return "\n".join(clean_lines)

def screen_reader(parameters: dict, player=None, speak=None) -> str:
    """
    Accessibility reader of text on screen.
    """
    action = parameters.get("action", "read_all").lower().strip()

    log(f"Ejecutando lector de pantalla con accion '{action}'...")

    # Simular la lectura del arbol de accesibilidad o textos en pantalla
    # En entornos reales esto puede usar librerias como pywinauto para recorrer los controles UI
    mock_screen_text = (
        "Bandeja de Entrada - Outlook\n"
        "Remitente: soporte@empresa.com\n"
        "Contenido: Por favor revisa la api_key: AIzaSyDsf92h182h para la conexion de base de datos.\n"
        "Ventana de comandos activa - PowerShell\n"
        "Comando: git status\n"
        "Preferencias del Sistema - Brillo: 80%"
    )

    # 1. VALIDACION DE SEGURIDAD: Limite del tamaño del buffer leído (50KB max)
    if len(mock_screen_text) > 50 * 1024:
        mock_screen_text = mock_screen_text[:50 * 1024]

    # 2. VALIDACION DE SEGURIDAD: Filtrar llaves y secretos
    clean_text = sanitize_read_text(mock_screen_text)

    if action == "read_all":
        return f"Texto leido en pantalla:\n---\n{clean_text}"
        
    elif action == "read_focused":
        active_title = "Ventana Desconocida"
        if gw:
            try:
                active_win = gw.getActiveWindow()
                if active_win:
                    active_title = active_win.title
            except Exception:
                pass
        return f"Texto en ventana enfocada [{active_title}]:\n---\n{clean_text.splitlines()[0]}"

    elif action == "read_window":
        return f"Texto de ventana de control:\n---\n{clean_text}"

    else:
        return f"Error: Accion '{action}' no soportada por el lector de pantalla."
