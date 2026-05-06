import os
import re

def find_translation_keys(directory):
    keys = set()
    # Matches _("key") or self._("key") or get_text("key")
    pattern = re.compile(r'(?:_|get_text)\("([^"]+)"')
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    for k in matches:
                        keys.add(k)
    return keys

if __name__ == "__main__":
    used_keys = find_translation_keys(".")
    import sys
    sys.path.append(os.path.join(os.getcwd(), 'core'))
    import localization
    
    de_keys = set(localization.TRANSLATIONS["de"].keys())
    en_keys = set(localization.TRANSLATIONS["en"].keys())
    
    missing_de = used_keys - de_keys
    missing_en = used_keys - en_keys
    
    print("Keys missing in DE:")
    for k in sorted(missing_de):
        print(f"- {k}")
        
    print("\nKeys missing in EN:")
    for k in sorted(missing_en):
        print(f"- {k}")
