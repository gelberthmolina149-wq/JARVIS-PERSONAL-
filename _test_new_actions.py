import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, '.')

print("=== VERIFICACION DE NUEVAS ACCIONES ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
for filename in ["actions/browser_control.py", "actions/file_controller.py"]:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            ast = compile(f.read(), filename, "exec")
        print(f"  [OK] Sintaxis de '{filename}' es valida.")
    except Exception as e:
        print(f"  [FAIL] Error de sintaxis en '{filename}': {e}")

# 2. Import Check
print("\n--- 2. Check de Importacion ---")
try:
    from actions.browser_control import browser_control
    print("  [OK] browser_control importado exitosamente.")
except Exception as e:
    print(f"  [FAIL] Error al importar browser_control: {e}")

try:
    from actions.file_controller import file_controller
    print("  [OK] file_controller importado exitosamente.")
except Exception as e:
    print(f"  [FAIL] Error al importar file_controller: {e}")

# 3. Mock Execution tests
print("\n--- 3. Pruebas de Ejecucion Mock (browser_control) ---")
try:
    # go_to con url invalido (debe gatillar seguridad o resolucion)
    r_bad_url = browser_control({"action": "go_to", "url": "ftp://malicious-site.com"})
    print(f"  [browser_control - Bad URL Security] {r_bad_url}")
    
    # search query
    r_search = browser_control({"action": "search", "query": "unit test mock"})
    print(f"  [browser_control - Search] {r_search}")
except Exception as e:
    print(f"  [browser_control] FAIL: {e}")

print("\n--- 4. Pruebas de Ejecucion (file_controller) ---")
try:
    test_file = Path("test_mock_file.txt").resolve()
    
    # Escribir
    r_write = file_controller({"action": "write", "path": str(test_file), "content": "Prueba de JARVIS\nLinea de control"})
    print(f"  [file_controller - Write] {r_write}")
    
    # Info
    r_info = file_controller({"action": "info", "path": str(test_file)})
    print(f"  [file_controller - Info] {r_info.strip()}")
    
    # Leer
    r_read = file_controller({"action": "read", "path": str(test_file)})
    print(f"  [file_controller - Read] Contenido: '{r_read.strip()}'")

    # Buscar
    r_find = file_controller({"action": "find", "path": ".", "name": "test_mock_file"})
    print(f"  [file_controller - Find] {r_find.strip()}")
    
    # Borrado seguro con confirmacion
    r_del_warn = file_controller({"action": "delete", "path": str(test_file), "confirm": False})
    print(f"  [file_controller - Delete warning] {r_del_warn.strip()}")
    
    r_del_ok = file_controller({"action": "delete", "path": str(test_file), "confirm": True})
    print(f"  [file_controller - Delete confirm] {r_del_ok.strip()}")

    # Validacion path traversal (seguridad)
    r_traversal = file_controller({"action": "read", "path": "C:\\Windows\\System32\\drivers\\etc\\hosts"})
    print(f"  [file_controller - Security Traversal Block] {r_traversal}")
except Exception as e:
    print(f"  [file_controller] FAIL: {e}")

# 4. Manager Routing Check
print("\n--- 5. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # Dispatch browser_control mock search
        res_browser = await mgr.dispatch("browser_control", {"action": "search", "query": "JARVIS assistant"}, ui=None)
        print(f"  [Manager -> browser_control] Ruteado: {res_browser}")
        
        # Dispatch file_controller mock list
        res_file = await mgr.dispatch("file_controller", {"action": "list", "path": "."}, ui=None)
        print(f"  [Manager -> file_controller] Ruteado: {res_file.splitlines()[0]}")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
