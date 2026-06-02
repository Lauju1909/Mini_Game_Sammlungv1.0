import os
import sys
import pygame
import pytest
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import MiniGameCollection

@pytest.fixture
def collection():
    pygame.init()
    
    class DummyChannel:
        def set_volume(self, *args): pass
        def stop(self): pass
        def play(self, *args, **kwargs): pass
        def fadeout(self, time_ms): pass

    class DummyAudio:
        def speak(self, text, interrupt=False, priority=0): pass
        def play_sound(self, name, volume=None, pan=None): pass
        def play_panned_sound(self, sound_name, pan): return DummyChannel()
        def play_looping_sound(self, sound_name, volume=None): return DummyChannel()
        def play_tone(self, frequency, duration_ms=500, volume=None, pan=0.0): return DummyChannel()
        def create_tone_loop(self, frequency, volume=None): return DummyChannel()
        def stop_sound(self, channel): pass
        def fadeout_sound(self, channel, time_ms): pass
        def set_channel_volume(self, channel, volume_left, volume_right=None): pass
        def set_volumes(self, sfx, music): pass
        def set_speech_rate(self, rate): pass
        def set_speech_volume(self, vol): pass
        def update(self): pass

    col = MiniGameCollection()
    col.audio = DummyAudio()
    yield col
    pygame.quit()

def test_all_games_deep(collection):
    cats = collection._get_categories_list()
    games = []
    for cat in cats:
        for g in cat.get("games", []):
            if "class" in g:
                games.append(g["class"])
    
    for game_class in games:
        game = game_class(collection.audio, collection.highscores, collection.settings, "TestPlayer")
        game.start()
        
        # Simulate 1500 frames (25s) to let bugs manifest
        frames_run = 0
        for _ in range(1500):
            if not getattr(game, 'active', True):
                break
                
            try:
                frames_run += 1
                game.update()
                
                # Random inputs with higher probability
                if random.random() < 0.2:
                    k = random.choice([
                        pygame.K_SPACE, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_RETURN,
                        pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
                        pygame.K_a, pygame.K_b, pygame.K_c
                    ])
                    unicode_char = chr(k) if 32 <= k <= 126 else ""
                    event = pygame.event.Event(pygame.KEYDOWN, key=k, unicode=unicode_char)
                    game.handle_input(event)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                pytest.fail(f"{game_class.__name__} failed during deep simulation: {e}")
                
        print(f"{game_class.__name__} ran {frames_run} frames.")
