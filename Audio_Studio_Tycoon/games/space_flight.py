import random
import pygame
import time
from games.base_game import BaseGame

class SpaceFlight(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "space_flight"
        self.instructions = self._("game_space_flight_instructions")
        self.next_asteroid = time.time() + 2
        self.asteroids_passed = 0

    def update(self):
        if time.time() > self.next_asteroid:
            self.side = random.choice(["links", "rechts"])
            pan = -1.0 if self.side == "links" else 1.0
            self.audio.play_panned_sound("warn", pan)
            # Nutze lokalisierte Richtungsansage
            self.audio.speak(self._("key_left" if self.side == "links" else "key_right"))
            self.hit_deadline = time.time() + 1.5
            self.next_asteroid = time.time() + 3
            self.waiting_for_dodge = True

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if not hasattr(self, 'waiting_for_dodge') or not self.waiting_for_dodge:
                return # Ignoriere Eingaben wenn kein Asteroid da ist
            
            if event.key == pygame.K_LEFT:
                if hasattr(self, 'side') and self.side == "rechts":
                    self._success()
                else: self._fail()
            elif event.key == pygame.K_RIGHT:
                if hasattr(self, 'side') and self.side == "links":
                    self._success()
                else: self._fail()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _success(self):
        self.waiting_for_dodge = False
        self.audio.play_sound("confirm")
        self.score += 50
        self.asteroids_passed += 1
        if self.asteroids_passed >= 5: self.finish()

    def _fail(self):
        self.audio.play_sound("error")
        self.audio.speak(self._("hit_obstacle"))
        self.finish()
