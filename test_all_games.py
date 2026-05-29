import os
import glob
import importlib.util
import sys
import pygame
from unittest.mock import MagicMock

# Set path to current directory so core imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create mock localization
mock_loc = MagicMock()
mock_loc.get_text.return_value = "mocked text"
sys.modules['localization'] = mock_loc

class MockAudio:
    def speak(self, text, interrupt=False, priority=1): pass
    def play_sound(self, name, vol=1.0, pan=0.0): pass
    def stop_sound(self, name): pass
    def set_music(self, name): pass
    def update(self): pass
    def play_panned_sound(self, name, pan): pass
    def play_looping_sound(self, name): return MagicMock()
    def create_tone_loop(self, freq): return MagicMock()
    def set_channel_volume(self, channel, vol_l, vol_r=None): pass

class MockHighscore:
    def add_score(self, game_id, player, score): pass
    def get_highscores(self, game_id): return []

class MockSettings:
    def __init__(self): self.d = {}
    def get(self, key, default=None): return self.d.get(key, default)
    def set(self, key, val): self.d[key] = val

def run_tests():
    pygame.init()
    pygame.display.set_mode((1,1))
    
    games_dir = "games"
    
    audio = MockAudio()
    hs = MockHighscore()
    settings = MockSettings()
    
    success = 0
    failed = []
    
    for py_file in glob.glob(os.path.join(games_dir, "*.py")):
        name = os.path.basename(py_file)[:-3]
        if name in ["base_game", "__init__"]: continue
        
        try:
            mod = __import__(f"games.{name}", fromlist=['*'])
            
            game_class = None
            for attr in dir(mod):
                val = getattr(mod, attr)
                if isinstance(val, type) and val.__name__ != "BaseGame" and "Game" in val.__name__ or attr == "Game":
                    if hasattr(val, "__init__"):
                        game_class = val
                        break
            
            if not game_class:
                for attr in dir(mod):
                    val = getattr(mod, attr)
                    if isinstance(val, type) and hasattr(val, '__bases__'):
                        if any(b.__name__ == 'BaseGame' for b in val.__bases__):
                             game_class = val
                             break
            
            if not game_class:
                for attr in dir(mod):
                    val = getattr(mod, attr)
                    if isinstance(val, type) and val.__module__ == f"games.{name}" and attr != "BaseGame":
                        game_class = val
                        break
                        
            if not game_class:
                 failed.append((name, "No Game class found"))
                 continue
                 
            game = game_class(audio, hs, settings, "TestPlayer")
            game.start()
            for _ in range(5): game.update()
            
            event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE, 'unicode': ' '})
            game.handle_input(event)
            game.update()
            
            game.finish()
            success += 1
            print(f"OK: {name}")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"FAIL: {name} - {e}")
            import traceback
            traceback.print_exc()
            
    print(f"\nSuccess: {success}, Failed: {len(failed)}")
    for f, err in failed:
        print(f" - {f}: {err}")

if __name__ == '__main__':
    run_tests()
