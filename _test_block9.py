import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 9) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/screen_vision.py",
    "actions/visual_click.py",
    "actions/screen_reader.py"
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
    from actions.screen_vision import screen_vision
    print("  [OK] screen_vision importado.")
except Exception as e:
    print(f"  [FAIL] Import screen_vision: {e}")

try:
    from actions.visual_click import visual_click
    print("  [OK] visual_click importado.")
except Exception as e:
    print(f"  [FAIL] Import visual_click: {e}")

try:
    from actions.screen_reader import screen_reader
    print("  [OK] screen_reader importado.")
except Exception as e:
    print(f"  [FAIL] Import screen_reader: {e}")

# 3. Execution Verification (screen_vision)
print("\n--- 3. Pruebas de Ejecucion Mock (screen_vision) ---")
try:
    r_vis = screen_vision({"text": "analiza el texto de prueba", "angle": "screen"})
    print(f"  [screen_vision - Process] {r_vis.splitlines()[0]}")
except Exception as e:
    print(f"  [screen_vision] FAIL: {e}")

# 4. Execution Verification (visual_click)
print("\n--- 4. Pruebas de Ejecucion Mock (visual_click) ---")
try:
    r_click = visual_click({"element_description": "enviar"})
    print(f"  [visual_click - Click Element] {r_click}")
except Exception as e:
    print(f"  [visual_click] FAIL: {e}")

# 5. Execution Verification (screen_reader)
print("\n--- 5. Pruebas de Ejecucion Mock (screen_reader) ---")
try:
    r_read = screen_reader({"action": "read_all"})
    print(f"  [screen_reader - Filtered Output]:\n{r_read}")
    
    # Comprobar que se hayan filtrado secretos de forma correcta
    if "api_key" not in r_read.lower() and "aizasy" not in r_read.lower():
        print("  [screen_reader - Safety Filter OK] Secretos y llaves de API filtrados con exito.")
    else:
        print("  [screen_reader - Safety Filter FAIL] Secretos expuestos.")
except Exception as e:
    print(f"  [screen_reader] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # screen_vision ruteado a SYSTEM
        res_vis = await mgr.dispatch("screen_vision", {"text": "ver"}, ui=None)
        print(f"  [Manager -> screen_vision] Ruteado: '{res_vis.splitlines()[0]}'")

        # visual_click ruteado a SYSTEM
        res_clk = await mgr.dispatch("visual_click", {"element_description": "enviar"}, ui=None)
        print(f"  [Manager -> visual_click] Ruteado: '{res_clk}'")

        # screen_reader ruteado a SYSTEM
        res_rdr = await mgr.dispatch("screen_reader", {"action": "read_focused"}, ui=None)
        print(f"  [Manager -> screen_reader] Ruteado: '{res_rdr.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
