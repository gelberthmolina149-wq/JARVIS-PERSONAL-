import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 5) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/youtube_video.py",
    "actions/spotify_control.py",
    "actions/rgb_control.py"
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
    from actions.youtube_video import youtube_video
    print("  [OK] youtube_video importado.")
except Exception as e:
    print(f"  [FAIL] Import youtube_video: {e}")

try:
    from actions.spotify_control import spotify_control
    print("  [OK] spotify_control importado.")
except Exception as e:
    print(f"  [FAIL] Import spotify_control: {e}")

try:
    from actions.rgb_control import rgb_control
    print("  [OK] rgb_control importado.")
except Exception as e:
    print(f"  [FAIL] Import rgb_control: {e}")

# 3. Execution Verification (youtube_video)
print("\n--- 3. Pruebas de Ejecucion Mock (youtube_video) ---")
try:
    # URL youtube domain verification (unsafe domain blocked)
    r_bad_url = youtube_video({"action": "play", "url": "https://malicious-youtube.com/watch?v=123"})
    print(f"  [youtube_video - Bad Domain Blocked] {r_bad_url}")

    # Normal Search Output
    r_play = youtube_video({"action": "play", "query": "avengers trailer"})
    print(f"  [youtube_video - Play Search] {r_play}")
except Exception as e:
    print(f"  [youtube_video] FAIL: {e}")

# 4. Execution Verification (spotify_control)
print("\n--- 4. Pruebas de Ejecucion Mock (spotify_control) ---")
try:
    # Volume range bounds checks
    r_vol_bad = spotify_control({"action": "volume", "value": "120"})
    print(f"  [spotify_control - Volume Max Limit] {r_vol_bad}")

    # Fallback to browser search
    r_play_web = spotify_control({"action": "play", "query": "daft punk"})
    print(f"  [spotify_control - Fallback Browser Search] {r_play_web}")
except Exception as e:
    print(f"  [spotify_control] FAIL: {e}")

# 5. Execution Verification (rgb_control)
print("\n--- 5. Pruebas de Ejecucion Mock (rgb_control) ---")
try:
    # Hex Color parsing
    from actions.rgb_control import parse_color
    r_color = parse_color("#FF5733")
    print(f"  [rgb_control - Hex Color Parse] {r_color}")

    # Connection failure fallback
    r_rgb_fail = rgb_control({"action": "set_color", "color": "rojo"})
    print(f"  [rgb_control - Connection Check] {r_rgb_fail}")
except Exception as e:
    print(f"  [rgb_control] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # youtube_video ruteado a CLOUD
        res_yt = await mgr.dispatch("youtube_video", {"action": "play", "query": "lofi hip hop"}, ui=None)
        print(f"  [Manager -> youtube_video] Ruteado: '{res_yt}'")

        # spotify_control ruteado a CLOUD
        res_sp = await mgr.dispatch("spotify_control", {"action": "pause"}, ui=None)
        print(f"  [Manager -> spotify_control] Ruteado: '{res_sp}'")

        # rgb_control ruteado a SYSTEM
        res_rgb = await mgr.dispatch("rgb_control", {"action": "list"}, ui=None)
        print(f"  [Manager -> rgb_control] Ruteado: '{res_rgb}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
