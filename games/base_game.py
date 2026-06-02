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
        self.is_tutorial = False
        self.tutorial_step = 0
        self.tutorial_finished = False

    def _(self, key, **kwargs):
        return get_text(key, **kwargs)

    def start(self):
        self.audio.speak(self.instructions, interrupt=False, priority=2)

    def start_tutorial(self):
        self.is_tutorial = True
        self.tutorial_step = 1
        self.audio.speak(self._("tutorial_welcome", game=self._(f"game_{self.game_id}")), priority=2)

    def update_tutorial(self):
        pass

    def handle_tutorial_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.finish_tutorial(skipped=True)

    def finish_tutorial(self, skipped=False):
        self.is_tutorial = False
        self.tutorial_finished = True
        if skipped:
            self.audio.speak(self._("tutorial_skip"), priority=2)
        else:
            self.audio.speak(self._("tutorial_finished"), priority=2)
        
        # In Settings speichern, dass das Tutorial erledigt ist
        completed = self.settings.get("completed_tutorials", [])
        if self.game_id not in completed:
            completed.append(self.game_id)
            self.settings.set("completed_tutorials", completed)

    def handle_input(self, event):
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()

    def update(self):
        if self.is_tutorial:
            self.update_tutorial()
            return

    def draw(self, screen):
        pass

    def sleep(self, seconds):
        import time
        end_time = time.time() + seconds
        while time.time() < end_time:
            pygame.time.Clock().tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

    def finish(self):
        self.active = False
        msg = self._("final_score", score=self.score)
        self.audio.speak(f"{self._('game_over')} {msg}", priority=2)
        self.highscores.add_score(self.game_id, self.player_name, self.score)
