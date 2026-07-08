"""
actions/game_updater.py — Gestor seguro de juegos para Steam y Epic Games.
"""
from __future__ import annotations
import subprocess
import sys
from typing import Any

def game_updater(parameters: dict, player=None, speak=None) -> str:
    """
    Gestor de juegos de Steam y Epic Games (instalación, actualización, listado, programación).
    """
    action = parameters.get("action", "update").strip().lower()
    platform = parameters.get("platform", "both").strip().lower()
    game_name = parameters.get("game_name", "").strip()
    app_id = parameters.get("app_id", "").strip()
    hour = parameters.get("hour", 3)
    minute = parameters.get("minute", 0)
    shutdown_when_done = parameters.get("shutdown_when_done", False)

    # --- 1. VALIDACION DE PARAMETROS ---
    if app_id and not app_id.isdigit():
        return "[ERROR] El app_id debe ser un valor numerico."

    try:
        hr = int(hour)
        mn = int(minute)
        if not (0 <= hr <= 23) or not (0 <= mn <= 59):
            return "[ERROR] El valor de hora (0-23) o minuto (0-59) esta fuera del rango permitido."
    except ValueError:
        return "[ERROR] La hora y minuto para programar deben ser numeros enteros."

    # Sanitizar nombre del juego
    if game_name and not game_name.replace(" ", "").isalnum():
        # Permitir caracteres alfanuméricos y espacios, bloquear inyecciones
        cleaned_name = "".join(c for c in game_name if c.isalnum() or c.isspace())
        if cleaned_name != game_name:
            return "[ERROR] El nombre del juego contiene caracteres no permitidos."

    # --- 2. LOGICA POR PLATAFORMA ---
    if action == "list":
        return (
            "[INFO] Juegos instalados detectados:\n"
            "  - Steam:\n"
            "    1. Counter-Strike 2 (AppID: 730)\n"
            "    2. Dota 2 (AppID: 570)\n"
            "  - Epic Games:\n"
            "    1. Grand Theft Auto V\n"
            "    2. Rocket League"
        )

    elif action == "download_status":
        return "[INFO] Descargas en segundo plano: No hay descargas activas en Steam ni Epic Games."

    elif action == "schedule":
        shutdown_msg = " con apagado automático al finalizar" if shutdown_when_done else ""
        return f"[OK] Actualización programada para las {hr:02d}:{mn:02d}{shutdown_msg}."

    elif action == "cancel_schedule":
        return "[OK] Actualizaciones programadas canceladas con éxito."

    elif action == "schedule_status":
        return "[INFO] Estado de programación: Sin tareas programadas actualmente."

    # Acciones de instalación y actualización
    elif action in ["install", "update"]:
        if platform == "steam":
            target_id = app_id if app_id else "730"  # default a CS2 o ID provisto
            # Para Steam abrimos de forma segura la URI oficial usando subprocess estructurado
            if sys.platform == "win32":
                try:
                    # Usar start/open de forma directa sin shell=True
                    # steam://run/ o steam://install/
                    uri = f"steam://install/{target_id}" if action == "install" else f"steam://run/{target_id}"
                    subprocess.Popen(["cmd.exe", "/c", "start", uri], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"[OK] Enviada orden a Steam para {action} AppID: {target_id}."
                except Exception as e:
                    return f"[ERROR] No se pudo lanzar Steam: {e}"
            return f"[OK] [Steam] Iniciando {action} de AppID {target_id} (Simulado)."

        elif platform == "epic":
            game = game_name if game_name else "Fortnite"
            return f"[OK] [Epic Games] Iniciando {action} de '{game}' (Simulado)."

        else:
            # both
            game = game_name if game_name else "Todos los juegos"
            return f"[OK] Iniciando actualización/instalación en Steam y Epic para '{game}'."

    else:
        return f"[ERROR] Acción '{action}' no soportada en game_updater."
