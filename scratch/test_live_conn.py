import asyncio
import json
from pathlib import Path
from google import genai
from google.genai import types

API_CONFIG_PATH = Path("config/api_keys.json")

async def test_live():
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
        
    client = genai.Client(
        api_key=api_key,
        http_options={"api_version": "v1beta"}
    )
    
    print("Test 1: Default config (no thinking_config)...")
    try:
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
        )
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print("Test 1: Successfully connected!")
    except Exception as e:
        print("Test 1 failed:", e)

    print("\nTest 2: Config with thinking_budget=0...")
    try:
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print("Test 2: Successfully connected with thinking_budget=0!")
    except Exception as e:
        print("Test 2 failed:", e)

    print("\nTest 3: Config with thinking_level=MINIMAL...")
    try:
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.MINIMAL)
        )
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print("Test 3: Successfully connected with thinking_level=MINIMAL!")
    except Exception as e:
        print("Test 3 failed:", e)

if __name__ == "__main__":
    asyncio.run(test_live())
