import sys
import os
import time

# Pfad-Management
ROOT_DIR = r"C:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung"
sys.path.append(ROOT_DIR)

from tools.agentic_tester_v4 import MiniGameEnv

def test_sound_memo_crash():
    env = MiniGameEnv()
    
    # 1. Navigation zum Sound-Memo
    # Hauptmenü: Spielen ist meist die erste Option
    print("Selecting Play...")
    env.perform_action("RETURN") 
    time.sleep(0.5)
    
    # Kategorien: Logik ist meist die zweite
    print("Selecting Logic Category...")
    env.perform_action("DOWN")
    env.perform_action("RETURN")
    time.sleep(0.5)
    
    # Spiele in Logik: Sound-Memo ist meist die erste
    print("Selecting Sound-Memo...")
    env.perform_action("RETURN")
    time.sleep(0.5)
    
    # Spieleranzahl: 1 Spieler
    print("Selecting 1 Player...")
    env.perform_action("RETURN")
    time.sleep(0.5)
    
    # Name eingeben: "Tester" + RETURN
    print("Entering Name...")
    for char in "Tester":
        # Hier müssten wir eigentlich die Tasten simulieren, aber der Tester hat perform_action für Spezialtasten.
        # MiniGameEnv.perform_action benutzt pygame.K_...
        # Wir können direkt MiniGameCollection.text_input manipulieren
        env.game.text_input.text = "Tester"
    env.perform_action("RETURN")
    time.sleep(0.5)
    
    # Beschreibung überspringen
    print("Starting Game...")
    env.perform_action("RETURN")
    time.sleep(1.0)
    
    # Jetzt sind wir im Spiel
    game = env.game.current_game
    if not game or game.game_id != "sound_memo":
        print(f"Failed to start SoundMemo. Current game: {game}")
        return

    grid = game.grid
    print(f"Grid: {grid}")
    
    # Find a pair
    pairs = {}
    for i, s in enumerate(grid):
        if s not in pairs: pairs[s] = []
        pairs[s].append(i)
    
    first_sound = list(pairs.keys())[0]
    idx1, idx2 = pairs[first_sound]
    
    print(f"Trying to match pair: {idx1} and {idx2} ({first_sound})")
    
    # Move to idx1
    # Assuming grid is 4x3 or something? No, it's 1D navigation in SoundMemo
    game.pos = idx1
    env.perform_action("RETURN")
    time.sleep(0.5)
    
    # Move to idx2
    game.pos = idx2
    print("Performing second RETURN (should find pair)...")
    env.perform_action("RETURN")
    
    print("Checking if still alive...")
    state = env.get_state()
    print(f"Current State: {state}")
    
    # If we reached here, it didn't crash
    print("Test completed.")

if __name__ == "__main__":
    test_sound_memo_crash()
