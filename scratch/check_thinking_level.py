from google.genai import types
try:
    print("ThinkingLevel options:")
    for name, member in types.ThinkingLevel.__members__.items():
        print(f"  {name}: {member.value}")
except Exception as e:
    print(e)
