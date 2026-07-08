import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 7) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/google_drive.py",
    "actions/gmail_control.py",
    "actions/arca_invoice.py"
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
    from actions.google_drive import google_drive
    print("  [OK] google_drive importado.")
except Exception as e:
    print(f"  [FAIL] Import google_drive: {e}")

try:
    from actions.gmail_control import gmail_control
    print("  [OK] gmail_control importado.")
except Exception as e:
    print(f"  [FAIL] Import gmail_control: {e}")

try:
    from actions.arca_invoice import arca_invoice
    print("  [OK] arca_invoice importado.")
except Exception as e:
    print(f"  [FAIL] Import arca_invoice: {e}")

# 3. Execution Verification (google_drive)
print("\n--- 3. Pruebas de Ejecucion Mock (google_drive) ---")
try:
    # Local path safety check (upload blocks credential files)
    r_up_sec = google_drive({"action": "upload", "path": "config/api_keys.example.json"})
    print(f"  [google_drive - Security Key Block] {r_up_sec}")

    # Fallback to OAuth missing keys
    r_drive_fail = google_drive({"action": "list"})
    print(f"  [google_drive - Setup Fallback Check] {r_drive_fail.splitlines()[0]}")
except Exception as e:
    print(f"  [google_drive] FAIL: {e}")

# 4. Execution Verification (gmail_control)
print("\n--- 4. Pruebas de Ejecucion Mock (gmail_control) ---")
try:
    # HTML sanitization / clean MIME builder check
    from actions.gmail_control import build_message
    msg_mime = build_message("dest@test.com", "Alert", "Hello <script>alert(1)</script>")
    print(f"  [gmail_control - HTML Escape Check] Raw present: {len(msg_mime.get('raw', '')) > 0}")

    # Fallback warning check
    r_gmail_fail = gmail_control({"action": "inbox"})
    print(f"  [gmail_control - Setup Fallback Check] {r_gmail_fail.splitlines()[0]}")
except Exception as e:
    print(f"  [gmail_control] FAIL: {e}")

# 5. Execution Verification (arca_invoice)
print("\n--- 5. Pruebas de Ejecucion Mock (arca_invoice) ---")
try:
    # List invoices
    r_list = arca_invoice({"action": "list"})
    print(f"  [arca_invoice - List] {r_list.splitlines()[0]}")

    # Download safety check (out of bounds directory blocked)
    r_down_sec = arca_invoice({"action": "download", "invoice_id": "FC-00124", "destination_folder": "C:\\Windows\\System32"})
    print(f"  [arca_invoice - Safety Path Blocked] {r_down_sec}")
except Exception as e:
    print(f"  [arca_invoice] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # google_drive ruteado a CLOUD
        res_drv = await mgr.dispatch("google_drive", {"action": "list"}, ui=None)
        print(f"  [Manager -> google_drive] Ruteado: '{res_drv.splitlines()[0]}'")

        # gmail_control ruteado a CLOUD
        res_gml = await mgr.dispatch("gmail_control", {"action": "inbox"}, ui=None)
        print(f"  [Manager -> gmail_control] Ruteado: '{res_gml.splitlines()[0]}'")

        # arca_invoice ruteado a CLOUD
        res_arc = await mgr.dispatch("arca_invoice", {"action": "list"}, ui=None)
        print(f"  [Manager -> arca_invoice] Ruteado: '{res_arc.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
