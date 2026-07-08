import sys
sys.path.append('.')
from main import TOOL_DECLARATIONS

for idx, tool in enumerate(TOOL_DECLARATIONS):
    params = tool.get("parameters", {})
    props = params.get("properties", {})
    for prop_name, prop_val in props.items():
        if prop_val.get("type") == "NUMBER":
            print(f"Tool {idx} ({tool['name']}) has NUMBER prop: {prop_name}")
        # also check nested items
        items = prop_val.get("items", {})
        if isinstance(items, dict):
            item_props = items.get("properties", {})
            for ip_name, ip_val in item_props.items():
                if ip_val.get("type") == "NUMBER":
                    print(f"Tool {idx} ({tool['name']}) has nested NUMBER prop: {prop_name}.{ip_name}")
