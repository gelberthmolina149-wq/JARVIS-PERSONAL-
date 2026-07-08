import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 14) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/document_creator.py",
    "actions/document_manager.py",
    "actions/file_processor.py",
    "actions/codebase.py"
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
    from actions.document_creator import document_creator
    print("  [OK] document_creator importado.")
except Exception as e:
    print(f"  [FAIL] Import document_creator: {e}")

try:
    from actions.document_manager import document_manager
    print("  [OK] document_manager importado.")
except Exception as e:
    print(f"  [FAIL] Import document_manager: {e}")

try:
    from actions.file_processor import file_processor
    print("  [OK] file_processor importado.")
except Exception as e:
    print(f"  [FAIL] Import file_processor: {e}")

try:
    from actions.codebase import codebase
    print("  [OK] codebase importado.")
except Exception as e:
    print(f"  [FAIL] Import codebase: {e}")

# 3. Execution & Safety Verification (document_creator)
print("\n--- 3. Pruebas de Seguridad (document_creator) ---")
try:
    r_doc_ok = document_creator({"action": "word", "title": "informe_mensual", "content": "Metricas de venta"})
    r_doc_path_unsafe = document_creator({"action": "word", "title": "informe", "save_path": "C:\\Windows\\System32\\bad.docx"})
    r_doc_ext_bad = document_creator({"action": "word", "title": "informe", "save_path": "c:\\Users\\User\\Documents\\jarvis-personal\\informe.xlsx"})
    
    print(f"  [document_creator - OK] {r_doc_ok}")
    print(f"  [document_creator - Path Traversal Blocked] {r_doc_path_unsafe}")
    print(f"  [document_creator - Extension Check] {r_doc_ext_bad}")
except Exception as e:
    print(f"  [document_creator] FAIL: {e}")

# 4. Execution & Safety Verification (document_manager)
print("\n--- 4. Pruebas de Seguridad (document_manager) ---")
try:
    r_mgr_info = document_manager({"action": "info", "path": "c:\\Users\\User\\Documents\\jarvis-personal\\README.md"})
    r_mgr_unsafe = document_manager({"action": "info", "path": "C:\\Windows\\System32\\cmd.exe"})
    
    print(f"  [document_manager - Info OK] {r_mgr_info.splitlines()[0]}")
    print(f"  [document_manager - Path Traversal Blocked] {r_mgr_unsafe}")
except Exception as e:
    print(f"  [document_manager] FAIL: {e}")

# 5. Execution & Safety Verification (file_processor)
print("\n--- 5. Pruebas de Seguridad (file_processor) ---")
try:
    r_proc_ok = file_processor({"action": "summarize", "file_path": "c:\\Users\\User\\Documents\\jarvis-personal\\README.md"})
    r_proc_unsafe = file_processor({"action": "summarize", "file_path": "C:\\Windows\\System32\\cmd.exe"})
    
    # Crear un archivo de prueba grande (11MB) para verificar el limite DoS
    test_large_path = "c:\\Users\\User\\Documents\\jarvis-personal\\test_large_file.txt"
    try:
        with open(test_large_path, "wb") as f:
            f.write(b"\0" * (11 * 1024 * 1024))
        r_proc_large = file_processor({"action": "summarize", "file_path": test_large_path})
        print(f"  [file_processor - DoS Limit Blocked] {r_proc_large}")
    finally:
        if os.path.exists(test_large_path):
            os.remove(test_large_path)
            
    print(f"  [file_processor - OK] {r_proc_ok}")
    print(f"  [file_processor - Path Blocked] {r_proc_unsafe}")
except Exception as e:
    print(f"  [file_processor] FAIL: {e}")

# 6. Execution & Safety Verification (codebase)
print("\n--- 6. Pruebas de Seguridad (codebase) ---")
try:
    r_cb_index = codebase({"action": "index", "path": "c:\\Users\\User\\Documents\\jarvis-personal"})
    r_cb_unsafe = codebase({"action": "index", "path": "C:\\Windows"})
    
    print(f"  [codebase - Index OK] {r_cb_index}")
    print(f"  [codebase - Sandbox Blocked] {r_cb_unsafe}")
except Exception as e:
    print(f"  [codebase] FAIL: {e}")

# 7. Manager Routing Check
print("\n--- 7. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        res_dc = await mgr.dispatch("document_creator", {"action": "word", "title": "test"}, ui=None)
        print(f"  [Manager -> document_creator] Ruteado: '{res_dc.splitlines()[0]}'")

        res_dm = await mgr.dispatch("document_manager", {"action": "info", "path": "c:\\Users\\User\\Documents\\jarvis-personal\\README.md"}, ui=None)
        print(f"  [Manager -> document_manager] Ruteado: '{res_dm.splitlines()[0]}'")

        res_fp = await mgr.dispatch("file_processor", {"action": "summarize", "file_path": "c:\\Users\\User\\Documents\\jarvis-personal\\README.md"}, ui=None)
        print(f"  [Manager -> file_processor] Ruteado: '{res_fp.splitlines()[0]}'")

        res_cb = await mgr.dispatch("codebase", {"action": "list"}, ui=None)
        print(f"  [Manager -> codebase] Ruteado: '{res_cb.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
