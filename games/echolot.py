import random
import pygame
from games.base_game import BaseGame

class Echolot(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "echolot"
        self.instructions = self._("game_echolot_instructions")
        self.target_dist = random.uniform(20, 100)
        self.current_dist = self.target_dist
        self.last_ping_time = 0
        self.ping_active = False
        self.ping_delay = 0

    def update(self):
        super().update()
        if not self.active or self.is_tutorial:
            return
            
        # Schiff bewegt sich langsam vorwärts
        self.current_dist -= 0.05 # Move per frame, e.g. 60 FPS = 3 units / sec
        
        if self.ping_active:
            now = pygame.time.get_ticks() / 1000.0
            if now - self.last_ping_time >= self.ping_delay:
                self.audio.play_sound("click")
                self.ping_active = False

        if self.current_dist <= 0:
            self.audio.play_sound("error")
            self.audio.speak(self._("crash"))
            self.finish()

    def handle_input(self, event):
        super().handle_input(event)
        if not self.active or self.is_tutorial:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not self.ping_active:
                    self.ping_active = True
                    self.last_ping_time = pygame.time.get_ticks() / 1000.0
                    self.ping_delay = max(0.0, self.current_dist / 50.0)
            elif event.key == pygame.K_SPACE:
                diff = abs(self.current_dist - 5.0)
                self.score = int(max(0, 1000 - diff * 50))
                self.audio.speak(self._("distance_feedback", dist=round(self.current_dist, 1)))
                self.finish()
