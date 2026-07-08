"""
actions/workspace_search.py — Buscador global local confinado al workspace.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Any

# Archivos y carpetas sensibles excluidos por defecto
EXCLUDED_NAMES = {
    "api_keys.json", "api_keys.example.json", "long_term.json", "tokens.json",
    ".git", "__pycache__", ".idea", ".vscode", "node_modules", "venv", ".env"
}

def is_safe_path(path: Path) -> bool:
    """Verifica que la ruta viva estrictamente dentro del workspace de jarvis-personal."""
    try:
        resolved = path.resolve()
        workspace = Path("c:/Users/User/Documents/jarvis-personal").resolve()
        # Debe estar dentro del workspace de jarvis-personal
        return workspace in resolved.parents or resolved == workspace
    except Exception:
        return False

def workspace_search(parameters: dict, player=None, speak=None) -> str:
    """
    Realiza una búsqueda de texto global en los archivos del proyecto dentro del workspace.
    Cualquier ruta fuera del root es rechazada. Excluye archivos sensibles por defecto.
    """
    query = parameters.get("query", "").strip()
    path_str = parameters.get("path", "").strip()

    if not query:
        return "[ERROR] Falta el parametro obligatorio 'query'."

    # --- 1. VALIDACION DE RUTA Y CONFINE DEL SANDBOX ---
    search_root = Path("c:/Users/User/Documents/jarvis-personal").resolve()
    if path_str:
        custom_path = Path(path_str).resolve()
        if not is_safe_path(custom_path):
            return f"[ERROR] Acceso denegado: La ruta de busqueda '{path_str}' esta fuera del workspace aprobado."
        search_root = custom_path

    # --- 2. BUSQUEDA CON EXCLUSION DE ARCHIVOS SENSIBLES ---
    matches = []
    query_lower = query.lower()

    try:
        for root, dirs, files in os.walk(search_root):
            # Filtrar carpetas excluidas de forma dinamica en el walk
            dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_NAMES and not d.startswith('.')]
            
            for file in files:
                file_lower = file.lower()
                if file_lower in EXCLUDED_NAMES or file_lower.startswith('.'):
                    continue
                
                # Omitir extensiones binarias comunes
                if file_lower.endswith(('.pyc', '.png', '.jpg', '.jpeg', '.zip', '.tar', '.gz', '.db', '.sqlite')):
                    continue
                
                file_path = Path(root) / file
                
                # Limite de tamano: Max 1MB por archivo para evitar DoS
                try:
                    if file_path.stat().st_size > 1 * 1024 * 1024:
                        continue
                except Exception:
                    continue
                
                # Leer y buscar
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        for line_num, line_content in enumerate(lines, 1):
                            if query_lower in line_content.lower():
                                # Formatear coincidencia relativa al root
                                rel_path = file_path.relative_to(search_root)
                                matches.append((rel_path, line_num, line_content.strip()))
                                # Limite maximo de matches a reportar
                                if len(matches) >= 30:
                                    break
                except Exception:
                    continue
                
                if len(matches) >= 30:
                    break
            if len(matches) >= 30:
                break
                
    except Exception as e:
        return f"[ERROR] Fallo durante la busqueda global: {e}"

    # --- 3. FORMATO DE RESULTADOS ---
    if not matches:
        return f"[INFO] No se encontraron coincidencias para '{query}' dentro del workspace."

    res = f"[OK] Coincidencias encontradas para '{query}' (Mostrando hasta 30 resultados):\n"
    for path, line_no, content in matches:
        # Truncar lineas muy largas
        if len(content) > 100:
            content = content[:97] + "..."
        res += f"  - {path}:{line_no} -> {content}\n"
        
    return res
