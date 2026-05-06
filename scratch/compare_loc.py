import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'core'))
import localization

def compare_translations():
    de_keys = set(localization.TRANSLATIONS["de"].keys())
    en_keys = set(localization.TRANSLATIONS["en"].keys())
    
    only_de = de_keys - en_keys
    only_en = en_keys - de_keys
    
    print("Keys only in DE:")
    for k in sorted(only_de):
        print(f"- {k}")
        
    print("\nKeys only in EN:")
    for k in sorted(only_en):
        print(f"- {k}")

if __name__ == "__main__":
    compare_translations()
