"""
Binary-search with smaller and smaller subsets to find the min N that causes 1011.
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

async def try_n_tools(n):
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": TOOL_DECLARATIONS[:n]}],
    )
    try:
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print(f"  n={n}: OK", flush=True)
            return True
    except Exception as e:
        print(f"  n={n}: FAILED", flush=True)
        return False

async def main():
    # Test powers of 2 to bracket the failure threshold
    for n in [1, 5, 10, 15, 20, 25]:
        ok = await try_n_tools(n)
        if not ok:
            print(f"\nFailure threshold is at or below n={n}", flush=True)
            # Narrow it down
            for i in range(n-5, n+1):
                if i > 0:
                    ok2 = await try_n_tools(i)
                    if not ok2:
                        print(f"\nMinimum failure at n={i}", flush=True)
                        # Show which tool is at index i-1
                        if i-1 < len(TOOL_DECLARATIONS):
                            print(f"Tool at index {i-1}: {TOOL_DECLARATIONS[i-1]['name']}", flush=True)
                        break
            break

if __name__ == "__main__":
    asyncio.run(main())
