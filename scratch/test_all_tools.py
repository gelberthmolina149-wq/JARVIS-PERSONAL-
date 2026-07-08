"""
Test all 59 tools together to see if 1011 is caused by the full set or is transient.
Then do a binary search if it fails.
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

async def try_tools(label, tools):
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": tools}],
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            thinking_level=types.ThinkingLevel.MINIMAL
        )
    )
    try:
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print(f"{label}: OK (n={len(tools)})", flush=True)
            return True
    except Exception as e:
        print(f"{label}: FAILED (n={len(tools)}) — {str(e)[:120]}", flush=True)
        return False

async def main():
    n = len(TOOL_DECLARATIONS)
    print(f"Total tools: {n}", flush=True)

    # Test 1: all 59 tools (same as main.py)
    ok = await try_tools("All tools", TOOL_DECLARATIONS)
    if ok:
        print("\nAll 59 tools pass! 1011 was likely a transient server error.", flush=True)
        return

    # Binary search to find which half fails
    print("\nBinary search for failing group...", flush=True)
    mid = n // 2
    left_ok  = await try_tools("First half",  TOOL_DECLARATIONS[:mid])
    right_ok = await try_tools("Second half", TOOL_DECLARATIONS[mid:])

    if not left_ok and right_ok:
        print(f"\nProblem in FIRST half (tools 0-{mid-1})", flush=True)
    elif left_ok and not right_ok:
        print(f"\nProblem in SECOND half (tools {mid}-{n-1})", flush=True)
    elif not left_ok and not right_ok:
        print("\nBoth halves fail — problem may be total size/count", flush=True)
    else:
        print("\nBoth halves pass individually — combination is the trigger", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
