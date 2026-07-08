import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

terms = ['thinking', 'budget', 'proactive', 'affective']

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        matched = [t for t in terms if t in line.lower()]
                        if matched:
                            # print safely
                            print(f"{filepath}:{i} (matches {matched}): {line.strip()}")
            except Exception as e:
                pass
