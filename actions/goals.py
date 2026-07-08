"""
actions/goals.py — Gestión y persistencia de objetivos a largo plazo en JARVIS.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any

GOALS_FILE = Path("config/goals.json")
MAX_GOALS = 50

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[goals] {msg}")
    except Exception:
        pass

def load_goals() -> dict[str, dict[str, Any]]:
    """Carga de forma segura los objetivos desde JSON."""
    if not GOALS_FILE.exists():
        GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    try:
        if GOALS_FILE.stat().st_size > 50 * 1024: # Limite a 50KB
            return {}
        with open(GOALS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_goals(goals: dict[str, dict[str, Any]]) -> bool:
    """Guarda de forma segura los objetivos en JSON."""
    try:
        data_str = json.dumps(goals, indent=4, ensure_ascii=False)
        if len(data_str.encode("utf-8")) > 50 * 1024:
            return False
        with open(GOALS_FILE, "w", encoding="utf-8") as f:
            f.write(data_str)
        return True
    except Exception as e:
        log(f"Error al guardar objetivos: {e}")
        return False

def goals(parameters: dict, player=None, speak=None) -> str:
    """
    Manages long-term objectives: list, add, update, delete.
    """
    action = parameters.get("action", "").lower().strip()
    goal_text = parameters.get("goal_text", "").strip()
    priority = parameters.get("priority", "medium").lower().strip() # low, medium, high
    status = parameters.get("status", "pending").lower().strip() # pending, done
    goal_id = parameters.get("goal_id", "").strip()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    goals_db = load_goals()

    if action == "add":
        if not goal_text:
            return "Error: Para agregar un objetivo se requiere el parametro 'goal_text'."
        
        if len(goals_db) >= MAX_GOALS:
            return f"Error: Se alcanzo el limite maximo de {MAX_GOALS} objetivos registrados."

        # Limitar longitud de texto
        if len(goal_text) > 300:
            goal_text = goal_text[:300]

        # ID unico
        g_id = f"goal_{int(time.time() * 100) % 100000}"
        goals_db[g_id] = {
            "id": g_id,
            "text": goal_text,
            "priority": priority if priority in ["low", "medium", "high"] else "medium",
            "status": status if status in ["pending", "done"] else "pending",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if save_goals(goals_db):
            return f"Objetivo registrado exitosamente (ID: {g_id})."
        else:
            return "Error al guardar el objetivo."

    elif action == "update":
        if not goal_id:
            return "Error: Se requiere 'goal_id' para actualizar."
        
        key = goal_id.lower().strip()
        if key not in goals_db:
            return f"Error: No existe ningun objetivo con el ID '{goal_id}'."

        if goal_text:
            goals_db[key]["text"] = goal_text[:300]
        if priority in ["low", "medium", "high"]:
            goals_db[key]["priority"] = priority
        if status in ["pending", "done"]:
            goals_db[key]["status"] = status

        if save_goals(goals_db):
            return f"Objetivo '{goal_id}' actualizado con exito."
        else:
            return "Error al persistir la actualizacion del objetivo."

    elif action == "delete":
        if not goal_id:
            return "Error: Se requiere 'goal_id' para eliminar."
        
        key = goal_id.lower().strip()
        if key in goals_db:
            del goals_db[key]
            save_goals(goals_db)
            return f"Objetivo '{goal_id}' eliminado con exito."
        return f"El objetivo con ID '{goal_id}' no existe."

    elif action == "list":
        if not goals_db:
            return "No hay objetivos registrados en el sistema."
        
        res = "Objetivos a largo plazo de JARVIS:\n"
        for gid, g in sorted(goals_db.items()):
            symbol = "[x]" if g.get("status") == "done" else "[ ]"
            res += f"  - {symbol} [{gid}] ({g.get('priority').upper()}): {g.get('text')}\n"
        return res.strip()

    else:
        return f"Error: Accion '{action}' no reconocida para goals."
