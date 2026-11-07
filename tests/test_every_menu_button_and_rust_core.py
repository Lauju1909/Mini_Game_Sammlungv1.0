import ctypes
import glob
import os
import sys
import tempfile
import pygame
from unittest.mock import MagicMock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "core"))

from core.menu_manager import MenuManager
from core.settings_manager import SettingsManager
from core.highscore_manager import HighscoreManager
from core import localization


def test_rust_core_dll_ffi_and_wav_generation():
    dll_path = os.path.join(BASE_DIR, "mini_game_core.dll")
    assert os.path.isfile(dll_path), "mini_game_core.dll must exist"

    dll = ctypes.CDLL(dll_path)
    dll.rust_mg_generate_wav_file.argtypes = [
        ctypes.c_char_p,
        ctypes.c_float,
        ctypes.c_uint32,
        ctypes.c_float,
        ctypes.c_float,
        ctypes.c_uint8,
    ]
    dll.rust_mg_generate_wav_file.restype = ctypes.c_int32
    dll.rust_mg_verify_file_hash.argtypes = [ctypes.c_char_p]
    dll.rust_mg_verify_file_hash.restype = ctypes.c_uint64

    with tempfile.TemporaryDirectory() as tmp:
        for waveform in (0, 1, 2, 3):
            for pan in (-1.0, 0.0, 1.0):
                wav_path = os.path.join(tmp, f"tone_{waveform}_{pan}.wav").encode("utf-8")
                rc = dll.rust_mg_generate_wav_file(wav_path, 440.0, 60, 0.8, pan, waveform)
                assert rc == 0
                assert os.path.getsize(wav_path) > 44
                h1 = dll.rust_mg_verify_file_hash(wav_path)
                h2 = dll.rust_mg_verify_file_hash(wav_path)
                assert h1 != 0 and h1 == h2


def test_menu_manager_every_button_stack_and_navigation():
    audio = MagicMock()
    menu = MenuManager(audio)
    selected = []
    adjusted = []

    items = ["Spielen", "Ranglisten", "Einstellungen", "Sprache", "Beenden"]
    menu.on_select_callback = lambda item: selected.append(item)
    menu.on_adjust_callback = lambda item, delta: adjusted.append((item, delta))
    menu.set_menu(items, title="Hauptmenü")
    assert audio.speak.called

    # Boundary bump at top
    ev_up = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP, "unicode": ""})
    menu.handle_input(ev_up)
    assert menu.index == 0

    # Navigate down through all 5 items and activate each one with RETURN
    ev_down = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN, "unicode": ""})
    ev_enter = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN, "unicode": "\r"})
    ev_left = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT, "unicode": ""})
    ev_right = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT, "unicode": ""})
    ev_esc = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "unicode": ""})

    for expected_idx in range(len(items)):
        assert menu.index == expected_idx
        menu.handle_input(ev_enter)
        if expected_idx == 2:
            menu.handle_input(ev_left)
            menu.handle_input(ev_right)
        if expected_idx < len(items) - 1:
            menu.handle_input(ev_down)

    # Boundary bump at bottom
    menu.handle_input(ev_down)
    assert menu.index == len(items) - 1

    assert selected == items
    assert adjusted == [("Einstellungen", -1), ("Einstellungen", 1)]

    # Test submenu stack push and pop via ESCAPE
    menu.push_menu(["Lautstärke", "Zurück"], title="Einstellungen")
    assert menu.current_title == "Einstellungen"
    res = menu.handle_input(ev_esc)
    assert res is None
    assert menu.current_title == "Hauptmenü"


def test_settings_highscore_and_localization_clean_utf8():
    with tempfile.TemporaryDirectory() as tmp:
        sm = SettingsManager(os.path.join(tmp, "settings.json"))
        sm.set("language", "en")
        assert sm.get("language") == "en"
        sm.set("language", "de")
        assert sm.get("language") == "de"

        hm = HighscoreManager(os.path.join(tmp, "highscores.json"))
        hm.add_score("audio_archery", "Laurin", 500)
        scores = hm.get_highscores("audio_archery")
        assert isinstance(scores, list)

    localization.set_language("de")
    de_title = localization.get_text("main_menu")
    localization.set_language("en")
    en_title = localization.get_text("main_menu")
    assert de_title and en_title

    # Verify zero UTF-8 mojibake across all DE/EN translations
    for lang, table in localization.TRANSLATIONS.items():
        for k, v in table.items():
            assert "\u00c3\u00a4" not in v and "\u00c3\u00b6" not in v and "\u00c3\u00bc" not in v, f"Mojibake in {lang}.{k}: {v}"


def test_all_75_games_every_key_and_menu_action():
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    pygame.display.set_mode((1, 1))

    games_dir = os.path.join(BASE_DIR, "games")

    audio = MagicMock()
    audio.play_looping_sound.return_value = MagicMock()
    audio.create_tone_loop.return_value = MagicMock()

    hs = MagicMock()
    hs.get_highscores.return_value = []
    settings = MagicMock()
    settings.get.side_effect = lambda k, d=None: d

    keys_to_test = [
        pygame.K_UP,
        pygame.K_DOWN,
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_SPACE,
        pygame.K_RETURN,
        pygame.K_f,
        pygame.K_j,
        pygame.K_1,
        pygame.K_2,
        pygame.K_3,
        pygame.K_h,
        pygame.K_ESCAPE,
    ]

    tested_count = 0
    for py_file in sorted(glob.glob(os.path.join(games_dir, "*.py"))):
        name = os.path.basename(py_file)[:-3]
        if name in ("base_game", "__init__"):
            continue

        mod = __import__(f"games.{name}", fromlist=["*"])
        game_class = None
        for attr in dir(mod):
            val = getattr(mod, attr)
            if isinstance(val, type) and hasattr(val, "__bases__"):
                if any(b.__name__ == "BaseGame" for b in val.__bases__):
                    game_class = val
                    break
        assert game_class is not None, f"Missing BaseGame subclass in {name}"

        game = game_class(audio, hs, settings, "TestPlayer")
        game.start()
        for k in keys_to_test:
            ev = pygame.event.Event(pygame.KEYDOWN, {"key": k, "unicode": "1"})
            game.handle_input(ev)
            game.update()
        game.finish()
        tested_count += 1

    assert tested_count >= 70
