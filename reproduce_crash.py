import sys
import os
import pygame
import time

# Add root and core to sys.path
ROOT_DIR = r"C:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung"
if ROOT_DIR not in sys.path: sys.path.append(ROOT_DIR)
CORE_DIR = os.path.join(ROOT_DIR, "core")
if CORE_DIR not in sys.path: sys.path.append(CORE_DIR)

from games.sound_memo import SoundMemo
from audio import AudioManager
from highscore_manager import HighscoreManager
from settings_manager import SettingsManager

def reproduce():
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    # Mock settings to avoid file I/O issues in test
    class MockSettings:
        def get(self, key, default=None):
            if key == "language": return "de"
            if "volume" in key: return 100
            if key == "speech_rate": return 50
            return default
        def set(self, key, value): pass

    settings = MockSettings()
    
    # Mock Audio to avoid real TTS/Sound issues
    class MockAudio:
        def __init__(self):
            self.last_spoken = ""
        def speak(self, text, **kwargs):
            print(f"SPEAK: {text}")
            self.last_spoken = text
        def play_sound(self, name):
            print(f"PLAY SOUND: {name}")
        def cleanup(self): pass

    audio = MockAudio()
    
    class MockHighscores:
        def add_score(self, game_id, name, score):
            print(f"ADD SCORE: {game_id}, {name}, {score}")
        def get_scores(self, game_id): return []

    highscores = MockHighscores()
    player = "Tester"
    
    game = SoundMemo(audio, highscores, settings, player)
    game.start()
    
    grid = game.grid
    print(f"Grid: {grid}")
    
    # Find all pairs
    pairs = {}
    for i, s in enumerate(grid):
        if s not in pairs:
            pairs[s] = []
        pairs[s].append(i)
    
    class FakeEvent:
        def __init__(self, key):
            self.type = pygame.KEYDOWN
            self.key = key

    for s, indices in pairs.items():
        print(f"\nTrying pair for sound: {s}")
        for idx in indices:
            game.pos = idx
            print(f"Revealing pos {idx}")
            game.handle_input(FakeEvent(pygame.K_RETURN))
            game.update()
            
            # Simulate some frames for draw
            # We don't call game.draw here because we want to see if logic crashes
            # But the user might be referring to a draw crash
            try:
                # Mock screen
                screen = pygame.Surface((800, 600))
                game.draw(screen)
            except Exception as e:
                print(f"CRASH IN DRAW: {e}")
                raise e

    print("\nAll pairs found successfully.")
    pygame.quit()

if __name__ == "__main__":
    try:
        reproduce()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
