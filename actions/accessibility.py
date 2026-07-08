"""
actions/accessibility.py — Módulo de accesibilidad universal con validaciones de rango.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ALLOWED_ACC_ACTIONS = {
    "task_simplify", "emotional", "routine", "eye_tracking", 
    "micro_movement", "speech_config", "feedback", "config"
}

def accessibility(parameters: dict, player=None, speak=None) -> str:
    """
    Modulo de accesibilidad universal.
    """
    action = parameters.get("action", "").strip().lower()
    text = parameters.get("text", "").strip()
    format_type = parameters.get("format", "steps").strip().lower()
    name = parameters.get("name", "").strip()
    setting = parameters.get("setting", "").strip()
    value = parameters.get("value", "").strip()
    level = parameters.get("level", None)
    stress_level = parameters.get("stress_level", None)

    if not action:
        return "[ERROR] Falta el parametro obligatorio 'action'."

    if action not in ALLOWED_ACC_ACTIONS:
        return f"[ERROR] Accion '{action}' no reconocida para el modulo de accesibilidad."

    # --- 1. VALIDACION DE RANGOS ---
    if level is not None:
        try:
            val_lvl = float(level)
            if not (0.1 <= val_lvl <= 1.0):
                return "[ERROR] El nivel de tolerancia/sensibilidad debe estar entre 0.1 y 1.0."
        except ValueError:
            return "[ERROR] El parametro 'level' debe ser un numero decimal valido."

    if stress_level is not None:
        try:
            val_str = float(stress_level)
            if not (0.0 <= val_str <= 1.0):
                return "[ERROR] El nivel de estres estimado debe estar entre 0.0 y 1.0."
        except ValueError:
            return "[ERROR] El parametro 'stress_level' debe ser un numero decimal valido."

    # Sanitizar entrada de texto
    if text and ("<script" in text.lower() or "javascript:" in text.lower()):
        return "[ERROR] El texto provisto contiene elementos de script no permitidos."

    # --- 2. LOGICA POR ACCION ---
    if action == "task_simplify":
        if not text:
            return "[ERROR] Falta el parametro 'text' para simplificar."
        # Simular descomposicion en pasos
        steps = (
            f"[INFO] Tarea simplificada ({format_type}):\n"
            f"  Paso 1: Identificar el objetivo principal.\n"
            f"  Paso 2: Dividir el trabajo en tres partes de 15 minutos.\n"
            f"  Paso 3: Tomar un descanso de 5 minutos al finalizar cada parte."
        )
        return steps

    elif action == "speech_config":
        sens = level if level is not None else 0.5
        return f"[OK] Sensibilidad del reconocimiento de voz configurada a {sens}."

    elif action == "routine":
        routine_name = name if name else "Rutina Matutina"
        return f"[OK] Rutina '{routine_name}': Progreso guardado, racha incrementada."

    elif action == "emotional":
        stress = stress_level if stress_level is not None else 0.3
        return (
            f"[INFO] Intervención Emocional Activa (Estrés: {stress}):\n"
            f"  Inicie ejercicio de respiracion guiado: Inhale durante 4 segundos, retenga 4, exhale 4. Repita 3 veces."
        )

    elif action in ["eye_tracking", "micro_movement"]:
        return f"[OK] Control asistido por '{action}' activado usando la webcam."

    elif action == "config":
        return f"[INFO] Configuraciones de accesibilidad actuales: Contraste: Alto, Lupa: Apagada, Voz: Habilitada."

    else:
        return f"[OK] Accion '{action}' ejecutada en accesibilidad."
