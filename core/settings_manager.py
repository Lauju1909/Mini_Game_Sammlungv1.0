import json
import os

class SettingsManager:
    def __init__(self, settings_path):
        self.settings_path = settings_path
        self.settings = {
            "volume_sfx": 100,
            "volume_music": 50,
            "speech_volume": 100,
            "speech_rate": 50,
            "language": "de",
            "player_name": "Spieler",
            "tts_engine": "auto"
        }
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"Fehler beim Laden der Einstellungen: {e}")

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
