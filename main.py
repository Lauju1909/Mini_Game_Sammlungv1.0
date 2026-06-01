import pygame
import sys
import os
import random
import math

# Pfade anpassen
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from audio import AudioManager
from settings_manager import SettingsManager
from highscore_manager import HighscoreManager
from menu_manager import MenuManager
from text_input import TextInput
import localization
from localization import get_text as _

# Import der Spiele
from games.golden_mic import GoldenMic
from games.beat_reaktor import BeatReaktor
from games.number_guess import NumberGuess
from games.sound_memo import SoundMemo
from games.math_blitz import MathBlitz
from games.key_storm import KeyStorm
from games.simon_says import SimonSays
from games.stereo_catch import StereoCatch
from games.bomb_defuser import BombDefuser
from games.safe_cracker import SafeCracker
from games.audio_maze import AudioMaze
from games.echolot import Echolot
from games.blind_farm import BlindFarm
from games.space_flight import SpaceFlight
from games.word_snake import WordSnake
from games.sound_quiz import SoundQuiz
from games.letter_salad import LetterSalad
from games.capital_hunter import CapitalHunter
from games.audio_bowling import AudioBowling
from games.rps_extreme import RPS_Extreme
from games.code_breaker import CodeBreaker
from games.sound_catch import SoundCatch
from games.speed_dial import SpeedDial
from games.mole_master import MoleMaster
from games.rhythm_master import RhythmMaster
from games.reaction_blitz import ReactionBlitz
from games.audio_archery import AudioArchery
from games.audio_slots import AudioSlots
from games.audio_sequence import AudioSequence
from games.echo_hunter import EchoHunter
from games.animal_radar import AnimalRadar
from games.morse_runner import MorseRunner
from games.ticking_clock import TickingClock
from games.pitch_perfect import PitchPerfect
from games.mystery_door import MysteryDoor
from games.frequency_jammer import FrequencyJammer
from games.stairs_of_fate import StairsOfFate
from games.sound_weaver import SoundWeaver
from games.beat_matcher import BeatMatcher
from games.audio_balance import AudioBalance
from games.audio_runner import AudioRunner
from games.submarine_sonar import SubmarineSonar
from games.audio_factory import AudioFactory
from games.dial_master import DialMaster
from games.spatial_memory import SpatialMemory
from games.audio_ping_pong import AudioPingPong
from games.audio_archery_pro import AudioArcheryPro
from games.rhythm_blacksmith import RhythmBlacksmith
from games.audio_defense import AudioDefense
from games.audio_boss import AudioBoss
from games.audio_racer import AudioRacer
from games.audio_minesweeper import AudioMinesweeper
from games.audio_frogger import AudioFrogger
from games.audio_battleship import AudioBattleship
from games.audio_mosquito import AudioMosquito

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.5, 0.5)
        self.size = random.uniform(2, 5)
        self.color = [random.randint(150, 255), random.randint(150, 255), 255, random.randint(50, 150)]
        self.life = random.uniform(100, 200)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.life < 50:
            self.color[3] = int(max(0, self.color[3] - 2))

    def draw(self, screen):
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, self.color, (self.size, self.size), self.size)
        screen.blit(s, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    def __init__(self, count=50):
        self.particles = [Particle(random.randint(0, 800), random.randint(0, 600)) for _ in range(count)]

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0 or p.x < 0 or p.x > 800 or p.y < 0 or p.y > 600:
                self.particles.remove(p)
                self.particles.append(Particle(random.randint(0, 800), random.randint(0, 600)))

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

class MiniGameCollection:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(_("app_title"))
        self.font_main = pygame.font.SysFont("Outfit, Inter, Arial", 32)
        self.font_small = pygame.font.SysFont("Outfit, Inter, Arial", 24)
        self.font_title = pygame.font.SysFont("Outfit, Inter, Arial", 48, bold=True)
        
        self.settings = SettingsManager("data/settings.json")
        
        # Sprache initialisieren
        # Sprache initialisieren
        lang = self.settings.get("language")
        if not lang:
            lang = localization.get_system_language()
            self.settings.set("language", lang)
        
        localization.set_language(lang)
        
        self.audio = AudioManager(self.settings)
        self.highscores = HighscoreManager("data/highscores.json")
        self.menu = MenuManager(self.audio)
        self.text_input = None
        self.current_highscore_data = {"game_name": "", "scores": []}
        
        self.players = []
        self.current_game = None
        self.state = "main_menu"
        self.particles = ParticleSystem(80)
        self.ui_time = 0
        self.score_bars_anim = {}
        self.running = True
        self.game_queue = []
        self.current_queue_index = 0
        self.setup_main_menu()
        self.audio.speak(_("ready"), interrupt=False, priority=2)

    def on_name_entered(self, name):
        if name:
            self.settings.set("player_name", name)
            self.players = [name]
            self.text_input = None
            self.state = "main_menu"
            self.setup_main_menu()
        else:
            # Fallback
            self.on_name_entered(_("default_player_name"))

    def setup_main_menu(self):
        items = [
            {"label": _("play"), "id": "play"},
            {"label": _("highscores"), "id": "highscores"},
            {"label": _("settings"), "id": "settings"},
            {"label": _("exit"), "id": "quit"}
        ]
        self.menu.clear_stack()
        self.menu.on_adjust_callback = None
        self.menu.set_menu(items, _("main_menu"))
        self.menu.on_select_callback = self.on_main_menu_select

    def on_main_menu_select(self, item):
        if item["id"] == "play":
            self.setup_categories()
        elif item["id"] == "highscores":
            self.setup_highscore_menu()
        elif item["id"] == "settings":
            self.setup_settings_menu()
        elif item["id"] == "quit":
            self.quit_game()

    def setup_categories(self):
        categories = self._get_categories_list()
        self.menu.push_menu(categories, _("select_category"))
        self.menu.on_select_callback = self.on_category_select

    def on_category_select(self, item):
        if item["id"] == "back":
            self.menu.pop_menu()
            return
        
        # Erzeuge eine Kopie der Spieleliste, um das Original nicht zu verändern
        game_list = list(item.get("games", []))
        if not any(g.get("id") == "back" for g in game_list):
            game_list.append({"label": _("back"), "id": "back"})
        
        self.menu.push_menu(game_list, _("games_in_category", cat=item['label']))
        self.menu.on_select_callback = self.on_game_select
        self.menu.on_toggle_callback = self.on_game_toggle

    def on_game_toggle(self, item):
        if item.get("id") == "back":
            return
        
        if not hasattr(self, 'game_queue'):
            self.game_queue = []
            
        if item in self.game_queue:
            self.game_queue.remove(item)
            self.audio.speak(item['label'] + " entfernt", interrupt=True)
        else:
            self.game_queue.append(item)
            self.audio.speak(item['label'] + " zur Playlist hinzugefügt", interrupt=True)

    def on_game_select(self, item):
        if item.get("id") == "back":
            self.menu.pop_menu()
            return

        if not hasattr(self, 'game_queue'):
            self.game_queue = []

        if not self.game_queue:
            self.game_queue = [item]
        elif item not in self.game_queue:
            # If they just hit ENTER on a game not in queue, clear queue and play this one
            self.game_queue = [item]
            
        self.current_queue_index = 0
        self.selected_game_item = self.game_queue[0]

        # Frage nach Spieleranzahl
        items = [
            {"label": _("player_count_item", count=1), "count": 1},
            {"label": _("player_count_item", count=2), "count": 2},
            {"label": _("player_count_item", count=3), "count": 3},
            {"label": _("player_count_item", count=4), "count": 4},
            {"label": _("back"), "id": "back"}
        ]
        self.menu.push_menu(items, _("player_count_title", game=self.selected_game_item['label']))
        self.menu.on_select_callback = self.on_player_count_selected
        self.menu.on_toggle_callback = None

    def on_player_count_selected(self, item):
        if item.get("id") == "back":
            self.menu.pop_menu()
            return
        
        self.target_player_count = item["count"]
        self.temp_players = []
        self.ask_next_player_name()

    def ask_next_player_name(self):
        player_idx = len(self.temp_players) + 1
        self.state = "name_input"
        prompt = _("name_input_prompt", idx=player_idx)
        self.text_input = TextInput(self.audio, prompt, self.on_multi_name_entered)

    def on_multi_name_entered(self, name):
        if name is None:
            # ESC wurde gedrückt -> Abbrechen
            self.state = "main_menu"
            self.text_input = None
            self.setup_main_menu()
            self.audio.speak(_("aborted_main_menu"), interrupt=True, priority=2)
            return

        self.temp_players.append(name)
        
        if len(self.temp_players) < self.target_player_count:
            self.ask_next_player_name()
        else:
            self.players = self.temp_players
            self.state = "description"
            desc = self.selected_game_item.get("desc", _("no_desc_available"))
            self.audio.speak(_("game_desc_start", desc=desc), interrupt=True, priority=2)

    def start_selected_game(self):
        game_class = self.selected_game_item.get("class")
        if game_class:
            self.current_player_idx = 0
            self.session_scores = {}
            self.audio.speak(_("first_player", player=self.players[0]), priority=2)
            self.current_game = game_class(self.audio, self.highscores, self.settings, self.players[0])
            
            # Tutorial Check
            completed = self.settings.get("completed_tutorials", [])
            game_id = self.selected_game_item.get("id")
            
            if game_id not in completed:
                self.state = "tutorial"
                self.current_game.start_tutorial()
            else:
                self.state = "playing"
                self.current_game.start()

    def setup_settings_menu(self):
        items = [
            {"label": _("settings_sfx_vol", vol=self.settings.get('volume_sfx')), "id": "vol_sfx"},
            {"label": _("settings_music_vol", vol=self.settings.get('volume_music')), "id": "vol_music"},
            {"label": _("settings_speech_rate", rate=self.settings.get('speech_rate')), "id": "speech_rate"},
            {"label": _("settings_lang", lang=self.settings.get('language')), "id": "language"},
            {"label": _("settings_speech_vol", vol=self.settings.get('speech_volume')), "id": "speech_vol"},
            {"label": _("back"), "id": "back"}
        ]
        self.menu.push_menu(items, _("settings"))
        self.menu.on_select_callback = self.on_settings_select
        self.menu.on_adjust_callback = self.on_settings_adjust

    def on_settings_adjust(self, item, direction):
        if item["id"] == "vol_sfx":
            vol = self.settings.get("volume_sfx")
            if (vol == 0 and direction < 0) or (vol == 100 and direction > 0):
                self.audio.play_sound("bump")
            else:
                new_vol = max(0, min(100, vol + direction * 10))
                self.settings.set("volume_sfx", new_vol)
                self.audio.set_volumes(new_vol, self.settings.get("volume_music"))
                item["label"] = _("settings_sfx_vol", vol=new_vol)
                self.audio.speak(item["label"])
        elif item["id"] == "vol_music":
            vol = self.settings.get("volume_music")
            if (vol == 0 and direction < 0) or (vol == 100 and direction > 0):
                self.audio.play_sound("bump")
            else:
                new_vol = max(0, min(100, vol + direction * 10))
                self.settings.set("volume_music", new_vol)
                self.audio.set_volumes(self.settings.get("volume_sfx"), new_vol)
                item["label"] = _("settings_music_vol", vol=new_vol)
                self.audio.speak(item["label"])
        elif item["id"] == "speech_rate":
            rate = self.settings.get("speech_rate")
            if (rate == 30 and direction < 0) or (rate == 100 and direction > 0):
                self.audio.play_sound("bump")
            else:
                new_rate = max(30, min(100, rate + direction * 10))
                self.settings.set("speech_rate", new_rate)
                self.audio.set_speech_rate(new_rate)
                item["label"] = _("settings_speech_rate", rate=new_rate)
                self.audio.speak(item["label"])
        elif item["id"] == "speech_vol":
            vol = self.settings.get("speech_volume")
            if (vol == 0 and direction < 0) or (vol == 100 and direction > 0):
                self.audio.play_sound("bump")
            else:
                new_vol = max(0, min(100, vol + direction * 10))
                self.settings.set("speech_volume", new_vol)
                self.audio.set_speech_volume(new_vol)
                item["label"] = _("settings_speech_vol", vol=new_vol)
                self.audio.speak(item["label"])
        elif item["id"] == "language":
            langs = ["de", "en"]
            current = self.settings.get("language")
            idx = langs.index(current)
            if (idx == 0 and direction < 0) or (idx == len(langs)-1 and direction > 0):
                self.audio.play_sound("bump")
            else:
                new_idx = idx + direction
                new_lang = langs[new_idx]
                self.settings.set("language", new_lang)
                localization.set_language(new_lang)
                self.refresh_settings_menu_labels()
                self.menu.current_title = _("settings")
                self.refresh_all_menu_stacks()
                self.audio.speak(_("language_changed"), interrupt=False, priority=2)

    def on_settings_select(self, item):
        if item["id"] == "back":
            self.menu.pop_menu()
            return
        
        if item["id"] == "language":
            current = self.settings.get("language")
            new_lang = "en" if current == "de" else "de"
            self.settings.set("language", new_lang)
            localization.set_language(new_lang)
            
            # Alle Menü-Labels im aktuellen Menü (Einstellungen) aktualisieren
            self.refresh_settings_menu_labels()
            
            # Die Titel-Attribute im Stack und das aktuelle Menu aktualisieren
            self.menu.current_title = _("settings")
            self.refresh_all_menu_stacks()
            self.audio.speak(_("language_changed"), interrupt=False)
        else:
            # Fallback für Enter
            self.on_settings_adjust(item, 1)

    def refresh_all_menu_stacks(self):
        """Aktualisiert alle Menüs im Stack auf die neue Sprache."""
        # Das aktuelle Menü-Titel-Attribut aktualisieren
        self.menu.current_title = _("settings")
        
        for i, stack_item in enumerate(self.menu.menu_stack):
            items, index, sel_cb, adj_cb, title = stack_item
            
            # Identifiziere das Menü anhand seiner IDs und übersetze es neu
            if any(it.get("id") == "play" for it in items):
                new_items = [
                    {"label": _("play"), "id": "play"},
                    {"label": _("highscores"), "id": "highscores"},
                    {"label": _("settings"), "id": "settings"},
                    {"label": _("exit"), "id": "quit"}
                ]
                self.menu.menu_stack[i] = (new_items, index, sel_cb, adj_cb, _("main_menu"))
            
            elif any(it.get("id") == "action" for it in items):
                # Kategorien-Menü
                new_items = self._get_categories_list()
                self.menu.menu_stack[i] = (new_items, index, sel_cb, adj_cb, _("select_category"))
            
            elif any(it.get("class") is not None for it in items):
                # Spiele-Liste
                new_items = []
                cat_label = _("select_game")
                for it in items:
                    if it.get("id") == "back":
                        new_items.append({"label": _("back"), "id": "back"})
                    else:
                        all_cats = self._get_categories_list()
                        found = False
                        for cat in all_cats:
                            for game in cat.get("games", []):
                                if game["id"] == it["id"]:
                                    new_items.append(game)
                                    cat_label = _("games_in_category", cat=cat["label"])
                                    found = True
                                    break
                            if found: break
                self.menu.menu_stack[i] = (new_items, index, sel_cb, adj_cb, cat_label)
                
            elif any(it.get("id") == "h_action" for it in items):
                new_items = [
                    {"label": _("cat_action"), "id": "h_action"},
                    {"label": _("cat_logic"), "id": "h_logic"},
                    {"label": _("cat_nav"), "id": "h_nav"},
                    {"label": _("cat_speech"), "id": "h_speech"},
                    {"label": _("cat_sim"), "id": "h_sim"},
                    {"label": _("back"), "id": "back"}
                ]
                self.menu.menu_stack[i] = (new_items, index, sel_cb, adj_cb, _("highscores"))

    def _get_categories_list(self):
        """Hilfsfunktion zur Erzeugung der Kategorienliste (lokalisiert)."""
        return [
            {"label": _("cat_action"), "id": "action", "games": [
                {"label": _("game_beat_reaktor"), "id": "beat_reaktor", "class": BeatReaktor, "desc": _("game_beat_reaktor_desc")},
                {"label": _("game_stereo_catch"), "id": "stereo_catch", "class": StereoCatch, "desc": _("game_stereo_catch_desc")},
                {"label": _("game_sound_catch"), "id": "sound_catch", "class": SoundCatch, "desc": _("game_sound_catch_desc")},
                {"label": _("game_bomb_defuser"), "id": "bomb_defuser", "class": BombDefuser, "desc": _("game_bomb_defuser_desc")},
                {"label": _("game_key_storm"), "id": "key_storm", "class": KeyStorm, "desc": _("game_key_storm_desc")},
                {"label": _("game_speed_dial"), "id": "speed_dial", "class": SpeedDial, "desc": _("game_speed_dial_desc")},
                {"label": _("game_mole_master"), "id": "mole_master", "class": MoleMaster, "desc": _("game_mole_master_desc")},
                {"label": _("game_rhythm_master"), "id": "rhythm_master", "class": RhythmMaster, "desc": _("game_rhythm_master_desc")},
                {"label": _("game_reaction_blitz"), "id": "reaction_blitz", "class": ReactionBlitz, "desc": _("game_reaction_blitz_desc")},
                {"label": _("game_audio_archery"), "id": "audio_archery", "class": AudioArchery, "desc": _("game_audio_archery_desc")},
                {"label": _("game_audio_archery_pro"), "id": "audio_archery_pro", "class": AudioArcheryPro, "desc": _("game_audio_archery_pro_desc")},
                {"label": _("game_rhythm_blacksmith"), "id": "rhythm_blacksmith", "class": RhythmBlacksmith, "desc": _("game_rhythm_blacksmith_desc")},
                {"label": _("game_audio_defense"), "id": "audio_defense", "class": AudioDefense, "desc": _("game_audio_defense_desc")},
                {"label": _("game_audio_boss"), "id": "audio_boss", "class": AudioBoss, "desc": _("game_audio_boss_desc")},
                {"label": _("game_audio_racer"), "id": "audio_racer", "class": AudioRacer, "desc": _("game_audio_racer_desc")},
                {"label": _("game_audio_frogger"), "id": "audio_frogger", "class": AudioFrogger, "desc": _("game_audio_frogger_desc")},
                {"label": _("game_audio_mosquito"), "id": "audio_mosquito", "class": AudioMosquito, "desc": _("game_audio_mosquito_desc")},
                {"label": _("game_beat_matcher"), "id": "beat_matcher", "class": BeatMatcher, "desc": _("game_beat_matcher_desc")},
                {"label": _("game_audio_ping_pong"), "id": "audio_ping_pong", "class": AudioPingPong, "desc": _("game_audio_ping_pong_desc")},
                {"label": _("game_audio_balance"), "id": "audio_balance", "class": AudioBalance, "desc": _("game_audio_balance_desc")},
                {"label": _("game_audio_runner"), "id": "audio_runner", "class": AudioRunner, "desc": _("game_audio_runner_desc")},
                {"label": _("game_audio_factory"), "id": "audio_factory", "class": AudioFactory, "desc": _("game_audio_factory_desc")},
                {"label": _("game_morse_runner"), "id": "morse_runner", "class": MorseRunner, "desc": _("game_morse_runner_desc")}
            ]},
            {"label": _("cat_logic"), "id": "logic", "games": [
                {"label": _("game_sound_memo"), "id": "sound_memo", "class": SoundMemo, "desc": _("game_sound_memo_desc")},
                {"label": _("game_simon_says"), "id": "simon_says", "class": SimonSays, "desc": _("game_simon_says_desc")},
                {"label": _("game_spatial_memory"), "id": "spatial_memory", "class": SpatialMemory, "desc": _("game_spatial_memory_desc")},
                {"label": _("game_code_breaker"), "id": "code_breaker", "class": CodeBreaker, "desc": _("game_code_breaker_desc")},
                {"label": _("game_number_guess"), "id": "number_guess", "class": NumberGuess, "desc": _("game_number_guess_desc")},
                {"label": _("game_safe_cracker"), "id": "safe_cracker", "class": SafeCracker, "desc": _("game_safe_cracker_desc")},
                {"label": _("game_dial_master"), "id": "dial_master", "class": DialMaster, "desc": _("game_dial_master_desc")},
                {"label": _("game_math_blitz"), "id": "math_blitz", "class": MathBlitz, "desc": _("game_math_blitz_desc")},
                {"label": _("game_ticking_clock"), "id": "ticking_clock", "class": TickingClock, "desc": _("game_ticking_clock_desc")},
                {"label": _("game_pitch_perfect"), "id": "pitch_perfect", "class": PitchPerfect, "desc": _("game_pitch_perfect_desc")},
                {"label": _("game_sound_weaver"), "id": "sound_weaver", "class": SoundWeaver, "desc": _("game_sound_weaver_desc")},
                {"label": _("game_audio_sequence"), "id": "audio_sequence", "class": AudioSequence, "desc": _("game_audio_sequence_desc")},
                {"label": _("game_audio_minesweeper"), "id": "audio_minesweeper", "class": AudioMinesweeper, "desc": _("game_audio_minesweeper_desc")},
                {"label": _("game_audio_battleship"), "id": "audio_battleship", "class": AudioBattleship, "desc": _("game_audio_battleship_desc")}
            ]},
            {"label": _("cat_nav"), "id": "nav", "games": [
                {"label": _("game_golden_mic"), "id": "golden_mic", "class": GoldenMic, "desc": _("game_golden_mic_desc")},
                {"label": _("game_audio_maze"), "id": "audio_maze", "class": AudioMaze, "desc": _("game_audio_maze_desc")},
                {"label": _("game_echolot"), "id": "echolot", "class": Echolot, "desc": _("game_echolot_desc")},
                {"label": _("game_blind_farm"), "id": "blind_farm", "class": BlindFarm, "desc": _("game_blind_farm_desc")},
                {"label": _("game_space_flight"), "id": "space_flight", "class": SpaceFlight, "desc": _("game_space_flight_desc")},
                {"label": _("game_animal_radar"), "id": "animal_radar", "class": AnimalRadar, "desc": _("game_animal_radar_desc")},
                {"label": _("game_mystery_door"), "id": "mystery_door", "class": MysteryDoor, "desc": _("game_mystery_door_desc")},
                {"label": _("game_frequency_jammer"), "id": "frequency_jammer", "class": FrequencyJammer, "desc": _("game_frequency_jammer_desc")},
                {"label": _("game_stairs_of_fate"), "id": "stairs_of_fate", "class": StairsOfFate, "desc": _("game_stairs_of_fate_desc")},
                {"label": _("game_submarine_sonar"), "id": "submarine_sonar", "class": SubmarineSonar, "desc": _("game_submarine_sonar_desc")}
            ]},
            {"label": _("cat_speech"), "id": "speech", "games": [
                {"label": _("game_word_snake"), "id": "word_snake", "class": WordSnake, "desc": _("game_word_snake_desc")},
                {"label": _("game_sound_quiz"), "id": "sound_quiz", "class": SoundQuiz, "desc": _("game_sound_quiz_desc")},
                {"label": _("game_letter_salad"), "id": "letter_salad", "class": LetterSalad, "desc": _("game_letter_salad_desc")},
                {"label": _("game_capital_hunter"), "id": "capital_hunter", "class": CapitalHunter, "desc": _("game_capital_hunter_desc")}
            ]},
            {"label": _("cat_sim"), "id": "sim", "games": [
                {"label": _("game_audio_bowling"), "id": "audio_bowling", "class": AudioBowling, "desc": _("game_audio_bowling_desc")},
                {"label": _("game_rps_extreme"), "id": "rps_extreme", "class": RPS_Extreme, "desc": _("game_rps_extreme_desc")},
                {"label": _("game_audio_slots"), "id": "audio_slots", "class": AudioSlots, "desc": _("game_audio_slots_desc")},
                {"label": _("game_echo_hunter"), "id": "echo_hunter", "class": EchoHunter, "desc": _("game_echo_hunter_desc")}
            ]},
            {"label": _("cat_all"), "id": "all", "games": [
                {"label": _("game_beat_reaktor"), "id": "beat_reaktor", "class": BeatReaktor, "desc": _("game_beat_reaktor_desc")},
                {"label": _("game_stereo_catch"), "id": "stereo_catch", "class": StereoCatch, "desc": _("game_stereo_catch_desc")},
                {"label": _("game_sound_catch"), "id": "sound_catch", "class": SoundCatch, "desc": _("game_sound_catch_desc")},
                {"label": _("game_bomb_defuser"), "id": "bomb_defuser", "class": BombDefuser, "desc": _("game_bomb_defuser_desc")},
                {"label": _("game_key_storm"), "id": "key_storm", "class": KeyStorm, "desc": _("game_key_storm_desc")},
                {"label": _("game_speed_dial"), "id": "speed_dial", "class": SpeedDial, "desc": _("game_speed_dial_desc")},
                {"label": _("game_mole_master"), "id": "mole_master", "class": MoleMaster, "desc": _("game_mole_master_desc")},
                {"label": _("game_rhythm_master"), "id": "rhythm_master", "class": RhythmMaster, "desc": _("game_rhythm_master_desc")},
                {"label": _("game_reaction_blitz"), "id": "reaction_blitz", "class": ReactionBlitz, "desc": _("game_reaction_blitz_desc")},
                {"label": _("game_audio_archery"), "id": "audio_archery", "class": AudioArchery, "desc": _("game_audio_archery_desc")},
                {"label": _("game_sound_memo"), "id": "sound_memo", "class": SoundMemo, "desc": _("game_sound_memo_desc")},
                {"label": _("game_simon_says"), "id": "simon_says", "class": SimonSays, "desc": _("game_simon_says_desc")},
                {"label": _("game_spatial_memory"), "id": "spatial_memory", "class": SpatialMemory, "desc": _("game_spatial_memory_desc")},
                {"label": _("game_audio_sequence"), "id": "audio_sequence", "class": AudioSequence, "desc": _("game_audio_sequence_desc")},
                {"label": _("game_code_breaker"), "id": "code_breaker", "class": CodeBreaker, "desc": _("game_code_breaker_desc")},
                {"label": _("game_number_guess"), "id": "number_guess", "class": NumberGuess, "desc": _("game_number_guess_desc")},
                {"label": _("game_safe_cracker"), "id": "safe_cracker", "class": SafeCracker, "desc": _("game_safe_cracker_desc")},
                {"label": _("game_dial_master"), "id": "dial_master", "class": DialMaster, "desc": _("game_dial_master_desc")},
                {"label": _("game_math_blitz"), "id": "math_blitz", "class": MathBlitz, "desc": _("game_math_blitz_desc")},
                {"label": _("game_golden_mic"), "id": "golden_mic", "class": GoldenMic, "desc": _("game_golden_mic_desc")},
                {"label": _("game_audio_maze"), "id": "audio_maze", "class": AudioMaze, "desc": _("game_audio_maze_desc")},
                {"label": _("game_echolot"), "id": "echolot", "class": Echolot, "desc": _("game_echolot_desc")},
                {"label": _("game_blind_farm"), "id": "blind_farm", "class": BlindFarm, "desc": _("game_blind_farm_desc")},
                {"label": _("game_space_flight"), "id": "space_flight", "class": SpaceFlight, "desc": _("game_space_flight_desc")},
                {"label": _("game_word_snake"), "id": "word_snake", "class": WordSnake, "desc": _("game_word_snake_desc")},
                {"label": _("game_sound_quiz"), "id": "sound_quiz", "class": SoundQuiz, "desc": _("game_sound_quiz_desc")},
                {"label": _("game_letter_salad"), "id": "letter_salad", "class": LetterSalad, "desc": _("game_letter_salad_desc")},
                {"label": _("game_capital_hunter"), "id": "capital_hunter", "class": CapitalHunter, "desc": _("game_capital_hunter_desc")},
                {"label": _("game_audio_bowling"), "id": "audio_bowling", "class": AudioBowling, "desc": _("game_audio_bowling_desc")},
                {"label": _("game_rps_extreme"), "id": "rps_extreme", "class": RPS_Extreme, "desc": _("game_rps_extreme_desc")},
                {"label": _("game_audio_slots"), "id": "audio_slots", "class": AudioSlots, "desc": _("game_audio_slots_desc")},
                {"label": _("game_animal_radar"), "id": "animal_radar", "class": AnimalRadar, "desc": _("game_animal_radar_desc")},
                {"label": _("game_morse_runner"), "id": "morse_runner", "class": MorseRunner, "desc": _("game_morse_runner_desc")},
                {"label": _("game_ticking_clock"), "id": "ticking_clock", "class": TickingClock, "desc": _("game_ticking_clock_desc")},
                {"label": _("game_pitch_perfect"), "id": "pitch_perfect", "class": PitchPerfect, "desc": _("game_pitch_perfect_desc")},
                {"label": _("game_mystery_door"), "id": "mystery_door", "class": MysteryDoor, "desc": _("game_mystery_door_desc")},
                {"label": _("game_frequency_jammer"), "id": "frequency_jammer", "class": FrequencyJammer, "desc": _("game_frequency_jammer_desc")},
                {"label": _("game_stairs_of_fate"), "id": "stairs_of_fate", "class": StairsOfFate, "desc": _("game_stairs_of_fate_desc")},
                {"label": _("game_audio_archery_pro"), "id": "audio_archery_pro", "class": AudioArcheryPro, "desc": _("game_audio_archery_pro_desc")},
                {"label": _("game_rhythm_blacksmith"), "id": "rhythm_blacksmith", "class": RhythmBlacksmith, "desc": _("game_rhythm_blacksmith_desc")},
                {"label": _("game_audio_defense"), "id": "audio_defense", "class": AudioDefense, "desc": _("game_audio_defense_desc")},
                {"label": _("game_audio_boss"), "id": "audio_boss", "class": AudioBoss, "desc": _("game_audio_boss_desc")},
                {"label": _("game_audio_racer"), "id": "audio_racer", "class": AudioRacer, "desc": _("game_audio_racer_desc")},
                {"label": _("game_audio_minesweeper"), "id": "audio_minesweeper", "class": AudioMinesweeper, "desc": _("game_audio_minesweeper_desc")},
                {"label": _("game_audio_frogger"), "id": "audio_frogger", "class": AudioFrogger, "desc": _("game_audio_frogger_desc")},
                {"label": _("game_audio_battleship"), "id": "audio_battleship", "class": AudioBattleship, "desc": _("game_audio_battleship_desc")},
                {"label": _("game_audio_mosquito"), "id": "audio_mosquito", "class": AudioMosquito, "desc": _("game_audio_mosquito_desc")},
                {"label": _("game_beat_matcher"), "id": "beat_matcher", "class": BeatMatcher, "desc": _("game_beat_matcher_desc")},
                {"label": _("game_audio_ping_pong"), "id": "audio_ping_pong", "class": AudioPingPong, "desc": _("game_audio_ping_pong_desc")},
                {"label": _("game_audio_balance"), "id": "audio_balance", "class": AudioBalance, "desc": _("game_audio_balance_desc")},
                {"label": _("game_audio_runner"), "id": "audio_runner", "class": AudioRunner, "desc": _("game_audio_runner_desc")},
                {"label": _("game_audio_factory"), "id": "audio_factory", "class": AudioFactory, "desc": _("game_audio_factory_desc")},
                {"label": _("game_submarine_sonar"), "id": "submarine_sonar", "class": SubmarineSonar, "desc": _("game_submarine_sonar_desc")},
                {"label": _("game_morse_runner"), "id": "morse_runner", "class": MorseRunner, "desc": _("game_morse_runner_desc")}
            ]},
            {"label": _("back"), "id": "back"}
        ]

    def refresh_settings_menu_labels(self):
        for m_item in self.menu.current_menu:
            i_id = m_item.get("id")
            if i_id == "vol_sfx":
                m_item["label"] = _("settings_sfx_vol", vol=self.settings.get("volume_sfx"))
            elif i_id == "vol_music":
                m_item["label"] = _("settings_music_vol", vol=self.settings.get("volume_music"))
            elif i_id == "speech_rate":
                m_item["label"] = _("settings_speech_rate", rate=self.settings.get("speech_rate"))
            elif i_id == "speech_vol":
                m_item["label"] = _("settings_speech_vol", vol=self.settings.get("speech_volume"))
            elif i_id == "language":
                m_item["label"] = _("settings_lang", lang=self.settings.get("language"))
            elif i_id == "back":
                m_item["label"] = _("back")
        self.menu._announce_current()

    def setup_highscore_menu(self):
        # Zeige Kategorien für Highscores
        items = [
            {"label": _("cat_action"), "id": "h_action"},
            {"label": _("cat_logic"), "id": "h_logic"},
            {"label": _("cat_nav"), "id": "h_nav"},
            {"label": _("cat_speech"), "id": "h_speech"},
            {"label": _("cat_sim"), "id": "h_sim"},
            {"label": _("cat_all"), "id": "h_all"},
            {"label": _("back"), "id": "back"}
        ]
        self.menu.push_menu(items, _("highscores"))
        self.menu.on_select_callback = self.on_highscore_category_select

    def on_highscore_category_select(self, item):
        if item["id"] == "back":
            self.menu.pop_menu()
            return
        
        target_cat_id = item["id"].replace("h_", "")
        all_cats = self._get_categories_list()
        
        if target_cat_id == "all":
            all_scores = []
            for cat in all_cats:
                if cat["id"] == "all": continue
                for game in cat.get("games", []):
                    scores = self.highscores.get_scores(game["id"])
                    for s in scores:
                        all_scores.append({
                            "name": f"{s['name']} ({game['label']})",
                            "score": s['score']
                        })
            all_scores.sort(key=lambda x: x["score"], reverse=True)
            self.current_highscore_data = {"game_name": _("cat_all"), "scores": all_scores[:20]}
            self.state = "viewing_highscores"
            self.audio.speak(_("highscore_category", cat=_("cat_all")))
            return

        target_cat = next((c for c in all_cats if c["id"] == target_cat_id), None)
        if not target_cat:
            self.menu.pop_menu()
            return

        items = []
        for game_info in target_cat.get("games", []):
            g_id = game_info["id"]
            scores = self.highscores.get_scores(g_id)
            if scores:
                top = scores[0]
                label = f"{game_info['label']} - Top: {top['name']} ({top['score']})"
                items.append({"label": label, "id": g_id, "scores": scores, "game_title": game_info['label']})
        
        if not items:
            self.audio.speak(_("no_highscores_in_category"))
            return

        items.append({"label": _("back"), "id": "back"})
        self.menu.push_menu(items, _("games_in_category", cat=target_cat["label"]))
        self.menu.on_select_callback = self.on_show_scores

    def on_show_scores(self, item):
        if item["id"] == "back":
            self.menu.pop_menu()
            return
        
        scores = item["scores"]
        # Animation zurücksetzen
        self.score_bars_anim[item["id"]] = 0.0
        # Wir zeigen die Highscores jetzt grafisch an
        self.state = "viewing_highscores"
        self.current_highscore_data = {
            "game_name": item.get("game_title", item["label"]),
            "scores": scores,
            "id": item["id"],
            "index": 0
        }
        self.audio.speak(_("highscore_for", game=self.current_highscore_data["game_name"]), interrupt=True, priority=1)
        if not scores:
            self.audio.speak(_("no_highscores"), interrupt=False)
        else:
            # Ansage der Top 3 für Barrierefreiheit
            for i, s in enumerate(scores[:3]):
                self.audio.speak(_("score_entry", idx=i+1, name=s['name'], score=s['score']), interrupt=False)

    def draw_gradient_rect(self, rect, color1, color2):
        """Zeichnet ein Rechteck mit einem vertikalen Gradienten."""
        target_rect = pygame.Rect(rect)
        color_rect = pygame.Surface((2, 2))
        pygame.draw.line(color_rect, color1, (0, 0), (1, 0))
        pygame.draw.line(color_rect, color2, (0, 1), (1, 1))
        color_rect = pygame.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))
        self.screen.blit(color_rect, target_rect)

    def draw_glass_rect(self, rect, color=(255, 255, 255, 30), border_color=(255, 255, 255, 100)):
        """Zeichnet ein halbtransparentes Rechteck mit Rahmen (Glas-Effekt)."""
        shape_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, (0, 0, rect.width, rect.height), border_radius=15)
        pygame.draw.rect(shape_surf, border_color, (0, 0, rect.width, rect.height), width=2, border_radius=15)
        self.screen.blit(shape_surf, rect)

    def render_ui(self):
        # Dynamischer Hintergrund
        self.ui_time += 1
        t = self.ui_time * 0.01
        bg_color = (
            int(15 + 10 * math.sin(t)),
            int(15 + 10 * math.cos(t * 0.7)),
            int(35 + 15 * math.sin(t * 0.3))
        )
        self.screen.fill(bg_color)
        
        # Partikel im Hintergrund
        self.particles.update()
        self.particles.draw(self.screen)
        
        # Ein paar abstrakte Formen für den "WOW"-Effekt
        for i in range(3):
            angle = t * (0.5 + i * 0.2)
            dist = 200 + 50 * math.sin(t + i)
            pos = (400 + math.cos(angle) * dist, 300 + math.sin(angle) * dist)
            s = pygame.Surface((300, 300), pygame.SRCALPHA)
            pygame.draw.circle(s, (100, 100, 255, 10), (150, 150), 150)
            self.screen.blit(s, (pos[0]-150, pos[1]-150))
        
        if self.state in ["main_menu", "playing", "tutorial", "description", "name_input", "viewing_highscores"]:
            # Titel des aktuellen Menüs oder Zustands
            title_text = ""
            if self.state == "main_menu":
                title_text = self.menu.current_title
            elif self.state == "description":
                title_text = self.selected_game_item["label"]
            elif self.state == "viewing_highscores":
                title_text = self.current_highscore_data["game_name"]
            elif self.state == "waiting_for_next_player":
                title_text = _("round_ended_next_player", player=self.players[self.current_player_idx]).split('.')[0]
            
            if title_text:
                surf = self.font_title.render(title_text, True, (255, 255, 255))
                self.screen.blit(surf, (40, 40))

        if self.state == "main_menu":
            # Menü-Items rendern
            menu_rect = pygame.Rect(40, 120, 720, 440)
            self.draw_glass_rect(menu_rect)
            
            for i, item in enumerate(self.menu.current_menu):
                is_selected = (i == self.menu.index)
                color = (255, 215, 0) if is_selected else (200, 200, 200)
                if is_selected:
                    # Selektions-Hintergrund
                    sel_rect = pygame.Rect(50, 130 + i * 50, 700, 45)
                    pygame.draw.rect(self.screen, (255, 255, 255, 40), sel_rect, border_radius=10)
                
                label = item["label"]
                text_surf = self.font_main.render(label, True, color)
                self.screen.blit(text_surf, (70, 135 + i * 50))

        elif self.state == "viewing_highscores":
            # Highscore-Tabelle rendern
            scores = self.current_highscore_data["scores"]
            game_name = self.current_highscore_data["game_name"]
            
            # Hintergrund-Panel
            panel_rect = pygame.Rect(40, 100, 720, 460)
            self.draw_glass_rect(panel_rect, color=(20, 20, 40, 180), border_color=(100, 100, 255, 150))
            
            # Überschrift
            title_surf = self.font_title.render(game_name, True, (255, 255, 255))
            self.screen.blit(title_surf, (panel_rect.centerx - title_surf.get_width()//2, 115))
            
            # Trennlinie
            pygame.draw.line(self.screen, (255, 215, 0, 150), (100, 175), (700, 175), 2)
            
            if not scores:
                text = self.font_main.render(_("no_highscores"), True, (150, 150, 150))
                self.screen.blit(text, (400 - text.get_width()//2, 280))
            else:
                # Tabellenkopf (optional, aber schöner)
                header_y = 135
                name_hdr = self.font_small.render("NAME", True, (150, 150, 150))
                score_hdr = self.font_small.render(_("points").upper(), True, (150, 150, 150))
                self.screen.blit(name_hdr, (150, header_y))
                self.screen.blit(score_hdr, (600, header_y))
                pygame.draw.line(self.screen, (255, 255, 255, 50), (60, 160), (740, 160), 1)

                # Animation der Balken
                game_key = self.current_highscore_data.get("id", "default")
                anim_progress = self.score_bars_anim.get(game_key, 0.0)
                if anim_progress < 1.0:
                    self.score_bars_anim[game_key] = min(1.0, anim_progress + 0.05)
                    anim_progress = self.score_bars_anim[game_key]

                for i, s in enumerate(scores[:10]):
                    y_pos = 175 + i * 38
                    # Farbe basierend auf Rang
                    rank_color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50) if i == 2 else (255, 255, 255)
                    
                    # Glaskasten-Effekt für jeden Eintrag
                    entry_rect = pygame.Rect(60, y_pos - 5, 680, 34)
                    bg_alpha = 40 if i == 0 else 25 if i % 2 == 0 else 10
                    pygame.draw.rect(self.screen, (255, 255, 255, bg_alpha), entry_rect, border_radius=10)
                    
                    # Spezial-Effekt für Platz 1
                    if i == 0:
                        # Goldener Schimmer-Rahmen
                        shimmer = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0
                        pygame.draw.rect(self.screen, (255, 215, 0, int(150 * shimmer)), entry_rect, width=2, border_radius=10)
                    
                    # Medaillen-Icon Ersatz
                    if i < 3:
                        medal_colors = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
                        # Glow Effekt
                        for r in range(5):
                            pygame.draw.circle(self.screen, (*medal_colors[i], 50 - r*10), (85, y_pos + 12), 14 + r, width=1)
                        pygame.draw.circle(self.screen, medal_colors[i], (85, y_pos + 12), 14)
                        rank_text = str(i+1)
                        rank_surf = self.font_small.render(rank_text, True, (0, 0, 0))
                        self.screen.blit(rank_surf, (85 - rank_surf.get_width()//2, y_pos + 12 - rank_surf.get_height()//2))
                    else:
                        rank_surf = self.font_main.render(f"{i+1}.", True, (150, 150, 150))
                        self.screen.blit(rank_surf, (75, y_pos - 5))
                    
                    name_surf = self.font_main.render(s['name'], True, (255, 255, 255))
                    score_surf = self.font_main.render(str(s['score']), True, rank_color)
                    
                    self.screen.blit(name_surf, (150, y_pos - 5))
                    self.screen.blit(score_surf, (600, y_pos - 5))

                    # Balkendiagramm für Sehende (Visualisierung der Punktzahl) mit Animation
                    max_score = scores[0]['score'] if scores[0]['score'] > 0 else 1
                    target_bar_width = int(350 * (s['score'] / max_score))
                    bar_width = int(target_bar_width * anim_progress)
                    bar_rect = pygame.Rect(150, y_pos + 22, bar_width, 4)
                    
                    # Hintergrund des Balkens (Spur)
                    pygame.draw.rect(self.screen, (255, 255, 255, 20), (150, y_pos + 22, target_bar_width, 4), border_radius=2)
                    
                    # Farbverlauf für den Balken simulieren
                    pygame.draw.rect(self.screen, rank_color, bar_rect, border_radius=2)
                    
                    # Kleiner Glow am Ende des Balkens
                    if bar_width > 5:
                        pygame.draw.circle(self.screen, (255, 255, 255, 150), (150 + bar_width, y_pos + 24), 3)
            
            hint_surf = self.font_small.render(_("instructions_base"), True, (150, 150, 150))
            self.screen.blit(hint_surf, (40, 570))

        elif self.state == "description":
            desc_rect = pygame.Rect(40, 120, 720, 400)
            self.draw_glass_rect(desc_rect)
            
            desc_text = self.selected_game_item.get("desc", _("no_desc_available"))
            # Textumbruch (einfach)
            words = desc_text.split(' ')
            lines = []
            current_line = ""
            for word in words:
                if self.font_main.size(current_line + word)[0] < 680:
                    current_line += word + " "
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
            for i, line in enumerate(lines):
                text_surf = self.font_main.render(line, True, (230, 230, 230))
                self.screen.blit(text_surf, (60, 140 + i * 40))
            
            start_hint = self.font_main.render(_("press_enter_to_start"), True, (0, 255, 127))
            self.screen.blit(start_hint, (250, 470))

        elif self.state == "name_input":
            input_rect = pygame.Rect(200, 250, 400, 100)
            self.draw_glass_rect(input_rect)
            if self.text_input:
                prompt_surf = self.font_main.render(self.text_input.prompt, True, (255, 255, 255))
                self.screen.blit(prompt_surf, (200, 200))
                val_surf = self.font_main.render(self.text_input.text + "_", True, (255, 215, 0))
                self.screen.blit(val_surf, (220, 275))
        
        elif self.state in ["playing", "tutorial"]:
            # Während des Spiels zeigen wir ein einfaches "Playing..." UI
            play_rect = pygame.Rect(40, 120, 720, 440)
            self.draw_glass_rect(play_rect)
            
            # Spielspezifische Grafik rendern
            if self.current_game:
                self.current_game.draw(self.screen)

            game_name = self.selected_game_item["label"]
            if self.state == "tutorial":
                game_name += " (Tutorial)"
                
            name_surf = self.font_main.render(game_name, True, (255, 215, 0))
            self.screen.blit(name_surf, (60, 530))
            
            player_surf = self.font_small.render(f"Spieler: {self.players[self.current_player_idx]}", True, (255, 255, 255))
            self.screen.blit(player_surf, (600, 535))

            hint_surf = self.font_small.render(_("instructions_base"), True, (150, 150, 150))
            self.screen.blit(hint_surf, (40, 570))

    def on_game_finished(self):
        if not hasattr(self, 'session_scores'):
            self.session_scores = {}
        if self.current_game:
            self.session_scores[self.players[self.current_player_idx]] = self.current_game.score
            
        self.current_player_idx += 1
        if self.current_player_idx < len(self.players):
            self.state = "waiting_for_next_player"
            self.audio.speak(_("round_ended_next_player", player=self.players[self.current_player_idx]))
        else:
            if len(self.players) > 1 and self.session_scores:
                max_score = max(self.session_scores.values())
                winners = [p for p, s in self.session_scores.items() if s == max_score]
                if len(winners) > 1:
                    import localization
                    lang = localization.get_language()
                    winners_str = " und ".join(winners) if lang == "de" else " and ".join(winners)
                    self.audio.speak(_("all_players_finished_tie", players=winners_str, score=max_score))
                else:
                    self.audio.speak(_("all_players_finished_winner", player=winners[0], score=max_score))
            else:
                self.audio.speak(_("all_players_finished"))
                
            if hasattr(self, 'game_queue') and self.current_queue_index + 1 < len(self.game_queue):
                self.current_queue_index += 1
                self.selected_game_item = self.game_queue[self.current_queue_index]
                self.state = "waiting_for_next_game"
                self.audio.speak(_("press_enter_to_start") + " " + self.selected_game_item["label"], interrupt=False)
            else:
                self.state = "main_menu"
                self.current_game = None
                self.game_queue = []
                self.setup_main_menu()

    def start_next_player_round(self):
        game_class = self.selected_game_item.get("class")
        self.current_game = game_class(self.audio, self.highscores, self.settings, self.players[self.current_player_idx])
        self.state = "playing"
        self.current_game.start()

    def handle_input(self, event):
        if self.state == "name_input" and self.text_input:
            self.text_input.handle_input(event)
        elif self.state == "description":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.start_selected_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "main_menu"
                self.game_queue = []
                self.setup_main_menu()
        elif self.state == "waiting_for_next_player":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.start_next_player_round()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "main_menu"
                self.game_queue = []
                self.setup_main_menu()
        elif self.state == "waiting_for_next_game":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.start_selected_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "main_menu"
                self.game_queue = []
                self.setup_main_menu()
        elif self.state == "viewing_highscores":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE]:
                    self.state = "main_menu"
                    self.menu.pop_menu() # Gehe zurück zur Spieleliste in der Highscore-Kategorie
                    return None
                elif event.key == pygame.K_UP:
                    scores = self.current_highscore_data["scores"]
                    if not scores:
                        self.audio.play_sound("bump")
                    elif self.current_highscore_data["index"] > 0:
                        self.current_highscore_data["index"] -= 1
                        idx = self.current_highscore_data["index"]
                        s = scores[idx]
                        self.audio.play_sound("click")
                        self.audio.speak(_("score_entry", idx=idx+1, name=s['name'], score=s['score']), interrupt=True)
                    else:
                        self.audio.play_sound("bump")
                elif event.key == pygame.K_DOWN:
                    scores = self.current_highscore_data["scores"]
                    if not scores:
                        self.audio.play_sound("bump")
                    elif self.current_highscore_data["index"] < len(scores) - 1:
                        self.current_highscore_data["index"] += 1
                        idx = self.current_highscore_data["index"]
                        s = scores[idx]
                        self.audio.play_sound("click")
                        self.audio.speak(_("score_entry", idx=idx+1, name=s['name'], score=s['score']), interrupt=True)
                    else:
                        self.audio.play_sound("bump")
        elif self.state == "main_menu":
            res = self.menu.handle_input(event)
            if res == "quit":
                return "quit"
        elif self.state in ["playing", "tutorial"] and self.current_game:
            self.current_game.handle_input(event)
            if self.state == "tutorial" and self.current_game.tutorial_finished:
                self.state = "playing"
                self.current_game.start()
            elif self.state == "playing" and not self.current_game.active:
                self.on_game_finished()
        return None

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if self.handle_input(event) == "quit":
                    self.running = False
                    running = False
                
            if self.state in ["playing", "tutorial"] and self.current_game:
                self.current_game.update()
                if self.state == "tutorial" and self.current_game.tutorial_finished:
                    self.state = "playing"
                    self.current_game.start()

            self.render_ui()
            pygame.display.flip()
            clock.tick(60)

        self.quit_game()

    def quit_game(self):
        self.audio.cleanup()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MiniGameCollection()
    game.run()
