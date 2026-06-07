import os
import glob
import importlib.util
import sys
import pygame
import random
import traceback
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

pygame.init()
pygame.display.set_mode((1,1))

targets = [
    "animal_radar", "audio_archery", "audio_balance", "audio_bowling",
    "audio_maze", "audio_sequence", "audio_slots", "beat_matcher",
    "beat_reaktor", "blind_farm", "bomb_defuser", "capital_hunter", "code_breaker"
]

for name in targets:
    mod = __import__(f"games.{name}", fromlist=['*'])
    game_class = None
    for attr in dir(mod):
        val = getattr(mod, attr)
        if isinstance(val, type) and val.__module__ == f"games.{name}" and attr != "BaseGame":
            game_class = val
            break
            
    if not game_class:
        print(f"Skipping {name}, no class found")
        continue

    audio = MockAudio()
    hs = MockHighscore()
    settings = MockSettings()
    
    print(f"Simulating {name}...")
    try:
        ticks = [0]
        def mock_get_ticks():
            ticks[0] += 16
            return ticks[0]
        
        orig_ticks = pygame.time.get_ticks
        pygame.time.get_ticks = mock_get_ticks
        
        game = game_class(audio, hs, settings, "TestPlayer")
        game.start()
        
        # simulate 5000 frames (approx 80s at 60fps)
        for i in range(5000):
            # random inputs
            if random.random() < 0.1:
                key = random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE, pygame.K_RETURN, pygame.K_a, pygame.K_b])
                ev = pygame.event.Event(pygame.KEYDOWN, {'key': key, 'unicode': chr(key) if key < 128 else ''})
                game.handle_input(ev)
                
            game.update()
            
        pygame.time.get_ticks = orig_ticks
            
    except Exception as e:
        print(f"ERROR in {name}: {e}")
        traceback.print_exc()
        
