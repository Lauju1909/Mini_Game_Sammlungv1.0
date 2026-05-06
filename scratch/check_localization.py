import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'core'))
import localization

def check_keys(directory):
    missing_keys = set()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    import re
                    # Find all _("...") or self._("...")
                    matches = re.findall(r'_\("([^"]+)"\)', content)
                    for match in matches:
                        if match not in localization.TRANSLATIONS["de"]:
                            missing_keys.add((match, "de"))
                        if match not in localization.TRANSLATIONS["en"]:
                            missing_keys.add((match, "en"))
    return missing_keys

if __name__ == "__main__":
    missing = check_keys(".")
    print("Missing keys:")
    for key, lang in sorted(missing):
        print(f"- {key} (missing in {lang})")
