import random
import pygame
import time
from games.base_game import BaseGame

class Echolot(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "echolot"
        self.instructions = self._("game_echolot_instructions")
        self.target_dist = random.uniform(20, 100)
        self.current_dist = self.target_dist

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Simuliere Ping-Verzögerung
                delay = self.current_dist / 50.0
                time.sleep(delay)
                self.audio.play_sound("click")
            elif event.key == pygame.K_SPACE:
                diff = abs(self.current_dist - 5.0)
                self.score = int(max(0, 1000 - diff * 50))
                self.audio.speak(self._("distance_feedback", dist=round(self.current_dist, 1)))
                self.finish()
            elif event.key == pygame.K_ESCAPE:
                self.finish()
            
            # Schiff bewegt sich langsam vorwärts
            self.current_dist -= 2.0
            if self.current_dist <= 0:
                self.audio.play_sound("error")
                self.audio.speak(self._("crash"))
                self.finish()
                
