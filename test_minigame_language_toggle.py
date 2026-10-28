"""Automated verification test for Mini_Game_Sammlung language toggle and hotkeys (F8, Ctrl+L)."""
import os
import sys

# Headless pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from settings_manager import SettingsManager
import localization
from localization import get_text as _
from main import MiniGameCollection

def run_tests():
    print("=== Testing Mini_Game_Sammlung Language Toggle ===")
    app = MiniGameCollection()
    
    # Ensure starting in German
    app.settings.set("language", "de")
    localization.set_language("de")
    app.setup_main_menu()
    
    # Check initial main menu labels
    labels_de = [it["label"] for it in app.menu.items]
    print("Initial DE Main Menu:", labels_de)
    assert "Spielen" in labels_de, f"Expected German 'Spielen', got {labels_de}"
    
    # 1. Test direct toggle_language()
    print("\n--- Test 1: toggle_language() call ---")
    app.toggle_language()
    assert app.settings.get("language") == "en", "Language should now be 'en'"
    assert localization.get_language() == "en", "Localization get_language() should be 'en'"
    labels_en = [it["label"] for it in app.menu.items]
    print("Toggled EN Main Menu:", labels_en)
    assert "Play" in labels_en, f"Expected 'Play' in EN menu, got {labels_en}"
    
    # 2. Test toggling back to DE
    print("\n--- Test 2: toggle_language() back to DE ---")
    app.toggle_language()
    assert app.settings.get("language") == "de", "Language should now be 'de'"
    assert localization.get_language() == "de", "Localization get_language() should be 'de'"
    labels_de2 = [it["label"] for it in app.menu.items]
    print("Toggled back DE Main Menu:", labels_de2)
    assert "Spielen" in labels_de2, f"Expected 'Spielen' in DE menu, got {labels_de2}"
    
    # 3. Test F8 Hotkey in handle_input
    print("\n--- Test 3: F8 Hotkey Event ---")
    f8_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F8, mod=0)
    app.handle_input(f8_event)
    assert app.settings.get("language") == "en", "F8 should toggle to 'en'"
    labels_en2 = [it["label"] for it in app.menu.items]
    assert "Play" in labels_en2, f"Expected 'Play' after F8, got {labels_en2}"
    print("F8 successfully toggled to English.")
    
    # 4. Test Ctrl + L Hotkey Event
    print("\n--- Test 4: Ctrl + L Hotkey Event ---")
    ctrl_l_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_l, mod=pygame.KMOD_CTRL)
    app.handle_input(ctrl_l_event)
    assert app.settings.get("language") == "de", "Ctrl+L should toggle back to 'de'"
    labels_de3 = [it["label"] for it in app.menu.items]
    assert "Spielen" in labels_de3, f"Expected 'Spielen' after Ctrl+L, got {labels_de3}"
    print("Ctrl+L successfully toggled to German.")
    
    # 5. Test inside settings menu
    print("\n--- Test 5: In Settings Menu ---")
    app.setup_settings_menu()
    settings_labels = [it["label"] for it in app.menu.items]
    print("DE Settings Labels:", settings_labels)
    assert any("Sprache" in l for l in settings_labels), "Expected Sprache setting in German"
    
    # Toggle with F8 while in settings menu
    app.handle_input(f8_event)
    settings_labels_en = [it["label"] for it in app.menu.items]
    print("EN Settings Labels after F8:", settings_labels_en)
    assert any("Language" in l for l in settings_labels_en), "Expected Language setting in English"
    
    # 6. Test categories toggle
    print("\n--- Test 6: In Categories Menu ---")
    app.menu.menu_stack = []
    app.setup_categories()
    cat_labels_en = [it["label"] for it in app.menu.items]
    print("EN Categories:", cat_labels_en[:3])
    
    # Toggle with Ctrl+L
    app.handle_input(ctrl_l_event)
    cat_labels_de = [it["label"] for it in app.menu.items]
    print("DE Categories after Ctrl+L:", cat_labels_de[:3])
    assert cat_labels_de != cat_labels_en, "Categories should update when language toggles"
    
    print("\nALL 6 TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    run_tests()
