import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 13) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/accessibility.py",
    "actions/accessibility_overlay.py",
    "actions/camera_bus.py",
    "actions/jarvis_ui_control.py"
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
    from actions.accessibility import accessibility
    print("  [OK] accessibility importado.")
except Exception as e:
    print(f"  [FAIL] Import accessibility: {e}")

try:
    from actions.accessibility_overlay import accessibility_overlay
    print("  [OK] accessibility_overlay importado.")
except Exception as e:
    print(f"  [FAIL] Import accessibility_overlay: {e}")

try:
    from actions.camera_bus import camera_bus
    print("  [OK] camera_bus importado.")
except Exception as e:
    print(f"  [FAIL] Import camera_bus: {e}")

try:
    from actions.jarvis_ui_control import jarvis_ui_control
    print("  [OK] jarvis_ui_control importado.")
except Exception as e:
    print(f"  [FAIL] Import jarvis_ui_control: {e}")

# 3. Execution & Safety Verification (accessibility)
print("\n--- 3. Pruebas de Seguridad (accessibility) ---")
try:
    r_acc_ok = accessibility({"action": "speech_config", "level": 0.8})
    r_acc_bad_lvl = accessibility({"action": "speech_config", "level": 5.0})
    r_acc_bad_str = accessibility({"action": "emotional", "stress_level": -1.2})
    r_acc_unsafe_text = accessibility({"action": "task_simplify", "text": "hacked <script>alert(1)</script>"})
    
    print(f"  [accessibility - OK] {r_acc_ok}")
    print(f"  [accessibility - Level Bounds Blocked] {r_acc_bad_lvl}")
    print(f"  [accessibility - Stress Bounds Blocked] {r_acc_bad_str}")
    print(f"  [accessibility - Script Blocked] {r_acc_unsafe_text}")
except Exception as e:
    print(f"  [accessibility] FAIL: {e}")

# 4. Execution & Safety Verification (accessibility_overlay)
print("\n--- 4. Pruebas de Seguridad (accessibility_overlay) ---")
try:
    r_overlay_ok = accessibility_overlay({"action": "show"})
    r_overlay_bad = accessibility_overlay({"action": "hacked_action"})
    
    print(f"  [accessibility_overlay - OK] {r_overlay_ok}")
    print(f"  [accessibility_overlay - Blocked] {r_overlay_bad}")
except Exception as e:
    print(f"  [accessibility_overlay] FAIL: {e}")

# 5. Execution & Safety Verification (camera_bus)
print("\n--- 5. Pruebas de Seguridad (camera_bus) ---")
try:
    r_cam_ok = camera_bus({"action": "enable"})
    r_cam_bad = camera_bus({"action": "hacked_cam"})
    
    print(f"  [camera_bus - OK/Hardware Check] {r_cam_ok}")
    print(f"  [camera_bus - Blocked] {r_cam_bad}")
except Exception as e:
    print(f"  [camera_bus] FAIL: {e}")

# 6. Execution & Safety Verification (jarvis_ui_control)
print("\n--- 6. Pruebas de Seguridad (jarvis_ui_control) ---")
try:
    r_ui_ok = jarvis_ui_control({"action": "show", "widget": "weather"})
    r_ui_bad_widget = jarvis_ui_control({"action": "show", "widget": "malicious_widget"})
    r_ui_bad_action = jarvis_ui_control({"action": "eval_code", "widget": "weather"})
    
    print(f"  [jarvis_ui_control - OK] {r_ui_ok}")
    print(f"  [jarvis_ui_control - Widget Blocked] {r_ui_bad_widget}")
    print(f"  [jarvis_ui_control - Action Blocked] {r_ui_bad_action}")
except Exception as e:
    print(f"  [jarvis_ui_control] FAIL: {e}")

# 7. Manager Routing Check
print("\n--- 7. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        res_ac = await mgr.dispatch("accessibility", {"action": "config"}, ui=None)
        print(f"  [Manager -> accessibility] Ruteado: '{res_ac.splitlines()[0]}'")

        res_ao = await mgr.dispatch("accessibility_overlay", {"action": "status"}, ui=None)
        print(f"  [Manager -> accessibility_overlay] Ruteado: '{res_ao.splitlines()[0]}'")

        res_cb = await mgr.dispatch("camera_bus", {"action": "disable"}, ui=None)
        print(f"  [Manager -> camera_bus] Ruteado: '{res_cb.splitlines()[0]}'")

        res_ui = await mgr.dispatch("jarvis_ui_control", {"action": "hide_all"}, ui=None)
        print(f"  [Manager -> jarvis_ui_control] Ruteado: '{res_ui.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
