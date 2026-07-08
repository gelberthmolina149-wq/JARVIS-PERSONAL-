import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 10) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/windows_settings.py",
    "actions/system_monitor.py",
    "actions/smart_home.py"
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
    from actions.windows_settings import windows_settings
    print("  [OK] windows_settings importado.")
except Exception as e:
    print(f"  [FAIL] Import windows_settings: {e}")

try:
    from actions.system_monitor import system_monitor
    print("  [OK] system_monitor importado.")
except Exception as e:
    print(f"  [FAIL] Import system_monitor: {e}")

try:
    from actions.smart_home import smart_home
    print("  [OK] smart_home importado.")
except Exception as e:
    print(f"  [FAIL] Import smart_home: {e}")

# 3. Execution Verification (windows_settings)
print("\n--- 3. Pruebas de Seguridad (windows_settings) ---")
try:
    # Test volume/brightness limits
    r_bright_ok = windows_settings({"action": "set_brightness", "value": "80"})
    r_bright_err = windows_settings({"action": "set_brightness", "value": "150"})
    r_bright_nan = windows_settings({"action": "set_brightness", "value": "not-a-number"})
    
    print(f"  [set_brightness - OK] {r_bright_ok}")
    print(f"  [set_brightness - Fuera de rango] {r_bright_err}")
    print(f"  [set_brightness - No numerico] {r_bright_nan}")

    # Test environment variable constraints
    r_env_blocked = windows_settings({"action": "set_env", "name": "PATH", "value": "C:\\badpath"})
    r_env_ok = windows_settings({"action": "set_env", "name": "JARVIS_TEST_VAR", "value": "safe_val"})
    r_env_get = windows_settings({"action": "get_env", "name": "JARVIS_TEST_VAR"})
    r_env_del = windows_settings({"action": "delete_env", "name": "JARVIS_TEST_VAR"})
    
    print(f"  [set_env - Bloqueo Critico] {r_env_blocked}")
    print(f"  [set_env - Exitoso] {r_env_ok}")
    print(f"  [get_env] {r_env_get}")
    print(f"  [delete_env] {r_env_del}")

    # Test wallpaper path safety
    r_wall_unsafe = windows_settings({"action": "set_wallpaper", "path": "C:\\Windows\\System32\\cmd.exe"})
    print(f"  [set_wallpaper - Insegura] {r_wall_unsafe}")

except Exception as e:
    print(f"  [windows_settings] FAIL: {e}")

# 4. Execution Verification (system_monitor)
print("\n--- 4. Pruebas de Seguridad (system_monitor) ---")
try:
    # Test CPU and RAM info
    r_cpu = system_monitor({"action": "cpu"})
    r_ram = system_monitor({"action": "ram"})
    print(f"  [cpu] {r_cpu}")
    print(f"  [ram] {r_ram}")

    # Test process kill block lists (explorer.exe, PID 4, etc.)
    r_kill_critical = system_monitor({"action": "kill", "name": "explorer.exe"})
    r_kill_critical_pid = system_monitor({"action": "kill", "name": "4"})
    r_kill_normal = system_monitor({"action": "kill", "name": "non_existent_mock_process_999"})
    
    print(f"  [kill - Bloqueo critico por nombre] {r_kill_critical}")
    print(f"  [kill - Bloqueo critico por PID] {r_kill_critical_pid}")
    print(f"  [kill - Simulado normal] {r_kill_normal}")

except Exception as e:
    print(f"  [system_monitor] FAIL: {e}")

# 5. Execution Verification (smart_home)
print("\n--- 5. Pruebas de Seguridad (smart_home) ---")
try:
    # Test color validation (Hex and Names)
    r_color_hex = smart_home({"action": "color", "device": "sala", "color": "#00ff00"})
    r_color_name = smart_home({"action": "color", "device": "sala", "color": "azul"})
    r_color_invalid = smart_home({"action": "color", "device": "sala", "color": "inyeccion; rm -rf"})
    
    print(f"  [color - Hex OK] {r_color_hex}")
    print(f"  [color - Nombre OK] {r_color_name}")
    print(f"  [color - Invalido/Inyección] {r_color_invalid}")

    # Test bounds on brightness
    r_bright_ok = smart_home({"action": "brightness", "device": "cuarto", "brightness": 75})
    r_bright_bad = smart_home({"action": "brightness", "device": "cuarto", "brightness": 9999})
    
    print(f"  [brightness - OK] {r_bright_ok}")
    print(f"  [brightness - Invalido] {r_bright_bad}")

    # Test setup action instructions
    r_setup = smart_home({"action": "setup"})
    print(f"  [setup]\n{r_setup}")

except Exception as e:
    print(f"  [smart_home] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # Test routing for windows_settings
        res_ws = await mgr.dispatch("windows_settings", {"action": "info"}, ui=None)
        print(f"  [Manager -> windows_settings] Ruteado: '{res_ws.splitlines()[0]}'")

        # Test routing for system_monitor
        res_sm = await mgr.dispatch("system_monitor", {"action": "report"}, ui=None)
        print(f"  [Manager -> system_monitor] Ruteado: '{res_sm.splitlines()[0]}'")

        # Test routing for smart_home
        res_sh = await mgr.dispatch("smart_home", {"action": "list"}, ui=None)
        print(f"  [Manager -> smart_home] Ruteado: '{res_sh.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
