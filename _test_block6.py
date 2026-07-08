import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 6) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/google_calendar.py",
    "actions/google_maps.py",
    "actions/scheduler.py"
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
    from actions.google_calendar import google_calendar
    print("  [OK] google_calendar importado.")
except Exception as e:
    print(f"  [FAIL] Import google_calendar: {e}")

try:
    from actions.google_maps import google_maps
    print("  [OK] google_maps importado.")
except Exception as e:
    print(f"  [FAIL] Import google_maps: {e}")

try:
    from actions.scheduler import scheduler
    print("  [OK] scheduler importado.")
except Exception as e:
    print(f"  [FAIL] Import scheduler: {e}")

# 3. Execution Verification (google_calendar)
print("\n--- 3. Pruebas de Ejecucion Mock (google_calendar) ---")
try:
    # Auth warning fallback check
    r_cal = google_calendar({"action": "list"})
    print(f"  [google_calendar - Fallback Warning] {r_cal.splitlines()[0]}")
except Exception as e:
    print(f"  [google_calendar] FAIL: {e}")

# 4. Execution Verification (google_maps)
print("\n--- 4. Pruebas de Ejecucion Mock (google_maps) ---")
try:
    # Navigation route URL encoding
    r_maps = google_maps({"origin": "Lima", "destination": "Miraflores", "mode": "walking"})
    print(f"  [google_maps - Route Encoding] {r_maps}")
except Exception as e:
    print(f"  [google_maps] FAIL: {e}")

# 5. Execution Verification (scheduler)
print("\n--- 5. Pruebas de Ejecucion Mock (scheduler) ---")
try:
    # 1. Block command execution automation (terminal_agent)
    r_block_agent = scheduler({"action": "create", "name": "Hack", "task_action": "terminal_agent"})
    print(f"  [scheduler - Terminal Action Blocked] {r_block_agent}")

    # 2. Block low interval (1 min)
    r_block_time = scheduler({"action": "create", "name": "Fast Loop", "task_action": "backup", "frequency": "interval", "interval_minutes": 2})
    print(f"  [scheduler - Frequency Limit Blocked] {r_block_time}")

    # 3. Create normal routine
    r_create = scheduler({"action": "create", "name": "Daily Backup", "task_action": "file_controller"})
    print(f"  [scheduler - Create OK] {r_create}")

    # 4. List
    r_list = scheduler({"action": "list"})
    print(f"  [scheduler - List] {r_list.splitlines()[-1]}")
except Exception as e:
    print(f"  [scheduler] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # google_calendar ruteado a CLOUD
        res_cal = await mgr.dispatch("google_calendar", {"action": "list"}, ui=None)
        print(f"  [Manager -> google_calendar] Ruteado: '{res_cal.splitlines()[0]}'")

        # google_maps ruteado a CLOUD
        res_maps = await mgr.dispatch("google_maps", {"destination": "Lima"}, ui=None)
        print(f"  [Manager -> google_maps] Ruteado: '{res_maps}'")

        # scheduler ruteado a CLOUD
        res_sch = await mgr.dispatch("scheduler", {"action": "list"}, ui=None)
        print(f"  [Manager -> scheduler] Ruteado: '{res_sch.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
