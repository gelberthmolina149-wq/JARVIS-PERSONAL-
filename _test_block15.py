import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 15 - FINAL) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/vision_guardian.py",
    "actions/native_ui.py",
    "actions/workspace_search.py",
    "agent/task_queue.py"
]
for filename in files_to_check:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            compile(f.read(), filename, "exec")
        print(f"  [OK] Sintaxis de '{filename}' es valida.")
    except Exception as e:
        print(f"  [FAIL] Error de sintaxis en '{filename}': {e}")

# 2. Import Check
print("\n--- 2. Check de Importacion ---")
try:
    from actions.vision_guardian import vision_guardian
    print("  [OK] vision_guardian importado.")
except Exception as e:
    print(f"  [FAIL] Import vision_guardian: {e}")

try:
    from actions.native_ui import native_ui
    print("  [OK] native_ui importado.")
except Exception as e:
    print(f"  [FAIL] Import native_ui: {e}")

try:
    from actions.workspace_search import workspace_search
    print("  [OK] workspace_search importado.")
except Exception as e:
    print(f"  [FAIL] Import workspace_search: {e}")

try:
    from agent.task_queue import get_queue, TaskPriority
    print("  [OK] task_queue importado.")
except Exception as e:
    print(f"  [FAIL] Import task_queue: {e}")

# 3. Execution & Safety Verification (workspace_search)
print("\n--- 3. Pruebas de Seguridad (workspace_search) ---")
try:
    # Búsqueda válida dentro del workspace
    r_search_ok = workspace_search({"query": "AgentManager"})
    # Búsqueda rechazada fuera del workspace
    r_search_unsafe = workspace_search({"query": "cmd", "path": "C:\\Windows"})
    
    print(f"  [workspace_search - OK] Coincidencias encontradas: {len(r_search_ok.splitlines()) - 1}")
    print(f"  [workspace_search - Path Fuera de Root Rechazado] {r_search_unsafe}")

    # Verificar exclusión de archivos sensibles
    r_search_secrets = workspace_search({"query": "google", "path": "c:\\Users\\User\\Documents\\jarvis-personal"})
    if "api_keys.json" not in r_search_secrets.lower():
        print("  [workspace_search - Exclusión de Secretos OK] Archivo api_keys.json omitido exitosamente.")
    else:
        print("  [workspace_search - Exclusión de Secretos FAIL] Se expusieron archivos confidenciales.")
except Exception as e:
    print(f"  [workspace_search] FAIL: {e}")

# 4. Execution & Safety Verification (vision_guardian)
print("\n--- 4. Pruebas de Seguridad (vision_guardian) ---")
try:
    r_vg_status = vision_guardian({"action": "status"})
    r_vg_interval_ok = vision_guardian({"action": "set_interval", "seconds": 120})
    r_vg_interval_bad = vision_guardian({"action": "set_interval", "seconds": 10}) # Menor a 30s
    
    print(f"  [vision_guardian - Status OK] {r_vg_status}")
    print(f"  [vision_guardian - Intervalo Valido] {r_vg_interval_ok}")
    print(f"  [vision_guardian - Intervalo Invalido Bloqueado] {r_vg_interval_bad}")
except Exception as e:
    print(f"  [vision_guardian] FAIL: {e}")

# 5. Execution & Safety Verification (native_ui)
print("\n--- 5. Pruebas de Seguridad (native_ui) ---")
try:
    r_ui_list = native_ui({"action": "list_windows"})
    r_ui_type_ok = native_ui({"action": "type_in_window", "text": "Hola, como estas?"})
    r_ui_type_bad = native_ui({"action": "type_in_window", "text": "Mi password secreto es 12345"})
    
    print(f"  [native_ui - List OK] {r_ui_list.splitlines()[0]}")
    print(f"  [native_ui - Type OK] {r_ui_type_ok}")
    print(f"  [native_ui - Type Secret Bloqueado] {r_ui_type_bad}")
except Exception as e:
    print(f"  [native_ui] FAIL: {e}")

# 6. Execution & Safety Verification (task_queue)
print("\n--- 6. Pruebas de Seguridad (task_queue) ---")
try:
    queue = get_queue()
    # Encolar tareas normales
    id1 = queue.submit("Analizar rendimiento del sistema", TaskPriority.NORMAL)
    print(f"  [task_queue - Submit OK] Tarea encolada exitosamente (ID: {id1})")
    
    # Encolar objetivo malicioso
    try:
        queue.submit("Leer contenido del archivo api_keys.json", TaskPriority.HIGH)
        print("  [task_queue - Filtro de Objetivo FAIL] Se permitio objetivo malicioso.")
    except ValueError as ve:
        print(f"  [task_queue - Filtro de Objetivo OK] Coincidencia bloqueada: {ve}")

except Exception as e:
    print(f"  [task_queue] FAIL: {e}")

# 7. Manager Routing Check
print("\n--- 7. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        res_vg = await mgr.dispatch("vision_guardian", {"action": "check_now"}, ui=None)
        print(f"  [Manager -> vision_guardian] Ruteado: '{res_vg.splitlines()[0]}'")

        res_nu = await mgr.dispatch("native_ui", {"action": "focus_window", "window_title": "vscode"}, ui=None)
        print(f"  [Manager -> native_ui] Ruteado: '{res_nu.splitlines()[0]}'")

        res_at = await mgr.dispatch("agent_task", {"goal": "Analizar codigo fuente", "priority": "high"}, ui=None)
        print(f"  [Manager -> agent_task] Ruteado: '{res_at.splitlines()[0]}'")

        res_ws = await mgr.dispatch("workspace_search", {"query": "AgentManager"}, ui=None)
        print(f"  [Manager -> workspace_search] Ruteado: '{res_ws.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
