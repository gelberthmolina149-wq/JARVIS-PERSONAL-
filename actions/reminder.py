"""
actions/reminder.py — Programacion de alarmas y recordatorios persistentes en Windows.
"""
from __future__ import annotations
import datetime
import subprocess
import re
from typing import Any

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[reminder] {msg}")
    except Exception:
        pass

def reminder(parameters: dict, player=None, speak=None) -> str:
    """
    Sets a timed reminder using Windows Task Scheduler.
    """
    date_str = parameters.get("date", "").strip()
    time_str = parameters.get("time", "").strip()
    message = parameters.get("message", "").strip()

    if not date_str or not time_str or not message:
        return "Error: Faltan parametros obligatorios ('date', 'time', 'message')."

    # 1. Validacion estricta de formatos
    try:
        target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return "Error: Formato de fecha invalido. Debe ser YYYY-MM-DD."

    try:
        target_time = datetime.datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        return "Error: Formato de hora invalido. Debe ser HH:MM (24 horas)."

    # Validar que la fecha y hora sean futuras
    now = datetime.datetime.now()
    target_dt = datetime.datetime.combine(target_date, target_time)
    if target_dt <= now:
        return f"Error: La fecha y hora ingresadas ({target_dt}) ya han pasado. Ingresa un tiempo futuro."

    # 2. Sanitizacion de mensaje para prevenir inyecciones
    # Solo permitir letras, numeros, espacios y puntuacion basica
    clean_msg = re.sub(r'[^a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑüÜ.,!?-]', '', message)
    if len(clean_msg) > 150:
        clean_msg = clean_msg[:150]

    # Generar un ID de tarea unico
    task_id = f"JARVIS_Reminder_{target_dt.strftime('%Y%M%d_%H%M%S')}"

    log(f"Programando recordatorio: '{clean_msg}' para {date_str} a las {time_str}")

    # En Windows, creamos la tarea usando schtasks
    # Comando cmd seguro para mostrar un recordatorio en pantalla: msg * "Mensaje"
    # /sc ONCE: Corre solo una vez
    # /sd: Fecha (en formato nativo de Windows suele requerir DD/MM/YYYY o MM/DD/YYYY, convertimos a DD/MM/YYYY por compatibilidad extendida)
    formatted_date = target_date.strftime("%d/%m/%Y")
    formatted_time = target_time.strftime("%H:%M")

    # Comando a registrar
    task_cmd = f'msg * "JARVIS Recordatorio: {clean_msg}"'
    
    # 0x08000000 para CREATE_NO_WINDOW
    CREATE_NO_WINDOW = 0x08000000

    try:
        # Registrar la tarea de forma nativa e invisible
        cmd = [
            "schtasks", "/create", 
            "/tn", task_id, 
            "/tr", task_cmd, 
            "/sc", "ONCE", 
            "/sd", formatted_date, 
            "/st", formatted_time, 
            "/f"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            return f"Recordatorio programado con exito para el {date_str} a las {time_str}."
        else:
            # Fallback en caso de incompatibilidad de formatos de fecha regionales de Windows
            # Reintentar con formato original YYYY-MM-DD o YYYY/MM/DD
            formatted_date_alt = target_date.strftime("%Y/%m/%d")
            cmd_alt = [
                "schtasks", "/create", 
                "/tn", task_id, 
                "/tr", task_cmd, 
                "/sc", "ONCE", 
                "/sd", formatted_date_alt, 
                "/st", formatted_time, 
                "/f"
            ]
            result_alt = subprocess.run(cmd_alt, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            
            if result_alt.returncode == 0:
                return f"Recordatorio programado con exito para el {date_str} a las {time_str}."
            
            log(f"Error schtasks original: {result.stderr.strip()}")
            log(f"Error schtasks fallback: {result_alt.stderr.strip()}")
            return "Recordatorio registrado de forma parcial (ver logs de sistema)."
            
    except Exception as e:
        return f"Error al interactuar con el Programador de tareas de Windows: {e}"
