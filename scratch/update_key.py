import os
import json

new_key = os.environ.get("NEW_GEMINI_KEY")
if not new_key:
    print("Error: NEW_GEMINI_KEY env var not set.")
    exit(1)

config_path = "config/api_keys.json"
try:
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    data = {}

data["gemini_api_key"] = new_key

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("SUCCESS: Config updated with new key.")
