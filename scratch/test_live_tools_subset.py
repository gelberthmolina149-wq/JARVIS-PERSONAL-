import asyncio
import json
from pathlib import Path
from google import genai
from google.genai import types
import sys
sys.path.append('.')
from main import TOOL_DECLARATIONS

API_CONFIG_PATH = Path("config/api_keys.json")

async def try_connect(tools):
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
        
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1beta"}
    )
    
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": tools}],
    )
    
    try:
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            return True
    except Exception as e:
        return False

async def main():
    print("Testing connection with 0 tools...", flush=True)
    if await try_connect([]):
        print("0 tools: OK", flush=True)
    else:
        print("0 tools: FAILED", flush=True)
        return

    print("\nTesting tools individually...", flush=True)
    failed_tools = []
    for idx, tool in enumerate(TOOL_DECLARATIONS):
        print(f"Testing tool {idx} ({tool['name']})...", end="", flush=True)
        ok = await try_connect([tool])
        if not ok:
            print(" FAILED", flush=True)
            failed_tools.append(tool['name'])
        else:
            print(" OK", flush=True)

    print("\nFailed tools list:", failed_tools, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
