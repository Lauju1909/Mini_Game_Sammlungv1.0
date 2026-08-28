import random
import pygame
import time
from games.base_game import BaseGame

class ReactionBlitz(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "reaction_blitz"
        self.instructions = self._("game_reaction_blitz_instructions")
        self.rounds = 5
        self.current_round = 0
        self.state = "waiting" # waiting, prompt, result
        self.timer = 0
        self.wait_time = 0
        self.start_time = 0
        self.reaction_times = []

    def start(self):
        super().start()
        self.next_round()

    def next_round(self):
        if self.current_round >= self.rounds:
            self.finish()
            return
        
        self.current_round += 1
        self.state = "waiting"
        self.wait_time = random.uniform(2.0, 5.0)
        self.timer = time.monotonic()
        self.audio.speak(self._("round_number", idx=self.current_round), interrupt=False)

    def update(self):
        if not self.active: return
        
        if self.state == "waiting":
            if time.monotonic() - self.timer > self.wait_time:
                self.state = "prompt"
                self.start_time = time.monotonic()
                self.audio.play_sound("confirm") # Blitz-Sound
        
        elif self.state == "prompt":
            if time.monotonic() - self.start_time > 2.0: # Zu langsam (2 Sek)
                self.state = "result"
                self.audio.play_sound("error")
                self.audio.speak(self._("too_slow"))
                self.timer = time.monotonic()

        elif self.state == "result":
            if time.monotonic() - self.timer > 1.5:
                self.next_round()

    def handle_input(self, event):
        if not self.active: return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return

            if self.state == "waiting":
                # Zu früh gedrückt
                self.state = "result"
                self.audio.play_sound("error")
                self.audio.speak(self._("too_early"))
                self.score = max(0, self.score - 50)
                self.timer = time.monotonic()
            
            elif self.state == "prompt":
                # Getroffen!
                reaction = (time.monotonic() - self.start_time) * 1000 # in ms
                points = max(10, int(1000 - reaction))
                self.score += points
                self.reaction_times.append(reaction)
                
                self.state = "result"
                self.audio.play_sound("success")
                self.audio.speak(self._("reaction_result", ms=int(reaction)))
                self.timer = time.monotonic()

    def draw(self, screen):
        # Visuelles Feedback
        center = (400, 300)
        if self.state == "waiting":
            color = (100, 100, 100)
            text = self._("wait_for_it")
        elif self.state == "prompt":
            # Blitz-Effekt
            color = (255, 255, 0)
            text = "JETZT!"
            # Zeichne einen Blitz
            pygame.draw.polygon(screen, (255, 255, 255), [(400, 100), (450, 250), (350, 250), (400, 400)])
        elif self.state == "result":
            color = (50, 200, 50)
            text = self._("good")
        else:
            color = (0, 0, 0)
            text = ""

        pygame.draw.circle(screen, color, center, 100)
        font = pygame.font.SysFont("Arial", 48, bold=True)
        surf = font.render(text, True, (255, 255, 255))
        screen.blit(surf, (center[0] - surf.get_width()//2, center[1] - surf.get_height()//2))

        # Runde und Score
        score_font = pygame.font.SysFont("Arial", 32)
        score_surf = score_font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        round_surf = score_font.render(f"Runde: {self.current_round}/{self.rounds}", True, (200, 200, 200))
        screen.blit(score_surf, (40, 40))
        screen.blit(round_surf, (40, 80))
