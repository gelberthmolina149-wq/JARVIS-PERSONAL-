"""
Confirm: thinking_config is the 1011 trigger, not arca_invoice or schema issues.
"""
import asyncio
import json
from pathlib import Path
from google import genai
from google.genai import types
import sys
sys.path.append('.')
from main import TOOL_DECLARATIONS

API_CONFIG_PATH = Path("config/api_keys.json")

async def try_config(label, config):
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
    try:
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print(f"{label}: OK", flush=True)
            return True
    except Exception as e:
        print(f"{label}: FAILED — {str(e)[:120]}", flush=True)
        return False

async def main():
    all_tools = TOOL_DECLARATIONS  # 59 tools

    print(f"Using {len(all_tools)} tools in all tests\n", flush=True)

    # Test A: No thinking_config
    cfg_a = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": all_tools}],
    )
    await try_config("A. 59 tools, NO thinking_config", cfg_a)

    # Test B: thinking_config(budget=0, level=MINIMAL)
    cfg_b = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": all_tools}],
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            thinking_level=types.ThinkingLevel.MINIMAL
        )
    )
    await try_config("B. 59 tools, thinking_config(budget=0, level=MINIMAL)", cfg_b)

    # Test C: thinking_config(budget=0 only)
    cfg_c = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": all_tools}],
        thinking_config=types.ThinkingConfig(thinking_budget=0)
    )
    await try_config("C. 59 tools, thinking_config(budget=0 only)", cfg_c)

    # Test D: thinking_config(level=MINIMAL only)
    cfg_d = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": all_tools}],
        thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL)
    )
    await try_config("D. 59 tools, thinking_config(level=MINIMAL only)", cfg_d)

if __name__ == "__main__":
    asyncio.run(main())
