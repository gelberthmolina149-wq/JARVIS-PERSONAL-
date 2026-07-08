import sys, asyncio
sys.path.insert(0, '.')

print("=== PASO 4: Manager Routing Test ===")

async def test_manager():
    try:
        from core.manager import AgentManager
        mgr = AgentManager()

        tools_to_check = [
            ("open_app",          "system"),
            ("weather_report",    "cloud"),
            ("web_search",        "cloud"),
            ("computer_settings", "system"),
        ]

        all_ok = True
        for tool_name, expected_domain in tools_to_check:
            domain_agent = None
            for domain, agent in mgr._agents.items():
                if agent.handles(tool_name):
                    domain_agent = domain
                    break

            if domain_agent:
                mark = "PASS" if domain_agent == expected_domain else "WARN"
                print(f"  [{mark}] {tool_name} -> {domain_agent} (esperado: {expected_domain})")
            else:
                print(f"  [FAIL] {tool_name} -> NO REGISTRADA en ningun agente")
                all_ok = False

        print()
        if all_ok:
            print("  Manager routing OK - todas las tools estan registradas.")
        else:
            print("  Algunas tools no estan registradas en el manager.")

    except Exception as e:
        import traceback
        print(f"  [ERROR] {e}")
        traceback.print_exc()

asyncio.run(test_manager())
print("\nPaso 4 completado.")
