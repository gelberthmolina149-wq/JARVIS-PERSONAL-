"""
actions/smart_home.py — Control seguro y unificado de dispositivos inteligentes (Smart Home).
"""
from __future__ import annotations
import re
from typing import Any

# Expresión regular para validar colores en formato Hex (#RRGGBB o RRGGBB)
HEX_COLOR_PATTERN = re.compile(r'^#?[0-9a-fA-F]{6}$')

# Nombres de colores predefinidos permitidos
ALLOWED_COLOR_NAMES = {
    "rojo", "azul", "verde", "amarillo", "blanco", "calido", 
    "frio", "purpura", "naranja", "rosa", "cian", "magenta"
}

def smart_home(parameters: dict, player=None, speak=None) -> str:
    """
    Controla luces y dispositivos inteligentes utilizando varios protocolos (Hue, Tuya, LIFX, Yeelight).
    """
    action = parameters.get("action", "").strip().lower()
    device = parameters.get("device", "").strip()
    color = parameters.get("color", "").strip().lower()
    value = parameters.get("value", None)
    brightness = parameters.get("brightness", None)
    scene = parameters.get("scene", "").strip()
    protocol = parameters.get("protocol", "").strip().lower()
    group = parameters.get("group", "").strip()

    if not action:
        return "[ERROR] Falta el parametro obligatorio 'action'."

    # --- 1. SETUP INSTRUCTIONS ---
    if action == "setup":
        return (
            "[INFO] Configuración de Smart Home de JARVIS:\n"
            "  Para habilitar dispositivos reales, configure las credenciales en 'config/api_keys.json':\n"
            "  - Tuya: Client ID, Secret, y Device ID.\n"
            "  - Philips Hue: IP del Bridge y API Token.\n"
            "  - Yeelight/LIFX: Descubrimiento automatico en red local habilitado.\n"
            "  Actualmente ejecutando en modo de simulacion."
        )

    # --- 2. VALIDACIONES DE SEGURIDAD ---
    # Validacion del parametro Color
    if color:
        is_hex = HEX_COLOR_PATTERN.match(color)
        is_named = color in ALLOWED_COLOR_NAMES
        if not (is_hex or is_named):
            return f"[ERROR] El color '{color}' no tiene un formato seguro o valido (use nombres basicos o hex #RRGGBB)."

    # Validacion de limites de Brillo y Temperatura
    target_brightness = brightness if brightness is not None else value
    if target_brightness is not None:
        try:
            val = int(target_brightness)
            # Brillo: 1-100, Temperatura: 1700-9000
            if val < 0 or val > 9000:
                return "[ERROR] El valor ingresado para brillo/temperatura esta fuera de los limites permitidos."
        except ValueError:
            return "[ERROR] El parametro de brillo/temperatura debe ser un numero entero."

    # --- 3. EJECUCION / SIMULACION DE ACCIONES ---
    device_name = device if device else "todos los dispositivos"
    proto_name = f" usando {protocol}" if protocol else ""

    if action == "on":
        return f"[OK] Encendido: {device_name}{proto_name}."
        
    elif action == "off":
        return f"[OK] Apagado: {device_name}{proto_name}."
        
    elif action == "toggle":
        return f"[OK] Estado alternado para: {device_name}."
        
    elif action == "color":
        if not color:
            return "[ERROR] Falta el parametro 'color' para cambiar el color."
        return f"[OK] Color de {device_name} cambiado a '{color}'."
        
    elif action == "brightness":
        if target_brightness is None:
            return "[ERROR] Falta especificar el valor de brillo."
        return f"[OK] Brillo de {device_name} ajustado a {target_brightness}%."
        
    elif action == "temperature":
        if target_brightness is None:
            return "[ERROR] Falta especificar el valor de temperatura (Kelvin)."
        return f"[OK] Temperatura de {device_name} ajustada a {target_brightness} K."
        
    elif action == "scene":
        if not scene:
            return "[ERROR] Falta especificar la 'scene' a activar."
        return f"[OK] Escena '{scene}' activada en {device_name}."
        
    elif action == "status":
        return f"[INFO] Estado de {device_name}: Luces encendidas, Brillo al 80%, Color: Blanco."
        
    elif action == "list":
        return (
            "[INFO] Dispositivos en red inteligente:\n"
            "  1. Lámpara Principal (Techo) - yeelight [Apagado]\n"
            "  2. Luz de Escritorio - hue [Encendido - Blanco Cálido]\n"
            "  3. Smart Plug (Ventilador) - tuya [Apagado]"
        )

    else:
        return f"[ERROR] Accion '{action}' no soportada en Smart Home."
