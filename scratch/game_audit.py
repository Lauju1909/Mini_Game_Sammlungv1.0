import os
import sys
import importlib

# Pfade anpassen
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, 'core'))
sys.path.append(PROJECT_ROOT)

import localization
from localization import TRANSLATIONS

def audit():
    print("--- Mini-Game-Sammlung Audit ---")
    
    # 1. Games im Verzeichnis finden
    games_dir = os.path.join(PROJECT_ROOT, 'games')
    game_files = [f for f in os.listdir(games_dir) if f.endswith('.py') and f != '__init__.py' and f != 'base_game.py']
    game_ids_from_files = [f[:-3] for f in game_files]
    
    print(f"Gefundene Spieldateien: {len(game_ids_from_files)}")
    
    # 2. Registrierung in main.py prüfen
    main_path = os.path.join(PROJECT_ROOT, 'main.py')
    with open(main_path, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    # 3. Kategorien in main.py prüfen
    import main
    collection = main.MiniGameCollection.__new__(main.MiniGameCollection)
    # Mocking settings and audio for categories list
    collection.settings = type('obj', (object,), {'get': lambda self, x: 'de'})()
    
    # Wir brauchen ein minimales Mocking um _get_categories_list aufzurufen
    categories = collection._get_categories_list()
    registered_game_ids = []
    for cat in categories:
        for game in cat.get("games", []):
            registered_game_ids.append(game["id"])
    
    print(f"Registrierte Spiele in main.py (inkl. Duplikate): {len(registered_game_ids)}")
    unique_registered = list(set(registered_game_ids))
    print(f"Eindeutige registrierte Spiele: {len(unique_registered)}")
    
    # 4. Vergleich
    missing_in_main = [gid for gid in game_ids_from_files if gid not in unique_registered]
    if missing_in_main:
        print(f"\nWARNUNG: Dateien vorhanden aber nicht registriert: {missing_in_main}")
    
    extra_in_main = [gid for gid in unique_registered if gid not in game_ids_from_files]
    if extra_in_main:
        print(f"\nFEHLER: Registriert aber Datei fehlt: {extra_in_main}")
        
    # 5. Lokalisierung prüfen
    print("\nPrüfe Lokalisierung (de & en):")
    missing_locales = []
    for gid in unique_registered:
        for lang in ['de', 'en']:
            keys = [
                f"game_{gid}",
                f"game_{gid}_desc",
                f"game_{gid}_instructions"
            ]
            missing = [k for k in keys if k not in TRANSLATIONS[lang]]
            if missing:
                missing_locales.append((lang, gid, missing))
                print(f"  [{lang}] {gid}: Fehlende Keys: {missing}")
    
    if not missing_locales:
        print("  Alle Lokalisierungsschlüssel vorhanden.")

    # 6. Import Test
    print("\nTeste Importe:")
    import_errors = []
    for gid in game_ids_from_files:
        try:
            module = importlib.import_module(f"games.{gid}")
            found_class = False
            for name, obj in module.__dict__.items():
                if isinstance(obj, type) and name != 'BaseGame' and 'BaseGame' in [base.__name__ for base in getattr(obj, '__bases__', [])]:
                    found_class = True
                    break
            if not found_class:
                print(f"  {gid}: Keine Spielklasse gefunden!")
        except Exception as e:
            import_errors.append((gid, str(e)))
            print(f"  {gid}: Import-Fehler: {e}")
    
    if not import_errors:
        print("  Alle Importe erfolgreich.")

    # 7. Asset-Referenzen prüfen (einfacher Scan)
    print("\nPrüfe Asset-Referenzen (Scan nach .ogg/.mp3/.wav in games/):")
    assets_dir = os.path.join(PROJECT_ROOT, 'assets')
    available_assets = os.listdir(assets_dir)
    
    for gfile in game_files:
        with open(os.path.join(games_dir, gfile), 'r', encoding='utf-8') as f:
            content = f.read()
            import re
            found_assets = re.findall(r'play_sound\("([^"]+)"\)', content)
            found_assets += re.findall(r"play_sound\('([^']+)'\)", content)
            
            for asset in set(found_assets):
                # Prüfe ob asset.ogg, asset.mp3 oder asset.wav existiert
                exists = any(asset + ext in available_assets for ext in ['.ogg', '.mp3', '.wav'])
                if not exists:
                    print(f"  {gfile}: Sound '{asset}' nicht im assets-Ordner gefunden!")


if __name__ == "__main__":
    audit()
