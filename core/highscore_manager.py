import json
import os

class HighscoreManager:
    def __init__(self, data_path):
        self.data_path = data_path
        self.highscores = {}
        self.load_highscores()
        self.sanitize_highscores()

    def sanitize_highscores(self):
        """Entfernt ungültige Einträge (Score <= 0 oder Test-Bots) und stellt Format sicher."""
        changed = False
        bot_prefixes = ("QA_Bot", "Bot_", "TestPlayer", "Dummy")
        for game_id, entries in list(self.highscores.items()):
            if not isinstance(entries, list):
                self.highscores[game_id] = []
                changed = True
                continue
            cleaned = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                score = entry.get("score", 0)
                name = str(entry.get("name", "Spieler")).strip()
                if score <= 0:
                    continue
                if any(name.startswith(p) for p in bot_prefixes):
                    continue
                cleaned.append({"name": name, "score": int(score)})
            cleaned.sort(key=lambda x: x["score"], reverse=True)
            cleaned = cleaned[:10]
            if cleaned != entries:
                self.highscores[game_id] = cleaned
                changed = True
        if changed:
            self.save_highscores()

    def load_highscores(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.highscores = json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der Highscores: {e}")
                self.highscores = {}

    def save_highscores(self):
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.highscores, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Highscores: {e}")

    def add_score(self, game_id, player_name, score):
        if score is None or score <= 0:
            return
        
        name = str(player_name).strip() or "Spieler"
        if game_id not in self.highscores:
            self.highscores[game_id] = []
        
        self.highscores[game_id].append({"name": name, "score": int(score)})
        # Sortiere absteigend nach Score
        self.highscores[game_id].sort(key=lambda x: x["score"], reverse=True)
        # Behalte nur Top 10
        self.highscores[game_id] = self.highscores[game_id][:10]
        self.save_highscores()

    def get_scores(self, game_id):
        return self.highscores.get(game_id, [])

    def clear_scores(self, game_id=None):
        if game_id:
            self.highscores.pop(game_id, None)
        else:
            self.highscores.clear()
        self.save_highscores()
