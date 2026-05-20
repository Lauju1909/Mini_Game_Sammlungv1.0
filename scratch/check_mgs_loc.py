import sys
import os

# Path to localization.py
loc_path = r"c:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung\core\localization.py"

def find_duplicates(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    de_section = False
    en_section = False
    de_keys = []
    en_keys = []
    
    for line in lines:
        line = line.strip()
        if '"de": {' in line:
            de_section = True
            en_section = False
            continue
        if '"en": {' in line:
            en_section = True
            de_section = False
            continue
        
        if (de_section or en_section) and ":" in line:
            key = line.split(":")[0].strip().strip('"').strip("'")
            if de_section:
                de_keys.append(key)
            else:
                en_keys.append(key)
                
    def get_dups(keys):
        seen = set()
        dups = []
        for k in keys:
            if k in seen:
                dups.append(k)
            seen.add(k)
        return dups

    de_dups = get_dups(de_keys)
    en_dups = get_dups(en_keys)
    
    print(f"German Duplicates: {len(de_dups)}")
    for d in de_dups:
        print(f"  - {d}")
        
    print(f"English Duplicates: {len(en_dups)}")
    for d in en_dups:
        print(f"  - {d}")

    # Check for mismatches
    de_set = set(de_keys)
    en_set = set(en_keys)
    
    missing_in_en = de_set - en_set
    missing_in_de = en_set - de_set
    
    print(f"Missing in English: {len(missing_in_en)}")
    for m in missing_in_en:
        print(f"  - {m}")
        
    print(f"Missing in German: {len(missing_in_de)}")
    for m in missing_in_de:
        print(f"  - {m}")

if __name__ == "__main__":
    find_duplicates(loc_path)
