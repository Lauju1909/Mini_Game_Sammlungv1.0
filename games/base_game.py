import pygame
from localization import get_text

class BaseGame:
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        self.audio = audio_manager
        self.highscores = highscore_manager
        self.settings = settings_manager
        self.player_name = player_name
        self.active = True
        self.score = 0
        self.game_id = "base"
        self.instructions = self._("instructions_base")

    def _(self, key, **kwargs):
        return get_text(key, **kwargs)

    def start(self):
        self.audio.speak(self.instructions, interrupt=False, priority=2)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()

    def update(self):
        pass

    def draw(self, screen):
        pass

    def finish(self):
        self.active = False
        msg = self._("final_score", score=self.score)
        self.audio.speak(f"{self._('game_over')} {msg}", priority=2)
        self.highscores.add_score(self.game_id, self.player_name, self.score)
