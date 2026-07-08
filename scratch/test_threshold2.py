"""
Find exact N threshold between 25 and 59 where 1011 appears.
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
    print("Scanning from n=26 to n=59 to find failure threshold...", flush=True)
    last_ok = 25
    for n in range(26, 60):
        ok = await try_n_tools(n)
        if ok:
            last_ok = n
        else:
            print(f"\nThreshold found: n={n} fails. Tool #{n-1} is '{TOOL_DECLARATIONS[n-1]['name']}'", flush=True)
            print(f"Last passing n={last_ok}: Tool #{last_ok-1} is '{TOOL_DECLARATIONS[last_ok-1]['name']}'", flush=True)
            break

if __name__ == "__main__":
    asyncio.run(main())
