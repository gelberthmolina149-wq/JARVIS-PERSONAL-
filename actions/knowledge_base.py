"""
actions/knowledge_base.py — Base de conocimiento local simple, persistida en JSON y con limites de seguridad.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

KB_FILE = Path("config/knowledge_base.json")
MAX_ENTRIES = 200          # Limite maximo de entradas
MAX_CONTENT_LEN = 1000     # Limite de longitud por entrada (1KB)
MAX_FILE_SIZE = 100 * 1024 # Limite maximo del archivo (100KB)

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[knowledge_base] {msg}")
    except Exception:
        pass

def load_kb() -> dict[str, dict[str, str]]:
    """Carga de forma segura la base de conocimiento JSON."""
    if not KB_FILE.exists():
        KB_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(KB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    
    # Validar tamaño del archivo antes de leer
    try:
        if KB_FILE.stat().st_size > MAX_FILE_SIZE:
            log("Advertencia: El archivo de base de conocimiento excede el tamano maximo seguro. Recortando...")
            return {}
            
        with open(KB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_kb(kb: dict[str, dict[str, str]]) -> bool:
    """Guarda de forma segura la base de conocimiento JSON."""
    try:
        data_str = json.dumps(kb, indent=4, ensure_ascii=False)
        # Validar tamaño antes de escribir
        if len(data_str.encode("utf-8")) > MAX_FILE_SIZE:
            return False
        with open(KB_FILE, "w", encoding="utf-8") as f:
            f.write(data_str)
        return True
    except Exception as e:
        log(f"Error al guardar base de conocimiento: {e}")
        return False

def knowledge_base(parameters: dict, player=None, speak=None) -> str:
    """
    Manages a simple local knowledge base: search, add, update, delete, list.
    """
    action = parameters.get("action", "").lower().strip()
    query = parameters.get("query", "").strip()
    topic = parameters.get("topic", "").strip()
    content = parameters.get("content", "").strip()
    entry_id = parameters.get("entry_id", "").strip()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    kb = load_kb()

    if action == "add":
        if not topic or not content:
            return "Error: Para agregar una entrada se requiere 'topic' (tema) y 'content' (contenido)."
        
        # Validaciones de límites de tamaño
        if len(kb) >= MAX_ENTRIES:
            return f"Error de capacidad: Se alcanzo el limite maximo de {MAX_ENTRIES} entradas en la base de conocimiento."
        
        if len(content) > MAX_CONTENT_LEN:
            return f"Error: El contenido es demasiado largo. Limite maximo es {MAX_CONTENT_LEN} caracteres."

        # ID de entrada unico incremental o basado en el tema
        topic_key = topic.lower().replace(" ", "_")
        key = topic_key
        suffix = 1
        while key in kb:
            key = f"{topic_key}_{suffix}"
            suffix += 1

        kb[key] = {
            "topic": topic,
            "content": content
        }

        if save_kb(kb):
            return f"Entrada guardada con exito en el tema '{topic}' (ID: '{key}')."
        else:
            return "Error: No se pudo guardar la entrada (exceso de capacidad del archivo)."

    elif action == "update":
        if not entry_id or not content:
            return "Error: Para actualizar una entrada se requiere 'entry_id' y el nuevo 'content'."
        
        key = entry_id.lower().strip()
        if key not in kb:
            return f"Error: No se encontro ninguna entrada con el ID '{entry_id}'."

        if len(content) > MAX_CONTENT_LEN:
            return f"Error: El contenido excede el limite seguro de {MAX_CONTENT_LEN} caracteres."

        kb[key]["content"] = content
        if save_kb(kb):
            return f"Entrada '{entry_id}' actualizada con exito."
        else:
            return "Error al persistir la actualizacion."

    elif action == "delete":
        if not entry_id:
            return "Error: Se requiere 'entry_id' para eliminar la entrada."
        
        key = entry_id.lower().strip()
        if key in kb:
            del kb[key]
            save_kb(kb)
            return f"Entrada '{entry_id}' eliminada con exito."
        return f"La entrada con ID '{entry_id}' no existe."

    elif action == "list":
        if not kb:
            return "La base de conocimiento esta vacia."
        res = "Temas registrados en la base de conocimiento:\n"
        for k, v in sorted(kb.items()):
            res += f"  - [{k}] {v.get('topic')}: {v.get('content')[:80]}...\n"
        return res.strip()

    elif action == "search":
        if not query:
            return "Error: Se requiere un parametro 'query' para buscar."
        
        query_l = query.lower()
        matches = []
        for k, v in kb.items():
            if query_l in k or query_l in v.get("topic", "").lower() or query_l in v.get("content", "").lower():
                matches.append(f"  - [{k}] {v.get('topic')}: {v.get('content')}")
                
        if not matches:
            return f"No se encontraron coincidencias para '{query}'."
        return "Coincidencias encontradas:\n" + "\n".join(matches)

    else:
        return f"Error: Accion '{action}' no reconocida para knowledge_base."
