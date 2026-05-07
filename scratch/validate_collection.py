import os
import re
import sys

# Pfade
GAMES_DIR = r"C:\Users\lauri\AppData\Roaming\antigravity\brain\4ea3e66e-efc8-4d89-bc58-856de89de816\scratch\Mini_Game_Sammlung\games"
# Moment, der Pfad oben im list_dir war C:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung\
# Ich nutze den Pfad aus dem User Context
BASE_PATH = r"C:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung"
GAMES_DIR = os.path.join(BASE_PATH, "games")
MAIN_PY = os.path.join(BASE_PATH, "main.py")
LOCALIZATION_PY = os.path.join(BASE_PATH, "core", "localization.py")

def validate():
    print("--- Validierung der Mini-Game-Sammlung ---")
    
    # 1. Spiele im Ordner finden
    game_files = [f for f in os.listdir(GAMES_DIR) if f.endswith(".py") and f not in ["__init__.py", "base_game.py"]]
    game_ids = [f[:-3] for f in game_files]
    print(f"Gefundene Spiele-Dateien ({len(game_ids)}): {game_ids}")
    
    # 2. main.py lesen
    with open(MAIN_PY, "r", encoding="utf-8") as f:
        main_content = f.read()
        
    # 3. localization.py lesen
    with open(LOCALIZATION_PY, "r", encoding="utf-8") as f:
        loc_content = f.read()
        
    missing_imports = []
    missing_registration = []
    missing_loc_de = []
    missing_loc_en = []
    
    for gid in game_ids:
        # Import Check
        if f"games.{gid}" not in main_content:
            missing_imports.append(gid)
            
        # Registration Check (id: "gid")
        if f'"{gid}"' not in main_content and f"'{gid}'" not in main_content:
            missing_registration.append(gid)
            
        # Localization Check
        # Wir suchen nach game_gid in den "de" und "en" Bloecken
        # Da localization.py groß ist, schauen wir einfach ob der Key vorkommt
        if f'"game_{gid}"' not in loc_content and f"'game_{gid}'" not in loc_content:
            missing_loc_de.append(gid)
            
    print(f"\nFehlende Importe: {missing_imports}")
    print(f"Fehlende Registrierung: {missing_registration}")
    print(f"Fehlende Lokalisierung: {missing_loc_de}")
    
    if not missing_imports and not missing_registration and not missing_loc_de:
        print("\nAlles korrekt registriert!")
    else:
        print("\nHandlungsbedarf erforderlich!")

if __name__ == "__main__":
    validate()
