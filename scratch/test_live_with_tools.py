import asyncio
import json
from pathlib import Path
from google import genai
from google.genai import types

# Import TOOL_DECLARATIONS from main
import sys
sys.path.append('.')
from main import TOOL_DECLARATIONS

API_CONFIG_PATH = Path("config/api_keys.json")

async def test_live_tools():
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
        
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1beta"}
    )
    
    print(f"Number of tools in TOOL_DECLARATIONS: {len(TOOL_DECLARATIONS)}")
    
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": TOOL_DECLARATIONS}],
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            thinking_level=types.ThinkingLevel.MINIMAL
        )
    )
    
    try:
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print("Successfully connected with tools!")
    except Exception as e:
        import traceback
        print("Connection failed:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_live_tools())
