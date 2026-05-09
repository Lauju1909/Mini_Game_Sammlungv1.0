import sys
import os
import pygame
import time

# Add root and core to sys.path
ROOT_DIR = r"C:\Users\lauri\.\.gemini\antigravity\scratch\Mini_Game_Sammlung"
if ROOT_DIR not in sys.path: sys.path.append(ROOT_DIR)
CORE_DIR = os.path.join(ROOT_DIR, "core")
if CORE_DIR not in sys.path: sys.path.append(CORE_DIR)

from games.sound_memo import SoundMemo
from audio import AudioManager
from highscore_manager import HighscoreManager
from settings_manager import SettingsManager

def test_sound_memo():
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    settings = SettingsManager(os.path.join(ROOT_DIR, "data", "settings.json"))
    audio = AudioManager(settings)
    highscores = HighscoreManager(os.path.join(ROOT_DIR, "data", "highscores.json"))
    player = "Tester"
    
    game = SoundMemo(audio, highscores, settings, player)
    game.start()
    
    # Simulate finding a pair
    # We need to know which fields are the same
    grid = game.grid
    first_idx = 0
    second_idx = -1
    for i in range(1, 12):
        if grid[i] == grid[first_idx]:
            second_idx = i
            break
    
    print(f"Testing pair: {first_idx} and {second_idx} (Sound: {grid[first_idx]})")
    
    # Select first
    game.pos = first_idx
    class FakeEvent:
        def __init__(self, key):
            self.type = pygame.KEYDOWN
            self.key = key
    
    game.handle_input(FakeEvent(pygame.K_RETURN))
    game.update()
    
    # Select second
    game.pos = second_idx
    game.handle_input(FakeEvent(pygame.K_RETURN))
    game.update()
    
    print("Test finished without crash.")
    audio.cleanup()
    pygame.quit()

if __name__ == "__main__":
    try:
        test_sound_memo()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
