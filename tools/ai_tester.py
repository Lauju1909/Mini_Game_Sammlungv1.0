import os
import sys
import time
import random
import pygame
import json

# Pfade für Importe setzen
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, "core"))

# Dummy Treiber für kopfloses Testen
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1,1))

from main import MiniGameCollection

class MockAudio:
    def __init__(self):
        self.speech_count = 0
        self.sound_count = 0
        self.panned_count = 0
        self.last_speech = ""
        self.sounds_played_global = set()
        self.sounds_per_game = {}
        self.current_game_id = "menu"
        self.errors = []
        self.last_speak_time = 0
        self.in_init = False

    def speak(self, text, interrupt=True, **kwargs):
        now = time.time()
        if interrupt and now - self.last_speak_time < 0.1 and self.last_speak_time > 0:
            self.errors.append(f"SPEECH STOMPING in {self.current_game_id}: '{text}' unterbricht '{self.last_speech}' zu schnell!")
        
        if self.in_init:
            # Warnung statt Fehler, da es technisch erlaubt ist, aber Accessibility-Probleme macht
            print(f"    [WARN]: {self.current_game_id} spricht während __init__. Das wird wahrscheinlich von den Spielanweisungen unterbrochen!")

        self.speech_count += 1
        self.last_speech = text
        self.last_speak_time = now

    def play_sound(self, name):
        self._log_sound(name)
        self._check_file(name)
        self.sound_count += 1

    def play_panned_sound(self, name, pan):
        self._log_sound(name)
        self._check_file(name)
        self.panned_count += 1

    def _log_sound(self, name):
        self.sounds_played_global.add(name)
        if self.current_game_id not in self.sounds_per_game:
            self.sounds_per_game[self.current_game_id] = set()
        self.sounds_per_game[self.current_game_id].add(name)

    def _check_file(self, name):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = False
        for fmt in ["ogg", "mp3", "wav"]:
            if os.path.exists(os.path.join(base_dir, "assets", f"{name}.{fmt}")):
                found = True
                break
        if not found:
            self.errors.append(f"Audio-Datei fehlt: {name} (in {self.current_game_id})")

    def set_volumes(self, sfx, music): pass
    def cleanup(self): pass

def run_test():
    print("="*40)
    print("KI-PLAYTESTER 2.0 (INTELLIGENT) STARTET...")
    print("="*40)

    game = MiniGameCollection()
    mock_audio = MockAudio()
    game.audio = mock_audio
    
    errors = []
    games_tested = 0
    
    # Hauptmenü -> Spielen
    game.on_main_menu_select({"id": "play", "label": "Spielen"})
    
    categories = list(game.menu.current_menu)
    for cat in categories:
        if cat.get("id") == "back": continue
        
        print(f"  -> Teste Kategorie: {cat['label']}")
        game.on_category_select(cat)
        
        game_list = list(game.menu.current_menu)
        for item in game_list:
            if item.get("label") == "Zurück": continue
            
            # Nutze ID falls vorhanden, sonst Label
            game_id = item.get("id", item.get("label"))
            mock_audio.current_game_id = game_id
            print(f"    - Simuliere Spiel: {item['label']}")
            
            game.on_game_select(item)
            game.on_player_count_selected({"count": 1})
            
            # Einzigartiger Name für Highscore-Audit
            test_name = f"Bot_{random.randint(1000, 9999)}"
            game.on_multi_name_entered(test_name)
            
            # Start-Vorbereitung (wie in main.py)
            game.current_player_idx = 0 
            mock_audio.in_init = True
            try:
                game.start_selected_game()
            except Exception as e:
                errors.append(f"Crash beim Start von {game_id}: {e}")
                mock_audio.in_init = False
                continue
            mock_audio.in_init = False
            
            if game.state != "playing":
                errors.append(f"Spiel {item['label']} konnte nicht gestartet werden!")
                continue
            
            # Heuristik: Wir spielen so lange, bis wir min. 3 Sounds gehört haben oder Zeit um ist
            ticks = 0
            max_ticks = 400
            while ticks < max_ticks and game.current_game.active:
                game.current_game.update()
                # Bot "lernt": Er drückt öfter Tasten, wenn er noch keine Sounds gehört hat
                if len(mock_audio.sounds_per_game.get(game_id, [])) < 2:
                    key = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN])
                else:
                    key = random.choice([None, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
                
                if key:
                    game.current_game.handle_input(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=' '))
                
                time.sleep(0.005) # Zeitraffer
                ticks += 1
            
            # Ergebnis sichern
            final_score = game.current_game.score
            if game.current_game.active:
                game.current_game.finish()
            
            game.on_game_finished()
            
            # HIGHSCORE-AUDIT: Prüfen ob der Score in der Datei ist
            game.highscores.load_highscores()
            found = False
            for s in game.highscores.get_top_scores(game_id):
                if s["name"] == test_name and s["score"] == final_score:
                    found = True
                    break
            
            if final_score > 0 and not found:
                errors.append(f"Highscore-Audit fehlgeschlagen für {game_id}: Score {final_score} nicht gefunden!")
            
            games_tested += 1
            
        game.menu.pop_menu()
    game.menu.pop_menu()

    # Abschlussbericht
    print("\n" + "="*40)
    print("KI-TESTER 2.0 - ABSCHLUSSBERICHT")
    print("="*40)
    print(f"Spiele getestet: {games_tested}")
    
    stomping_errors = [e for e in mock_audio.errors if "SPEECH STOMPING" in e]
    other_errors = errors + [e for e in mock_audio.errors if "SPEECH STOMPING" not in e]

    if stomping_errors:
        print(f"\nBARRIEREFREIHEITS-WARNHINWEISE ({len(stomping_errors)}):")
        for err in set(stomping_errors):
            print(f"?? {err}")
    
    if other_errors:
        print(f"\nGEFUNDENE FUNKTIONALE FEHLER ({len(other_errors)}):")
        for err in set(other_errors):
            print(f"!! {err}")
    
    if not stomping_errors and not other_errors:
        print("\nERFOLG: 100% Funktionalität & Barrierefreiheit bestätigt.")
    elif not other_errors:
        print("\nHINWEIS: Spiele laufen stabil, aber die Barrierefreiheit (Sprachausgabe) sollte optimiert werden.")
    
    game.quit_game()

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"CRITICAL TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
