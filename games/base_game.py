import pygame
import time
import sys
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
        self.tutorial_finished = False
        game_name = self._(f"game_{self.game_id}")
        if not game_name or game_name == f"game_{self.game_id}":
            game_name = self.game_id.replace("_", " ").title()
        welcome_text = self._("tutorial_welcome", game=game_name)
        if not welcome_text or welcome_text == "tutorial_welcome":
            welcome_text = f"Willkommen zum Tutorial von {game_name}."
        self.audio.speak(welcome_text, priority=2)

    def update_tutorial(self):
        """Standard-Tutorial-Ablauf für alle Spiele ohne spezifisches Mini-Tutorial."""
        if self.tutorial_step == 1:
            if not self.audio.is_speaking():
                self.audio.speak(self.instructions, priority=1)
                self.tutorial_step = 2
        elif self.tutorial_step == 2:
            if not self.audio.is_speaking():
                prompt = self._("tutorial_press_enter")
                if not prompt or prompt == "tutorial_press_enter":
                    prompt = "Drücke Eingabe oder Leertaste zum Starten, oder Escape zum Überspringen."
                self.audio.speak(prompt, priority=1)
                self.tutorial_step = 3
        elif self.tutorial_step == 3:
            pass

    def handle_tutorial_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish_tutorial(skipped=True)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self.finish_tutorial(skipped=False)

    def finish_tutorial(self, skipped=False):
        self.is_tutorial = False
        self.tutorial_finished = True
        if skipped:
            skip_msg = self._("tutorial_skip")
            if not skip_msg or skip_msg == "tutorial_skip":
                skip_msg = "Tutorial übersprungen."
            self.audio.speak(skip_msg, priority=2)
        else:
            fin_msg = self._("tutorial_finished")
            if not fin_msg or fin_msg == "tutorial_finished":
                fin_msg = "Tutorial abgeschlossen. Das Spiel beginnt!"
            self.audio.speak(fin_msg, priority=2)
        
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
        """Unterbrechbarer Schlaf, der Fenster-Events verarbeitet und CPU schont."""
        end_time = time.monotonic() + seconds
        clock = pygame.time.Clock()
        while time.monotonic() < end_time and self.active:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.active = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.finish()
                    return

    def finish(self):
        self.active = False
        if self.score > 0:
            msg = self._("final_score", score=self.score)
            self.audio.speak(f"{self._('game_over')} {msg}", priority=2)
            self.highscores.add_score(self.game_id, self.player_name, self.score)
        else:
            self.audio.speak(self._('game_over'), priority=2)
