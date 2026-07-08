import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 4) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/code_helper.py",
    "actions/git_control.py",
    "actions/knowledge_base.py"
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
    from actions.code_helper import code_helper
    print("  [OK] code_helper importado.")
except Exception as e:
    print(f"  [FAIL] Import code_helper: {e}")

try:
    from actions.git_control import git_control
    print("  [OK] git_control importado.")
except Exception as e:
    print(f"  [FAIL] Import git_control: {e}")

try:
    from actions.knowledge_base import knowledge_base
    print("  [OK] knowledge_base importado.")
except Exception as e:
    print(f"  [FAIL] Import knowledge_base: {e}")

# 3. Execution Verification (code_helper)
print("\n--- 3. Pruebas de Ejecucion Mock (code_helper) ---")
try:
    # Action explain
    r_exp = code_helper({"action": "explain", "code": "def add(a, b): return a + b", "language": "python"})
    print(f"  [code_helper - Explain] {r_exp.splitlines()[0]}")

    # Action run security check (block compiled binaries)
    r_sec = code_helper({"action": "run", "file_path": "c:\\Windows\\explorer.exe"})
    print(f"  [code_helper - Security Check] {r_sec}")
except Exception as e:
    print(f"  [code_helper] FAIL: {e}")

# 4. Execution Verification (git_control)
print("\n--- 4. Pruebas de Ejecucion Mock (git_control) ---")
try:
    # Clone insecure domain check
    r_clone_bad = git_control({"action": "clone", "repo_url": "https://malicious-site.com/repo.git"})
    print(f"  [git_control - Security Clone Block] {r_clone_bad}")
except Exception as e:
    print(f"  [git_control] FAIL: {e}")

# 5. Execution Verification (knowledge_base)
print("\n--- 5. Pruebas de Ejecucion Mock (knowledge_base) ---")
try:
    # Agregar entrada
    r_add = knowledge_base({"action": "add", "topic": "JARVIS Rules", "content": "Keep it safe and clean"})
    print(f"  [knowledge_base - Add] {r_add}")

    # Buscar
    r_search = knowledge_base({"action": "search", "query": "rules"})
    print(f"  [knowledge_base - Search] {r_search}")

    # Limite de contenido excedido
    r_limit = knowledge_base({"action": "add", "topic": "Huge Entry", "content": "A" * 2000})
    print(f"  [knowledge_base - Content Limit Check] {r_limit}")

    # Eliminar
    r_del = knowledge_base({"action": "delete", "entry_id": "jarvis_rules"})
    print(f"  [knowledge_base - Delete] {r_del}")
except Exception as e:
    print(f"  [knowledge_base] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # code_helper ruteado a DEV
        res_code = await mgr.dispatch("code_helper", {"action": "explain", "code": "pass"}, ui=None)
        print(f"  [Manager -> code_helper] Ruteado: '{res_code.splitlines()[0]}'")

        # git_control ruteado a DEV
        res_git = await mgr.dispatch("git_control", {"action": "status"}, ui=None)
        print(f"  [Manager -> git_control] Ruteado: '{res_git.splitlines()[0]}'")

        # knowledge_base ruteado a DEV
        res_kb = await mgr.dispatch("knowledge_base", {"action": "list"}, ui=None)
        print(f"  [Manager -> knowledge_base] Ruteado: '{res_kb.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
