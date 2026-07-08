import sys
import os
import asyncio
from pathlib import Path

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 3) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/whatsapp.py",
    "actions/send_message.py",
    "actions/reminder.py"
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
    from actions.whatsapp import whatsapp
    print("  [OK] whatsapp importado.")
except Exception as e:
    print(f"  [FAIL] Import whatsapp: {e}")

try:
    from actions.send_message import send_message
    print("  [OK] send_message importado.")
except Exception as e:
    print(f"  [FAIL] Import send_message: {e}")

try:
    from actions.reminder import reminder
    print("  [OK] reminder importado.")
except Exception as e:
    print(f"  [FAIL] Import reminder: {e}")

# 3. Execution Verification (whatsapp)
print("\n--- 3. Pruebas de Ejecucion Mock (whatsapp) ---")
try:
    # Agregar contacto
    r_add = whatsapp({"action": "add_contact", "name": "Test Contact", "phone": "+5491155551234"})
    print(f"  [whatsapp - Add Contact] {r_add}")

    # Listar contactos
    r_list = whatsapp({"action": "list_contacts"})
    print(f"  [whatsapp - List Contacts] {r_list}")

    # Borrar contacto
    r_del = whatsapp({"action": "delete_contact", "name": "Test Contact"})
    print(f"  [whatsapp - Delete Contact] {r_del}")
except Exception as e:
    print(f"  [whatsapp] FAIL: {e}")

# 4. Execution Verification (send_message)
print("\n--- 4. Pruebas de Ejecucion Mock (send_message) ---")
try:
    # Discord bad webhook scheme check
    r_discord_bad = send_message({"receiver": "http://bad-webhook.com", "message_text": "Hello", "platform": "discord"})
    print(f"  [send_message - Discord Webhook Check] {r_discord_bad}")

    # Telegram missing keys check
    r_tele_bad = send_message({"receiver": "12345", "message_text": "Hello", "platform": "telegram"})
    print(f"  [send_message - Telegram Config Check] {r_tele_bad}")
except Exception as e:
    print(f"  [send_message] FAIL: {e}")

# 5. Execution Verification (reminder)
print("\n--- 5. Pruebas de Ejecucion Mock (reminder) ---")
try:
    # Formatos de fecha validos pero pasada
    r_past = reminder({"date": "2020-01-01", "time": "12:00", "message": "Past test"})
    print(f"  [reminder - Past Block] {r_past}")

    # Sanitizacion de caracteres especiales
    import datetime
    future_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    r_special = reminder({"date": future_date, "time": "15:00", "message": "Recordatorio hack: && rm -rf / ; msg *"})
    print(f"  [reminder - Sanitization Output] {r_special}")
except Exception as e:
    print(f"  [reminder] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # WhatsApp ruteado a CLOUD
        res_wa = await mgr.dispatch("whatsapp", {"action": "list_contacts"}, ui=None)
        print(f"  [Manager -> whatsapp] Ruteado: '{res_wa}'")

        # send_message ruteado a CLOUD
        res_msg = await mgr.dispatch("send_message", {"receiver": "web", "message_text": "hi", "platform": "signal"}, ui=None)
        print(f"  [Manager -> send_message] Ruteado: '{res_msg}'")

        # reminder ruteado a CLOUD
        res_rem = await mgr.dispatch("reminder", {"date": "2020-01-01", "time": "12:00", "message": "test"}, ui=None)
        print(f"  [Manager -> reminder] Ruteado: '{res_rem}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
