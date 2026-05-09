import sys
import os
import pygame
import time

# Pfad-Management
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ROOT_DIR, 'core'))
sys.path.append(ROOT_DIR)

# Mocking all managers to avoid path issues
class MockSettings:
    def get(self, key, default): return default
    def set(self, key, value): pass

class MockAudio:
    def __init__(self):
        self.sfx_volume = 100
    def speak(self, text, interrupt=True, priority=1):
        print(f"SPEAK: {text}")
    def play_sound(self, name):
        print(f"PLAY SOUND: {name}")

class MockHighscore:
    def add_score(self, game_id, player, score):
        print(f"ADD SCORE: {game_id}, {player}, {score}")

from games.sound_memo import SoundMemo

def test_sound_memo_crash():
    pygame.init()
    pygame.display.set_mode((800, 600))
    
    settings = MockSettings()
    audio = MockAudio()
    highscore = MockHighscore()
    
    game = SoundMemo(audio, highscore, settings, "Tester")
    game.start()
    
    # Solve all pairs
    found_indices = set()
    while len(found_indices) < 12:
        idx1 = -1
        for i in range(12):
            if i not in found_indices:
                idx1 = i
                break
        
        idx2 = -1
        for i in range(12):
            if i != idx1 and i not in found_indices and game.grid[i] == game.grid[idx1]:
                idx2 = i
                break
        
        print(f"Revealing pair {idx1}, {idx2} (Sound: {game.grid[idx1]})")
        game.pos = idx1
        game._reveal()
        game.pos = idx2
        game._reveal()
        
        found_indices.add(idx1)
        found_indices.add(idx2)

    print("All pairs revealed")

    # Try to draw
    # Note: drawing might require fonts, which we might need to mock if Arial is not found
    screen = pygame.Surface((800, 600))
    try:
        game.draw(screen)
        print("Draw successful")
    except Exception as e:
        print(f"CRASH in draw: {e}")
        import traceback
        traceback.print_exc()
        return

    print("Test finished without crash.")
    pygame.quit()

if __name__ == "__main__":
    test_sound_memo_crash()
