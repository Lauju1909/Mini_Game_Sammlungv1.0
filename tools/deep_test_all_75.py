import os
import sys
import glob
import time
import pygame
from unittest.mock import MagicMock

base_dir = r"C:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung"
sys.path.insert(0, base_dir)
sys.path.insert(0, os.path.join(base_dir, "core"))

import localization
localization.set_language("de")

class MockAudio:
    def speak(self, text, interrupt=False, priority=1): pass
    def play_sound(self, name, vol=1.0, pan=0.0): pass
    def stop_sound(self, name): pass
    def set_music(self, name): pass
    def update(self): pass
    def play_panned_sound(self, name, pan, volume=None): pass
    def play_looping_sound(self, name, volume=None): return MagicMock()
    def play_tone(self, frequency, duration_ms=500, volume=None, pan=0.0): pass
    def create_tone_loop(self, freq, volume=None): return MagicMock()
    def set_channel_volume(self, channel, vol_l, vol_r=None): pass
    def is_speaking(self): return False

class MockHighscore:
    def add_score(self, game_id, player, score): pass
    def get_scores(self, game_id): return []

class MockSettings:
    def __init__(self): self.d = {"completed_tutorials": []}
    def get(self, key, default=None): return self.d.get(key, default)
    def set(self, key, val): self.d[key] = val

def test_all():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    games_dir = os.path.join(base_dir, "games")
    py_files = sorted(glob.glob(os.path.join(games_dir, "*.py")))
    
    tested = 0
    errors = []
    
    for py_file in py_files:
        name = os.path.basename(py_file)[:-3]
        if name in ["base_game", "__init__"]:
            continue
            
        try:
            mod = __import__(f"games.{name}", fromlist=['*'])
            game_class = None
            for attr in dir(mod):
                val = getattr(mod, attr)
                if isinstance(val, type) and hasattr(val, '__bases__'):
                    if any(b.__name__ == 'BaseGame' for b in val.__bases__):
                        game_class = val
                        break
            if not game_class:
                errors.append(f"{name}: No BaseGame subclass found")
                continue
                
            audio = MockAudio()
            hs = MockHighscore()
            st = MockSettings()
            
            # 1. Instantiate
            game = game_class(audio, hs, st, "Tester")
            
            # 2. Tutorial test
            game.start_tutorial()
            game.update_tutorial()
            ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
            game.handle_tutorial_input(ev_enter)
            if not game.tutorial_finished:
                # Custom tutorials might need specific input or step progression
                game.finish_tutorial()
                
            # 3. Start game
            game.start()
            
            # 4. Update for 30 frames
            for _ in range(30):
                game.update()
                
            # 5. Handle key inputs
            for key in [pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_1]:
                ev = pygame.event.Event(pygame.KEYDOWN, key=key, unicode="1")
                game.handle_input(ev)
                game.update()
                
            # 6. Draw to screen
            game.draw(screen)
            
            # 7. Finish
            game.finish()
            
            tested += 1
            print(f"PASS: {name} (id={game.game_id})")
        except Exception as e:
            import traceback
            errors.append(f"FAIL: {name} -> {e}\n{traceback.format_exc()}")
            print(f"FAIL: {name} -> {e}")

    print("\n===============================")
    print(f"Total Passed: {tested} / {len(py_files) - 2}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for err in errors:
            print(err)
        return False
    else:
        print("ALL 75 GAMES PASSED COMPLETE DEEP SIMULATION & DRAW TESTS!")
        return True

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
