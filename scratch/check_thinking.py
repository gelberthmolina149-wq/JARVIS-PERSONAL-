from google import genai
from google.genai import types
import inspect

print("ThinkingConfig fields:")
try:
    print(inspect.signature(types.ThinkingConfig))
except Exception as e:
    print(e)

print("\nLiveConnectConfig fields:")
try:
    print(inspect.signature(types.LiveConnectConfig))
except Exception as e:
    print(e)
