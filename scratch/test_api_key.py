import json
from pathlib import Path
from google import genai

API_CONFIG_PATH = Path("config/api_keys.json")

def test_key():
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        api_key = json.load(f)["gemini_api_key"]
    
    print(f"API Key starting with: {api_key[:6]}...")
    client = genai.Client(api_key=api_key)
    
    print("\n--- Testing standard model (gemini-2.5-flash) ---")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hola, responde con 'OK'."
        )
        print("Success! Response:", response.text)
    except Exception as e:
        print("Error on generate_content:", e)
        
    print("\n--- Testing live model listing ---")
    try:
        models = client.models.list()
        for m in models:
            if "live" in m.name or "audio" in m.name:
                print("Available model:", m.name)
    except Exception as e:
        print("Error listing models:", e)

if __name__ == "__main__":
    test_key()
