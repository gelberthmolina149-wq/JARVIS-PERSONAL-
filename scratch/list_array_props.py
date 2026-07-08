import sys
sys.path.append('.')
from main import TOOL_DECLARATIONS

for idx, tool in enumerate(TOOL_DECLARATIONS):
    params = tool.get("parameters", {})
    props = params.get("properties", {})
    for prop_name, prop_val in props.items():
        if prop_val.get("type") == "ARRAY":
            print(f"Tool {idx} ({tool['name']}) has array prop: {prop_name} -> {prop_val}")
