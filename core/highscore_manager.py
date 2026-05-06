import json
import os

class HighscoreManager:
    def __init__(self, data_path):
        self.data_path = data_path
        self.highscores = {}
        self.load_highscores()

    def load_highscores(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.highscores = json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der Highscores: {e}")

    def save_highscores(self):
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.highscores, f, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern der Highscores: {e}")

    def add_score(self, game_id, player_name, score):
        if game_id not in self.highscores:
            self.highscores[game_id] = []
        
        self.highscores[game_id].append({"name": player_name, "score": score})
        # Sortiere absteigend nach Score
        self.highscores[game_id].sort(key=lambda x: x["score"], reverse=True)
        # Behalte nur Top 10
        self.highscores[game_id] = self.highscores[game_id][:10]
        self.save_highscores()

    def get_scores(self, game_id):
        return self.highscores.get(game_id, [])
