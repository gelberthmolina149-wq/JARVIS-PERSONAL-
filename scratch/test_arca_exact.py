"""
Diagnose which specific arca_invoice variant causes 1011.
Tests: nested NUMBER, top-level NUMBER, and then confirms the fix.
"""
import asyncio
import json
from pathlib import Path
from google import genai
from google.genai import types

API_CONFIG_PATH = Path("config/api_keys.json")

async def try_tool(label, schema):
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        tools=[{"function_declarations": [schema]}],
    )
    try:
        async with client.aio.live.connect(model="models/gemini-3.1-flash-live-preview", config=config) as session:
            print(f"{label}: OK", flush=True)
            return True
    except Exception as e:
        print(f"{label}: FAILED — {str(e)[:100]}", flush=True)
        return False

async def main():
    # Original full schema
    original = {
        "name": "arca_invoice",
        "description": "Genera comprobantes ARCA (ex AFIP).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":       {"type": "STRING", "description": "generar | listar | historial"},
                "tipo":         {"type": "INTEGER"},
                "razon_social": {"type": "STRING"},
                "cuit_receptor":{"type": "STRING"},
                "domicilio":    {"type": "STRING"},
                "detalle":      {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"descripcion": {"type": "STRING"}, "precio": {"type": "NUMBER"}, "cantidad": {"type": "INTEGER"}}}, "description": "Lista de productos"},
                "importe_neto": {"type": "NUMBER"},
                "importe_iva":  {"type": "NUMBER"},
                "iva_pct":      {"type": "NUMBER"},
                "fecha":        {"type": "STRING"},
            },
            "required": ["action"]
        }
    }
    await try_tool("1. ORIGINAL (baseline)", original)

    # Test: remove only detalle (keep top-level NUMBERs)
    no_detalle = {
        "name": "arca_invoice",
        "description": "Genera comprobantes ARCA.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":       {"type": "STRING", "description": "generar | listar | historial"},
                "importe_neto": {"type": "NUMBER"},
                "importe_iva":  {"type": "NUMBER"},
                "iva_pct":      {"type": "NUMBER"},
            },
            "required": ["action"]
        }
    }
    await try_tool("2. No detalle, keep top-level NUMBER", no_detalle)

    # Test: only detalle with NUMBER in items
    only_detalle = {
        "name": "arca_invoice",
        "description": "Genera comprobantes ARCA.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":  {"type": "STRING", "description": "generar | listar | historial"},
                "detalle": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"descripcion": {"type": "STRING"}, "precio": {"type": "NUMBER"}, "cantidad": {"type": "INTEGER"}}}, "description": "Lista de productos"},
            },
            "required": ["action"]
        }
    }
    await try_tool("3. Only detalle with nested NUMBER", only_detalle)

    # Test: detalle items OBJECT but precio as STRING instead of NUMBER
    detalle_precio_str = {
        "name": "arca_invoice",
        "description": "Genera comprobantes ARCA.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":  {"type": "STRING", "description": "generar | listar | historial"},
                "detalle": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"descripcion": {"type": "STRING"}, "precio": {"type": "STRING"}, "cantidad": {"type": "INTEGER"}}}, "description": "Lista de productos, precio como string numerico"},
                "importe_neto": {"type": "NUMBER"},
            },
            "required": ["action"]
        }
    }
    await try_tool("4. detalle.precio as STRING (workaround)", detalle_precio_str)

    # Test: detalle items OBJECT — add description to nested props
    detalle_with_desc = {
        "name": "arca_invoice",
        "description": "Genera comprobantes ARCA.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action":  {"type": "STRING", "description": "generar | listar | historial"},
                "detalle": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"descripcion": {"type": "STRING", "description": "desc"}, "precio": {"type": "NUMBER", "description": "precio unitario"}, "cantidad": {"type": "INTEGER", "description": "cantidad"}}}, "description": "Lista de productos"},
                "importe_neto": {"type": "NUMBER"},
            },
            "required": ["action"]
        }
    }
    await try_tool("5. Nested NUMBER with description on each prop", detalle_with_desc)

if __name__ == "__main__":
    asyncio.run(main())
