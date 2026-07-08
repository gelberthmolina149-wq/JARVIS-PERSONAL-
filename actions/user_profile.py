"""
actions/user_profile.py — Administracion segura del perfil de usuario y preferencias de JARVIS.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

PROFILE_FILE = Path("config/user_profile.json")
MAX_PREFERENCES = 100

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[user_profile] {msg}")
    except Exception:
        pass

def load_profile() -> dict[str, Any]:
    """Carga de forma segura el perfil de usuario JSON."""
    if not PROFILE_FILE.exists():
        PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    try:
        if PROFILE_FILE.stat().st_size > 50 * 1024: # Limite a 50KB
            return {}
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_profile(profile: dict[str, Any]) -> bool:
    """Guarda de forma segura el perfil de usuario JSON."""
    try:
        data_str = json.dumps(profile, indent=4, ensure_ascii=False)
        if len(data_str.encode("utf-8")) > 50 * 1024:
            return False
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            f.write(data_str)
        return True
    except Exception as e:
        log(f"Error al guardar perfil: {e}")
        return False

def record_action(action_name: str):
    pass

def user_profile(parameters: dict, player=None, speak=None) -> str:
    """
    Manages user profile preferences: get, set, delete, list.
    """
    action = parameters.get("action", "").lower().strip()
    key = parameters.get("key", "").strip()
    value = parameters.get("value", "").strip()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    profile = load_profile()

    if action == "set":
        if not key or not value:
            return "Error: Asignar preferencia requiere 'key' y 'value'."

        # 1. VALIDACION DE SEGURIDAD: Evitar almacenar credenciales confidenciales en texto plano
        key_lower = key.lower()
        sensitive_terms = ["api", "key", "token", "password", "contraseña", "secret"]
        if any(term in key_lower for term in sensitive_terms):
            return "Error de seguridad: No se permite almacenar tokens, contraseñas o llaves de API en el perfil de usuario."

        if len(profile) >= MAX_PREFERENCES:
            return f"Error: Se alcanzo el limite maximo de {MAX_PREFERENCES} preferencias en el perfil de usuario."

        # Limitar longitud de valor
        if len(value) > 200:
            value = value[:200]

        profile[key] = value
        if save_profile(profile):
            return f"Preferencia '{key}' guardada exitosamente."
        else:
            return "Error al guardar la preferencia."

    elif action == "get":
        if not key:
            return "Error: Se requiere 'key' para consultar."
        
        if key in profile:
            return f"Preferencia '{key}': '{profile[key]}'."
        return f"La preferencia '{key}' no esta definida."

    elif action == "delete":
        if not key:
            return "Error: Se requiere 'key' para eliminar."
        
        if key in profile:
            del profile[key]
            save_profile(profile)
            return f"Preferencia '{key}' eliminada del perfil."
        return f"La preferencia '{key}' no existe en el perfil."

    elif action == "list":
        if not profile:
            return "El perfil de usuario no tiene preferencias definidas."
        
        res = "Preferencias del Perfil de Usuario:\n"
        for k, v in sorted(profile.items()):
            res += f"  - {k}: {v}\n"
        return res.strip()

    else:
        return f"Error: Accion '{action}' no reconocida en user_profile."
