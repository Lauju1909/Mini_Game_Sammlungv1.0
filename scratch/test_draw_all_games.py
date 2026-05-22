import pygame
import sys
import os

# Mock the audio and other managers
class MockAudioManager:
    def speak(self, text, **kwargs): pass
    def play_sound(self, name, **kwargs): pass
    def set_volumes(self, sfx, music): pass
    def set_speech_rate(self, rate): pass
    def set_speech_volume(self, vol): pass

class MockHighscoreManager:
    def __init__(self): pass
    def get_highscores(self, game_id): return []
    def add_score(self, game_id, name, score): pass

class MockSettingsManager:
    def __init__(self): pass
    def get(self, key, default=None): return default
    def set(self, key, value): pass

# Add core and root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'core'))

import localization
localization.set_language("de")

# Import all games dynamically from games folder
games_dir = os.path.join(PROJECT_ROOT, 'games')
game_files = [f for f in os.listdir(games_dir) if f.endswith('.py') and f not in ['__init__.py', 'base_game.py']]

pygame.init()
screen = pygame.Surface((800, 600))

audio = MockAudioManager()
highscores = MockHighscoreManager()
settings = MockSettingsManager()

print(f"Testing draw() method of {len(game_files)} games...")

errors = 0
for f in game_files:
    game_id = f[:-3]
    module_name = f"games.{game_id}"
    try:
        import importlib
        module = importlib.import_module(module_name)
        # Find the game class
        game_class = None
        for name, obj in module.__dict__.items():
            if isinstance(obj, type) and name != 'BaseGame' and 'BaseGame' in [base.__name__ for base in getattr(obj, '__bases__', [])]:
                game_class = obj
                break
        
        if game_class:
            game = game_class(audio, highscores, settings, "Tester")
            # Try calling draw()
            game.draw(screen)
            print(f"[{game_id}] draw() SUCCESS")
        else:
            print(f"[{game_id}] No game class found")
    except Exception as e:
        print(f"[{game_id}] draw() FAILED: {e}")
        import traceback
        traceback.print_exc()
        errors += 1

pygame.quit()
print(f"Finished testing. Total errors found: {errors}")
sys.exit(errors)
