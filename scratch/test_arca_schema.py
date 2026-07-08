import asyncio
import json
from pathlib import Path
from google import genai
from google.genai import types

API_CONFIG_PATH = Path("config/api_keys.json")

def get_base_schema(detalle_schema):
    return {
        "name": "arca_invoice",
        "description": "Genera comprobantes digitales electrónicos válidos ante ARCA (ex AFIP).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":  {"type": "STRING", "description": "generar | listar | historial"},
                "tipo":    {"type": "INTEGER"},
                "detalle": detalle_schema
            },
            "required": ["action"]
        }
    }

async def try_connect_schema(schema):
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": [schema]}],
    )
    try:
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            return True, None
    except Exception as e:
        return False, str(e)

async def main():
    # Test 1: Original detail schema
    schema_1 = get_base_schema({
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "descripcion": {"type": "STRING"},
                "precio": {"type": "NUMBER"},
                "cantidad": {"type": "INTEGER"}
            }
        },
        "description": "Lista de productos"
    })
    ok, err = await try_connect_schema(schema_1)
    print(f"Test 1 (Original-like): {'OK' if ok else 'FAILED: ' + err}")

    # Test 2: Add description to nested properties
    schema_2 = get_base_schema({
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "descripcion": {"type": "STRING", "description": "desc"},
                "precio": {"type": "NUMBER", "description": "price"},
                "cantidad": {"type": "INTEGER", "description": "qty"}
            }
        },
        "description": "Lista de productos"
    })
    ok, err = await try_connect_schema(schema_2)
    print(f"Test 2 (With desc): {'OK' if ok else 'FAILED: ' + err}")

    # Test 3: Change NUMBER to string or float-like type, or change type capitalization?
    # Wait, OpenAPI spec standard capitalization is lowercase: "string", "number", "integer", "object", "array"
    # But wait, in main.py, the capitalizations are uppercase like "ARRAY", "STRING", etc.
    # Wait, does the API server require lowercase types for nested objects/arrays?
    # Let's test lowercase types.
    schema_3 = {
        "name": "arca_invoice",
        "description": "Genera comprobantes",
        "parameters": {
            "type": "object",
            "properties": {
                "action":  {"type": "string", "description": "action"},
                "tipo":    {"type": "integer"},
                "detalle": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "descripcion": {"type": "string", "description": "desc"},
                            "precio": {"type": "number", "description": "price"},
                            "cantidad": {"type": "integer", "description": "qty"}
                        }
                    }
                }
            },
            "required": ["action"]
        }
    }
    ok, err = await try_connect_schema(schema_3)
    print(f"Test 3 (Lowercase types): {'OK' if ok else 'FAILED: ' + err}")

if __name__ == "__main__":
    asyncio.run(main())
