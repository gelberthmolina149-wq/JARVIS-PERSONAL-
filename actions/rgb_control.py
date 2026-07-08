"""
actions/rgb_control.py — Control de dispositivos RGB locales via OpenRGB SDK.
"""
from __future__ import annotations
import re
from typing import Any

try:
    from openrgb import OpenRGBClient
    from openrgb.utils import RGBColor
except ImportError:
    OpenRGBClient = None
    RGBColor = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[rgb_control] {msg}")
    except Exception:
        pass

# Diccionario de colores comunes
COLOR_MAP = {
    "rojo": (255, 0, 0),
    "azul": (0, 0, 255),
    "verde": (0, 255, 0),
    "blanco": (255, 255, 255),
    "amarillo": (255, 255, 0),
    "cian": (0, 255, 255),
    "magenta": (255, 0, 255),
    "naranja": (255, 127, 0),
    "morado": (127, 0, 255),
    "rosa": (255, 192, 203),
    "gris": (127, 127, 127),
}

def parse_color(color_str: str) -> tuple[int, int, int] | None:
    """Valida y parsea el color hexadecimal (#RRGGBB) o por nombre."""
    color_clean = color_str.strip().lower()
    
    # 1. Comprobar diccionario de nombres
    if color_clean in COLOR_MAP:
        return COLOR_MAP[color_clean]
        
    # 2. Comprobar formato hexadecimal
    hex_pattern = re.compile(r"^#?([a-f0-9]{6})$")
    match = hex_pattern.match(color_clean)
    if match:
        hex_val = match.group(1)
        r = int(hex_val[0:2], 16)
        g = int(hex_val[2:4], 16)
        b = int(hex_val[4:6], 16)
        return (r, g, b)
        
    return None

def rgb_control(parameters: dict, player=None, speak=None) -> str:
    """
    Controla las luces RGB de perifericos y componentes de la PC.
    """
    action = parameters.get("action", "").lower().strip()
    color = parameters.get("color", "").strip()
    brightness = parameters.get("brightness")
    device_filter = parameters.get("device", "").lower().strip()
    effect = parameters.get("effect", "").strip()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    if not OpenRGBClient or not RGBColor:
        return "Info: La libreria 'openrgb-python' no esta instalada en este entorno."

    log(f"Ejecutando accion '{action}'")

    # Intentar conexion local silenciosa al servidor SDK de OpenRGB (puerto default: 6742)
    try:
        client = OpenRGBClient("localhost", 6742, client_name="JARVIS")
    except Exception as e:
        log(f"No se pudo conectar al servidor SDK de OpenRGB: {e}")
        return "Error: El servidor SDK de OpenRGB no esta activo en localhost:6742 o no hay dispositivos disponibles."

    try:
        # Obtener lista de dispositivos conectados
        devices = client.devices
        if not devices:
            return "No se detectaron dispositivos RGB compatibles en el servidor."

        # Filtrar dispositivos si se especifico un filtro por nombre
        target_devices = devices
        if device_filter:
            target_devices = [d for d in devices if device_filter in d.name.lower()]
            if not target_devices:
                return f"No se encontraron dispositivos RGB que coincidan con el filtro '{device_filter}'."

        if action == "list":
            res = "Dispositivos RGB conectados:\n"
            for d in devices:
                res += f"  - {d.name} (Modo actual: {d.active_mode})\n"
            return res.strip()

        elif action == "set_color":
            if not color:
                return "Error: Falta el parametro 'color' para cambiar el color."
            rgb = parse_color(color)
            if not rgb:
                return f"Error: Color '{color}' no valido. Usa nombres de colores comunes o formato hexadecimal '#RRGGBB'."
            
            rgb_obj = RGBColor(*rgb)
            for d in target_devices:
                try:
                    d.set_color(rgb_obj)
                except Exception:
                    pass
            return f"Color establecido en {color} para {len(target_devices)} dispositivo(s)."

        elif action == "off":
            off_color = RGBColor(0, 0, 0)
            for d in target_devices:
                try:
                    d.set_color(off_color)
                except Exception:
                    pass
            return f"Iluminacion RGB apagada para {len(target_devices)} dispositivo(s)."

        elif action == "brightness":
            if brightness is None:
                return "Error: Se requiere el parametro 'brightness' (0-100)."
            try:
                bright_val = int(brightness)
                if bright_val < 0 or bright_val > 100:
                    return "Error: El brillo debe estar en el rango de 0 a 100."
                
                # OpenRGB maneja el brillo escalando los colores de forma interna o por modos
                # Escalamos el color de cada led del dispositivo
                for d in target_devices:
                    try:
                        # Escalado manual simple de colores para simular el brillo
                        factor = bright_val / 100.0
                        for led in d.leds:
                            c = led.color
                            led.set_color(RGBColor(int(c.r * factor), int(c.g * factor), int(c.b * factor)))
                    except Exception:
                        pass
                return f"Brillo escalado al {bright_val}% en {len(target_devices)} dispositivo(s)."
            except ValueError:
                return "Error: El brillo debe ser un valor numerico entero."

        elif action == "effect":
            if not effect:
                return "Error: Se requiere el nombre del 'effect'."
            for d in target_devices:
                try:
                    # Comprobar si el dispositivo soporta ese modo/efecto
                    mode_found = None
                    for m in d.modes:
                        if effect.lower() in m.name.lower():
                            mode_found = m
                            break
                    if mode_found:
                        d.set_mode(mode_found.id)
                except Exception:
                    pass
            return f"Efecto '{effect}' aplicado a los dispositivos compatibles."

        elif action == "rainbow":
            # Cambia a modo Rainbow si esta disponible en los dispositivos
            rainbow_applied = 0
            for d in target_devices:
                try:
                    for m in d.modes:
                        if "rainbow" in m.name.lower() or "ciclo" in m.name.lower() or "color cycle" in m.name.lower():
                            d.set_mode(m.id)
                            rainbow_applied += 1
                            break
                except Exception:
                    pass
            return f"Efecto Arco Iris / Ciclo de color establecido en {rainbow_applied} dispositivo(s)."

        else:
            return f"Error: Accion '{action}' no reconocida en rgb_control."

    except Exception as e:
        return f"Error durante la interaccion con OpenRGB: {e}"
