import random
import pygame
import time
import math
from games.base_game import BaseGame

class BombDefuser(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "bomb_defuser"
        self.instructions = self._("game_bomb_defuser_instructions")
        self.speed = 1.0
        self.max_speed = 5.0
        self.last_tick = time.time()

    def update(self):
        now = time.time()
        if now - self.last_tick > (1.0 / self.speed):
            self.audio.play_sound("click")
            self.last_tick = now
            self.speed += 0.12 # Etwas schnellerer Anstieg
            if self.speed >= self.max_speed:
                self.audio.play_sound("error")
                self.audio.speak(self._("bomb_exploded"))
                self.score = 0
                self.finish()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                # Je näher an 5.0, desto besser. Aber ab 5.0 explodiert sie.
                if self.speed > 4.2:
                    # Punkteberechnung: Basis 500 + Bonus für Präzision
                    precision = (self.speed - 4.2) / (5.0 - 4.2) # 0.0 bis 1.0
                    self.score = int(500 + (precision * 1500))
                    
                    self.audio.play_sound("success")
                    if precision > 0.9:
                        self.audio.speak(self._("hit_perfect"))
                    else:
                        self.audio.speak(self._("bomb_defused_simple"))
                    
                    self.audio.speak(self._("final_score", score=self.score))
                    self.finish()
                else:
                    self.audio.speak(self._("bomb_too_early"))
                    self.score = 0
                    self.finish()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def draw(self, screen):
        # Fortschrittsbalken (Gefahr)
        progress = (self.speed - 1.0) / (self.max_speed - 1.0)

        # Zeichne Bombe
        center = (400, 300)
        # Bombenkörper
        pygame.draw.circle(screen, (30, 30, 30), center, 100)
        pygame.draw.circle(screen, (50, 50, 50), (370, 270), 20) # Glanzpunkt
        
        # Lunte (verkürzt sich)
        fuse_len = 1.0 - progress
        if fuse_len > 0:
            pygame.draw.arc(screen, (139, 69, 19), (380, 150, 140, 140), 0, (3.14/2) * fuse_len, 5)
        
        # Funke an der aktuellen Luntenspitze
        spark_angle = (3.14/2) * fuse_len
        spark_x = 380 + 70 + math.cos(spark_angle) * 70
        spark_y = 150 + 70 - math.sin(spark_angle) * 70
        
        if int(time.time() * 10) % 2 == 0:
            pygame.draw.circle(screen, (255, 200, 0), (int(spark_x), int(spark_y)), 15)
            pygame.draw.circle(screen, (255, 50, 0), (int(spark_x), int(spark_y)), 8)
        width = int(progress * 600)
        bar_color = (int(progress * 255), int((1-progress) * 255), 0)
        
        pygame.draw.rect(screen, (50, 50, 50), (100, 450, 600, 30), border_radius=15)
        pygame.draw.rect(screen, bar_color, (100, 450, width, 30), border_radius=15)
        
        # Text
        font = pygame.font.SysFont("Arial", 40, bold=True)
        label = font.render("GEFAHR!", True, bar_color)
        screen.blit(label, (400 - label.get_width()//2, 500))
        
        # Zielzone markieren
        target_start = int(((4.2 - 1.0) / (self.max_speed - 1.0)) * 600)
        pygame.draw.line(screen, (255, 255, 255), (100 + target_start, 445), (100 + target_start, 485), 3)
