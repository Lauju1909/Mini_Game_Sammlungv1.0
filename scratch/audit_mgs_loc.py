import sys
import os
import re

# Path to localization.py
loc_path = r"c:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung\core\localization.py"

def audit_translations(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract TRANSLATIONS dict
    # Simple regex to get the content between { and } for de and en
    # This is a bit fragile but might work for this specific file structure
    de_match = re.search(r'"de":\s*{(.*?)\s*},\s*"en":', content, re.DOTALL)
    en_match = re.search(r'"en":\s*{(.*?)\s*}', content, re.DOTALL)
    
    if not de_match or not en_match:
        print("Could not find de or en sections.")
        return
        
    de_content = de_match.group(1)
    en_content = en_match.group(1)
    
    def get_kv(text):
        kv = {}
        # Match "key": "value"
        matches = re.findall(r'"(.*?)"\s*:\s*"(.*?)"', text)
        for k, v in matches:
            if k in kv:
                # Handle duplicates by tracking them
                if isinstance(kv[k], list):
                    kv[k].append(v)
                else:
                    kv[k] = [kv[k], v]
            else:
                kv[k] = v
        return kv

    de_kv = get_kv(de_content)
    en_kv = get_kv(en_content)
    
    print("--- Audit Results ---")
    
    # Check for untranslated German strings
    untranslated = []
    for k, v in de_kv.items():
        if isinstance(v, list): v = v[0] # Just check first one for now
        # Check if value is identical to English value AND contains English common words
        if k in en_kv:
            ev = en_kv[k]
            if isinstance(ev, list): ev = ev[0]
            if v == ev and any(w in v.lower() for w in [" the ", " of ", " and ", " match ", " sequence ", " guess ", " search ", " press ", " enter ", " back "]):
                untranslated.append(f"{k}: {v}")
    
    print(f"Likely untranslated in German: {len(untranslated)}")
    for u in untranslated:
        print(f"  - {u}")

if __name__ == "__main__":
    audit_translations(loc_path)
