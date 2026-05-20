import os
import re

games_dir = "games"
main_file = "main.py"

game_files = [f for f in os.listdir(games_dir) if f.endswith(".py") and f != "__init__.py" and f != "base_game.py"]
game_ids = [f[:-3] for f in game_files]

with open(main_file, "r", encoding="utf-8") as f:
    main_content = f.read()

missing_imports = []
for gid in game_ids:
    if f"from games.{gid}" not in main_content:
        missing_imports.append(gid)

print(f"Missing imports: {missing_imports}")

missing_in_menu = []
for gid in game_ids:
    if f'"{gid}"' not in main_content and f"'{gid}'" not in main_content:
        missing_in_menu.append(gid)

print(f"Missing in menu: {missing_in_menu}")
