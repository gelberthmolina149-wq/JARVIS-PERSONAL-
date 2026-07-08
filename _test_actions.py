import sys
sys.path.insert(0, '.')

print("=== PASO 3: Mock Execution Test ===")

# open_app
from actions.open_app import open_app
try:
    r = open_app({'app_name': 'notepad'}, player=None)
    status = "PASS" if isinstance(r, str) and len(r) > 0 else "FAIL"
    print(f"  [open_app] {status}: {r}")
except Exception as e:
    print(f"  [open_app] FAIL: {e}")

# computer_settings - status (solo lectura)
from actions.computer_settings import computer_settings
try:
    r = computer_settings({'action': 'status'}, player=None)
    status = "PASS" if isinstance(r, str) and len(r) > 0 else "FAIL"
    print(f"  [computer_settings] {status}: {r[:100]}")
except Exception as e:
    print(f"  [computer_settings] FAIL: {e}")

# weather_report
from actions.weather_report import weather_action
try:
    r = weather_action({'city': 'Lima'}, player=None)
    status = "PASS" if isinstance(r, str) and len(r) > 5 else "FAIL"
    print(f"  [weather_report] {status}: {r[:120]}")
except Exception as e:
    print(f"  [weather_report] FAIL: {e}")

# web_search
from actions.web_search import web_search
try:
    r = web_search({'query': 'clima Lima Peru', 'mode': 'search'}, player=None)
    status = "PASS" if isinstance(r, str) and len(r) > 10 else "FAIL"
    print(f"  [web_search] {status}: {r[:120]}")
except Exception as e:
    print(f"  [web_search] FAIL: {e}")

print("\nPaso 3 completado.")
