import os
import re

def find_translation_keys(directory):
    keys = set()
    pattern = re.compile(r'(?:_|get_text)\("([^"]+)"')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        for k in matches:
                            keys.add(k)
                except:
                    pass
    return keys

if __name__ == "__main__":
    used_keys = find_translation_keys(".")
    for k in sorted(used_keys):
        print(k)
