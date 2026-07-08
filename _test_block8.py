import sys
import os
import asyncio

sys.path.insert(0, '.')

print("=== VERIFICACION DE ACCIONES (BLOQUE 8) ===")

# 1. Syntax Check
print("\n--- 1. Check de Sintaxis ---")
files_to_check = [
    "actions/rules_engine.py",
    "actions/user_profile.py",
    "actions/goals.py"
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
    from actions.rules_engine import rules_engine
    print("  [OK] rules_engine importado.")
except Exception as e:
    print(f"  [FAIL] Import rules_engine: {e}")

try:
    from actions.user_profile import user_profile
    print("  [OK] user_profile importado.")
except Exception as e:
    print(f"  [FAIL] Import user_profile: {e}")

try:
    from actions.goals import goals
    print("  [OK] goals importado.")
except Exception as e:
    print(f"  [FAIL] Import goals: {e}")

# 3. Execution Verification (rules_engine)
print("\n--- 3. Pruebas de Ejecucion Mock (rules_engine) ---")
try:
    # 1. Block rules execution on terminal_agent
    r_rules_block = rules_engine({"action": "create", "trigger_phrase": "destruye", "mapped_action": "terminal_agent"})
    print(f"  [rules_engine - Terminal Action Blocked] {r_rules_block}")

    # 2. Create normal trigger
    r_rules_ok = rules_engine({"action": "create", "trigger_phrase": "buenos dias", "mapped_action": "weather_report"})
    print(f"  [rules_engine - Create Trigger OK] {r_rules_ok}")

    # 3. Check triggers
    r_check = rules_engine({"action": "check_triggers", "trigger_phrase": "buenos dias JARVIS"})
    print(f"  [rules_engine - Trigger Matching] {r_check}")

    # Delete rule
    import json
    parsed_check = json.loads(r_check)
    if parsed_check.get("matched"):
        r_del = rules_engine({"action": "delete", "rule_id": parsed_check.get("rule_id")})
        print(f"  [rules_engine - Delete Rule] {r_del}")
except Exception as e:
    print(f"  [rules_engine] FAIL: {e}")

# 4. Execution Verification (user_profile)
print("\n--- 4. Pruebas de Ejecucion Mock (user_profile) ---")
try:
    # 1. Block secret credential storage
    r_prof_sec = user_profile({"action": "set", "key": "gemini_api_key", "value": "AIzaSy..."})
    print(f"  [user_profile - Sensitive Storage Blocked] {r_prof_sec}")

    # 2. Set normal pref
    r_prof_ok = user_profile({"action": "set", "key": "asistente_voz", "value": "Aoede"})
    print(f"  [user_profile - Set Preference] {r_prof_ok}")

    # 3. Get pref
    r_get = user_profile({"action": "get", "key": "asistente_voz"})
    print(f"  [user_profile - Get Preference] {r_get}")

    # Delete pref
    r_del_pref = user_profile({"action": "delete", "key": "asistente_voz"})
    print(f"  [user_profile - Delete Preference] {r_del_pref}")
except Exception as e:
    print(f"  [user_profile] FAIL: {e}")

# 5. Execution Verification (goals)
print("\n--- 5. Pruebas de Ejecucion Mock (goals) ---")
try:
    # 1. Add goal
    r_goals_ok = goals({"action": "add", "goal_text": "Mejorar modulos de JARVIS", "priority": "high"})
    print(f"  [goals - Add Goal] {r_goals_ok}")

    # 2. List
    r_list = goals({"action": "list"})
    print(f"  [goals - List Goals] {r_list.splitlines()[-1]}")

    # Delete goal
    # Find ID from list
    lines = r_list.splitlines()
    for l in lines:
        if "Mejorar modulos" in l:
            g_id = l.split("[")[2].split("]")[0] # Extraer el ID
            r_del_goal = goals({"action": "delete", "goal_id": g_id})
            print(f"  [goals - Delete Goal] {r_del_goal}")
            break
except Exception as e:
    print(f"  [goals] FAIL: {e}")

# 6. Manager Routing Check
print("\n--- 6. Test de Integracion de Manager ---")
async def test_manager_routing():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()
        
        # rules_engine ruteado a CLOUD
        res_rls = await mgr.dispatch("rules_engine", {"action": "list"}, ui=None)
        print(f"  [Manager -> rules_engine] Ruteado: '{res_rls.splitlines()[0]}'")

        # user_profile ruteado a DEV
        res_usr = await mgr.dispatch("user_profile", {"action": "list"}, ui=None)
        print(f"  [Manager -> user_profile] Ruteado: '{res_usr.splitlines()[0]}'")

        # goals ruteado a DEV
        res_gls = await mgr.dispatch("goals", {"action": "list"}, ui=None)
        print(f"  [Manager -> goals] Ruteado: '{res_gls.splitlines()[0]}'")
    except Exception as e:
        print(f"  [Manager Routing] FAIL: {e}")

asyncio.run(test_manager_routing())
