import os
import sys
import pygame
import time

# Pfad-Management
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, 'core'))

# Mock modules
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

from core.localization import set_language
from core.audio import AudioManager
from core.settings_manager import SettingsManager
from core.highscore_manager import HighscoreManager
from games.sound_memo import SoundMemo

def test_memo_pair():
    pygame.init()
    pygame.display.set_mode((1, 1))
    
    settings = SettingsManager("data/settings.json")
    audio = AudioManager(settings)
    # Mock Tolk to avoid errors
    audio.tolk_active = True
    class MockTolk:
        def Tolk_Output(self, text, interrupt): 
            print(f"TTS: {text}")
            return True
        def Tolk_IsSpeaking(self): return False
        def Tolk_Silence(self): return True
        def Tolk_Unload(self): return True
        def Tolk_IsLoaded(self): return True
    audio.tolk = MockTolk()
    audio.play_sound = lambda x, **kwargs: print(f"Sound: {x}")
    
    highscores = HighscoreManager("data/highscores.json")
    
    set_language("de")
    
    game = SoundMemo(audio, highscores, settings, "Tester")
    game.start()
    
    # Grid finden
    grid = game.grid
    print(f"Grid: {grid}")
    
    # Paar finden
    pair_item = grid[0]
    first_idx = 0
    second_idx = -1
    for i in range(1, len(grid)):
        if grid[i] == pair_item:
            second_idx = i
            break
    
    print(f"Testing pair: {pair_item} at {first_idx} and {second_idx}")
    
    # Erste Wahl
    game.pos = first_idx
    class FakeEvent:
        def __init__(self, key):
            self.type = pygame.KEYDOWN
            self.key = key
    
    print("Revealing first...")
    game.handle_input(FakeEvent(pygame.K_RETURN))
    
    # Zweite Wahl
    game.pos = second_idx
    print("Revealing second (pair)...")
    try:
        game.handle_input(FakeEvent(pygame.K_RETURN))
        print("Success! No crash on pair found.")
    except Exception as e:
        print(f"CRASH DETECTED: {e}")
        import traceback
        traceback.print_exc()

    # Jetzt alle Paare finden um finish() zu testen
    print("Finding all pairs to test finish()...")
    try:
        revealed_count = 0
        for i in range(len(grid)):
            if not game.revealed[i]:
                item = grid[i]
                # Suche Partner
                partner = -1
                for j in range(i+1, len(grid)):
                    if grid[j] == item:
                        partner = j
                        break
                
                if partner != -1:
                    game.pos = i
                    game.handle_input(FakeEvent(pygame.K_RETURN))
                    game.pos = partner
                    game.handle_input(FakeEvent(pygame.K_RETURN))
        
        print("Final reveal done.")
    except Exception as e:
        print(f"CRASH during final reveal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memo_pair()
