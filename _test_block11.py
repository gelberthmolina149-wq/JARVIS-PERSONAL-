import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 11) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/flight_finder.py",
    "actions/social_media.py",
    "actions/tiktok_analyzer.py",
    "actions/game_updater.py"
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
    from actions.flight_finder import flight_finder
    print("  [OK] flight_finder importado.")
except Exception as e:
    print(f"  [FAIL] Import flight_finder: {e}")

try:
    from actions.social_media import social_media
    print("  [OK] social_media importado.")
except Exception as e:
    print(f"  [FAIL] Import social_media: {e}")

try:
    from actions.tiktok_analyzer import tiktok_analyzer
    print("  [OK] tiktok_analyzer importado.")
except Exception as e:
    print(f"  [FAIL] Import tiktok_analyzer: {e}")

try:
    from actions.game_updater import game_updater
    print("  [OK] game_updater importado.")
except Exception as e:
    print(f"  [FAIL] Import game_updater: {e}")

# 3. Execution & Safety Verification (flight_finder)
print("\n--- 3. Pruebas de Seguridad (flight_finder) ---")
try:
    r_flights_ok = flight_finder({"origin": "LIM", "destination": "MIA", "date": "2026-10-15"})
    r_flights_bad_air = flight_finder({"origin": "LIM; rm -rf", "destination": "MIA", "date": "2026-10-15"})
    r_flights_bad_date = flight_finder({"origin": "LIM", "destination": "MIA", "date": "inject<script>"})
    
    print(f"  [flight_finder - OK] {r_flights_ok.splitlines()[0]}")
    print(f"  [flight_finder - Airport Blocked] {r_flights_bad_air}")
    print(f"  [flight_finder - Date Blocked] {r_flights_bad_date}")
except Exception as e:
    print(f"  [flight_finder] FAIL: {e}")

# 4. Execution & Safety Verification (social_media)
print("\n--- 4. Pruebas de Seguridad (social_media) ---")
try:
    r_sm_tweet = social_media({"platform": "twitter", "action": "tweet", "text": "Hola Mundo!"})
    r_sm_setup = social_media({"platform": "setup", "action": "setup"})
    r_sm_unsafe = social_media({"platform": "twitter", "action": "tweet", "text": "<script>alert(1)</script>"})
    r_sm_img_unsafe = social_media({"platform": "instagram", "action": "post", "image_path": "C:\\Windows\\System32\\cmd.exe"})
    
    print(f"  [social_media - Tweet OK] {r_sm_tweet}")
    print(f"  [social_media - Setup OK] {r_sm_setup.splitlines()[0]}")
    print(f"  [social_media - Script Blocked] {r_sm_unsafe}")
    print(f"  [social_media - Image Safe Check] {r_sm_img_unsafe}")
except Exception as e:
    print(f"  [social_media] FAIL: {e}")

# 5. Execution & Safety Verification (tiktok_analyzer)
print("\n--- 5. Pruebas de Seguridad (tiktok_analyzer) ---")
try:
    r_tk_ok = tiktok_analyzer({"profile_url": "https://www.tiktok.com/@dannyelarq", "max_videos": 5})
    r_tk_unsafe = tiktok_analyzer({"profile_url": "https://evil-tiktok.com/@hacker", "max_videos": 5})
    r_tk_limit = tiktok_analyzer({"profile_url": "https://www.tiktok.com/@dannyelarq", "max_videos": 999})
    
    print(f"  [tiktok_analyzer - URL OK] {r_tk_ok.splitlines()[0]}")
    print(f"  [tiktok_analyzer - Domain Blocked] {r_tk_unsafe}")
    print(f"  [tiktok_analyzer - Limit Blocked] {r_tk_limit}")
except Exception as e:
    print(f"  [tiktok_analyzer] FAIL: {e}")

# 6. Execution & Safety Verification (game_updater)
print("\n--- 6. Pruebas de Seguridad (game_updater) ---")
try:
    r_game_list = game_updater({"action": "list"})
    r_game_sched = game_updater({"action": "schedule", "hour": 4, "minute": 30})
    r_game_sched_bad = game_updater({"action": "schedule", "hour": 25, "minute": 90})
    r_game_name_bad = game_updater({"action": "install", "platform": "steam", "game_name": "CS; rm -rf"})
    
    print(f"  [game_updater - List OK] {r_game_list.splitlines()[0]}")
    print(f"  [game_updater - Sched OK] {r_game_sched}")
    print(f"  [game_updater - Sched Bounds Blocked] {r_game_sched_bad}")
    print(f"  [game_updater - Name Blocked] {r_game_name_bad}")
except Exception as e:
    print(f"  [game_updater] FAIL: {e}")

# 7. Manager Routing Check
print("\n--- 7. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        res_ff = await mgr.dispatch("flight_finder", {"origin": "LIM", "destination": "MIA", "date": "2026-10-15"}, ui=None)
        print(f"  [Manager -> flight_finder] Ruteado: '{res_ff.splitlines()[0]}'")

        res_sm = await mgr.dispatch("social_media", {"platform": "setup", "action": "setup"}, ui=None)
        print(f"  [Manager -> social_media] Ruteado: '{res_sm.splitlines()[0]}'")

        res_tk = await mgr.dispatch("tiktok_analyzer", {"profile_url": "https://www.tiktok.com/@dannyelarq"}, ui=None)
        print(f"  [Manager -> tiktok_analyzer] Ruteado: '{res_tk.splitlines()[0]}'")

        res_gu = await mgr.dispatch("game_updater", {"action": "download_status"}, ui=None)
        print(f"  [Manager -> game_updater] Ruteado: '{res_gu.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
