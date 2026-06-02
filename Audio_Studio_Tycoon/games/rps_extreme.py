import random
import pygame
from games.base_game import BaseGame

class RPS_Extreme(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "rps_extreme"
        self.instructions = self._("game_rps_extreme_instructions")

    def start(self):
        super().start()
        self.audio.speak(self._("rps_choose"))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                choices = [self._("rps_scissors"), self._("rps_stone"), self._("rps_paper")]
                idx = 0
                if event.key == pygame.K_2: idx = 1
                elif event.key == pygame.K_3: idx = 2
                
                p_choice = choices[idx]
                ai_choice = random.choice(choices)
                self.audio.speak(self._("rps_ai_has", choice=ai_choice))
                
                if p_choice == ai_choice:
                    self.audio.speak(self._("rps_draw"))
                elif (idx == 0 and ai_choice == choices[2]) or \
                     (idx == 1 and ai_choice == choices[0]) or \
                     (idx == 2 and ai_choice == choices[1]):
                    self.audio.play_sound("success")
                    self.audio.speak(self._("rps_win"))
                    self.score = 100
                else:
                    self.audio.play_sound("error")
                    self.audio.speak(self._("rps_lose"))
                self.finish()
            elif event.key == pygame.K_ESCAPE: self.finish()

    def draw(self, screen):
        font = pygame.font.SysFont("Arial", 40, bold=True)
        title = font.render("SCHERE-STEIN-PAPIER", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 80))
        
        # Symbole
        choices = ["(1) SCHERE", "(2) STEIN", "(3) PAPIER"]
        colors = [(200, 50, 50), (100, 100, 100), (50, 50, 200)]
        
        for i, choice in enumerate(choices):
            rect = pygame.Rect(100 + i * 210, 200, 180, 180)
            pygame.draw.rect(screen, colors[i], rect, border_radius=15)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=15)
            
            text = font.render(choice.split()[1], True, (255, 255, 255))
            screen.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
            
            num = font.render(choice.split()[0], True, (255, 215, 0))
            screen.blit(num, (rect.centerx - num.get_width()//2, rect.y + 10))
