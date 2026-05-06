import os
import sys
import time
import random
import pygame
import json

# Path setup
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
sys.path.append(os.path.join(base_path, "core"))

# Dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1,1))

from main import MiniGameCollection
import localization

class MockAudio:
    def __init__(self, tester):
        self.tester = tester
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
        self.current_lang = "de"

    def speak(self, text, interrupt=True):
        now = time.time()
        self.current_lang = localization.get_language()
        
        # Stomping detection
        if interrupt and now - self.last_speak_time < 0.2 and self.last_speak_time > 0:
            self.tester.log_error(f"SPEECH STOMPING in {self.current_game_id}: '{text}' interrupted '{self.last_speech}' too quickly!")
        
        if self.in_init:
            self.tester.log_warn(f"{self.current_game_id} speaks during __init__. This might be interrupted by main instructions.")

        # Language leak detection
        if self.current_lang == "en" and any(word in text.lower() for word in ["drücke", "spiel", "ende", "punkte", "anleitung", "hauptmenü"]):
            self.tester.log_error(f"LANGUAGE LEAK in {self.current_game_id}: German text '{text}' detected in English mode!")

        self.speech_count += 1
        self.last_speech = text
        self.last_speak_time = now
        print(f"    [AUDIO] Speak ({self.current_lang}): {text}")

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
        found = False
        for fmt in ["ogg", "mp3", "wav"]:
            if os.path.exists(os.path.join(base_path, "assets", f"{name}.{fmt}")):
                found = True
                break
        if not found:
            self.tester.log_error(f"Missing audio file: {name} (in {self.current_game_id})")

    def set_volumes(self, sfx, music): pass
    def cleanup(self): pass

class AITesterV3:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.games_tested = 0
        self.current_lang = "de"
        self.report_path = os.path.join(base_path, "tools", "test_report_v3.md")

    def log_error(self, msg):
        self.errors.append(msg)
        print(f"  [ERROR]: {msg}")

    def log_warn(self, msg):
        self.warnings.append(msg)
        print(f"  [WARN]: {msg}")

    def run_full_suite(self):
        print("="*60)
        print("AI PLAYTESTER 3.0 - ADVANCED QA AGENT")
        print("="*60)
        
        languages = list(localization.TRANSLATIONS.keys())
        for lang in languages:
            print(f"\n>>> TESTING LANGUAGE: {lang.upper()}")
            self.current_lang = lang
            # Set language before starting the game instance
            localization.set_language(lang)
            self.test_all_games(lang)
            
        self.generate_report()

    def test_all_games(self, lang):
        game_collection = MiniGameCollection()
        mock_audio = MockAudio(self)
        game_collection.audio = mock_audio
        
        # Set language via settings
        game_collection.settings.set("language", lang)
        localization.set_language(lang)
        
        # Test Main Menu Navigation
        try:
            game_collection.setup_main_menu()
            game_collection.on_main_menu_select({"id": "play", "label": "Play"})
        except Exception as e:
            self.log_error(f"Main menu crash in {lang}: {e}")
            return

        categories = list(game_collection.menu.current_menu)
        for cat in categories:
            if cat.get("id") == "back": continue
            
            print(f"  -> Category: {cat['label']}")
            game_collection.on_category_select(cat)
            
            games_in_cat = list(game_collection.menu.current_menu)
            for item in games_in_cat:
                if item.get("id") == "back": continue
                
                game_id = item.get("id", "unknown")
                mock_audio.current_game_id = game_id
                print(f"    - Testing Game: {item['label']} ({game_id})")
                
                self.simulate_game(game_collection, item, mock_audio)
                self.games_tested += 1
            
            game_collection.menu.pop_menu()
        
        game_collection.quit_game()

    def simulate_game(self, collection, game_item, mock_audio):
        try:
            collection.on_game_select(game_item)
            collection.on_player_count_selected({"count": 1})
            
            test_name = f"QA_Bot_{random.randint(1000, 9999)}"
            collection.on_multi_name_entered(test_name)
            
            mock_audio.in_init = True
            collection.start_selected_game()
            mock_audio.in_init = False
            
            if collection.state != "playing":
                self.log_error(f"Game {game_item['label']} failed to enter 'playing' state.")
                return

            # Simulation loop
            ticks = 0
            max_ticks = 200 # Faster than real player but enough to trigger logic
            while ticks < max_ticks and collection.current_game.active:
                collection.current_game.update()
                
                # Intelligent input simulation
                if random.random() < 0.3: # 30% chance to press a key
                    key = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_RETURN, 49, 50, 51])
                    collection.current_game.handle_input(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=str(random.randint(0,9))))
                
                time.sleep(0.001)
                ticks += 1
            
            score = collection.current_game.score
            if collection.current_game.active:
                collection.current_game.finish()
            
            collection.on_game_finished()
            time.sleep(0.05) # Delay for highscore file writing
            
            # Audit highscore
            collection.highscores.load_highscores()
            found = False
            for s in collection.highscores.get_top_scores(mock_audio.current_game_id):
                if s["name"] == test_name and s["score"] == score:
                    found = True
                    break
            
            if score > 0 and not found:
                self.log_error(f"Highscore Audit Failed for {mock_audio.current_game_id} (Score: {score})")

        except Exception as e:
            self.log_error(f"Crash in {mock_audio.current_game_id}: {e}")
            import traceback
            traceback.print_exc()

    def generate_report(self):
        report = []
        report.append("# AI Playtester v3.0 QA Report")
        report.append(f"**Timestamp:** {time.ctime()}")
        report.append(f"**Total Games Tested:** {self.games_tested}")
        report.append(f"**Status:** {'?? FAILED' if self.errors else '?? PASSED'}")
        
        report.append("\n## Functional Errors")
        if self.errors:
            for err in set(self.errors):
                report.append(f"- !! {err}")
        else:
            report.append("- No functional errors found.")

        report.append("\n## Accessibility & Localization Warnings")
        if self.warnings:
            for warn in set(self.warnings):
                report.append(f"- ?? {warn}")
        else:
            report.append("- No accessibility issues found.")

        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        
        print(f"\nReport generated: {self.report_path}")

if __name__ == "__main__":
    tester = AITesterV3()
    tester.run_full_suite()
