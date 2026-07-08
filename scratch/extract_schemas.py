import json
import os
import sys

# Ensure scratch directory exists
os.makedirs('scratch', exist_ok=True)

content = open('main.py', encoding='utf-8').read()
start = content.find('TOOL_DECLARATIONS = [')
if start == -1:
    print("Could not find TOOL_DECLARATIONS")
    sys.exit(1)

# Find matching closing bracket
bracket_count = 0
end = -1
for i in range(start + len('TOOL_DECLARATIONS = '), len(content)):
    if content[i] == '[':
        bracket_count += 1
    elif content[i] == ']':
        bracket_count -= 1
        if bracket_count == 0:
            end = i + 1
            break

if end == -1:
    print("Could not find end of TOOL_DECLARATIONS")
    sys.exit(1)

decl_str = content[start:end]
locs = {}
try:
    exec(decl_str, {}, locs)
    decls = locs['TOOL_DECLARATIONS']
    
    # Let's print all tool names first
    names = [d['name'] for d in decls]
    print("All declared tools in main.py:", names)
    
    missing_tools = ['windows_settings', 'vision_guardian', 'system_monitor', 'native_ui', 'smart_home', 'accessibility', 'accessibility_overlay', 'camera_bus', 'jarvis_ui_control', 'flight_finder', 'social_media', 'tiktok_analyzer', 'game_updater', 'dev_agent', 'codebase', 'file_processor', 'document_creator', 'document_manager', 'image_generation', 'morning_brief', 'openrouter_agent', 'agent_task']
    
    results = []
    for d in decls:
        name = d['name']
        if name in missing_tools:
            results.append({
                "name": name,
                "description": d.get("description", ""),
                "parameters": d.get("parameters", {})
            })
            
    with open('scratch/extracted_schemas.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Successfully extracted {len(results)} schemas.")
except Exception as e:
    import traceback
    traceback.print_exc()
