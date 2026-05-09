import sys
import os
import time
import pygame
import random

# Path management
ROOT_DIR = r"C:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung"
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, "core"))

from core.audio import AudioManager
from core.localization import get_text as _
import core.localization as localization
from games.sound_memo import SoundMemo

class MockSettings:
    def get(self, key, default):
        return default

def test_sound_memo_crash():
    print("Testing SoundMemo for crashes when finding a pair...")
    pygame.init()
    pygame.display.set_mode((1, 1)) # Small window for pygame logic
    
    settings = MockSettings()
    audio = AudioManager(settings)
    
    # Mock tolk and play_sound to avoid actual sound output
    audio.tolk_active = False
    audio.sapi = None
    audio.play_sound = lambda x: print(f"Playing sound: {x}")
    audio.speak = lambda text, **kwargs: print(f"Speaking: {text}")

    game = SoundMemo(audio, None, settings, "Tester")
    game.start()

    # Find where the pairs are
    sound_positions = {}
    for i, sound in enumerate(game.grid):
        if sound not in sound_positions:
            sound_positions[sound] = []
        sound_positions[sound].append(i)
    
    print(f"Grid: {game.grid}")
    print(f"Pairs: {sound_positions}")

    # Try to reveal a pair
    first_sound = list(sound_positions.keys())[0]
    pos1, pos2 = sound_positions[first_sound]

    print(f"Attempting to reveal first pair: {first_sound} at positions {pos1} and {pos2}")

    # Move to pos1 and reveal
    game.pos = pos1
    game.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    
    # Move to pos2 and reveal
    game.pos = pos2
    game.handle_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    print("Success! No crash detected in logic.")
    
    # Now test the draw function with a revealed pair
    print("Testing draw function...")
    screen = pygame.Surface((800, 600))
    try:
        game.draw(screen)
        print("Draw function successful.")
    except Exception as e:
        print(f"Crash in draw function: {e}")
        import traceback
        traceback.print_exc()

    pygame.quit()

if __name__ == "__main__":
    test_sound_memo_crash()
