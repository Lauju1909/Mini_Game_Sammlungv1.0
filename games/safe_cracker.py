import random
import pygame
import time
from games.base_game import BaseGame

class SafeCracker(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "safe_cracker"
        self.instructions = self._("game_safe_cracker_instructions")
        self.target_combination = [random.randint(0, 20) for _ in range(3)]
        self.current_index = 0
        self.current_value = 0
        self.start_time = 0

    def start(self):
        super().start()
        self.start_time = time.monotonic()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if self.current_value < 20:
                    self.current_value += 1
                    self._check_click()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if self.current_value > 0:
                    self.current_value -= 1
                    self._check_click()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _check_click(self):
        if self.current_value == self.target_combination[self.current_index]:
            self.audio.play_sound("metalLatch")
            self.audio.speak(self._("number_locked", idx=self.current_index + 1))
            self.current_index += 1
            if self.current_index >= 3:
                duration = time.monotonic() - self.start_time
                self.score = max(100, int(1000 - duration * 5))
                self.audio.play_sound("handleCoins")
                self.audio.speak(self._("safe_open"))
                self.audio.speak(self._("final_score", score=self.score))
                self.finish()
        else:
            self.audio.play_sound("metalClick")

    def draw(self, screen):
        font_large = pygame.font.SysFont("Arial", 48, bold=True)
        font_medium = pygame.font.SysFont("Arial", 32)
        
        # Tresor-Scheibe (Dial)
        center = (400, 300)
        radius = 120
        pygame.draw.circle(screen, (80, 80, 80), center, radius)
        pygame.draw.circle(screen, (150, 150, 150), center, radius, width=10)
        
        # Zeiger (Marker)
        pygame.draw.polygon(screen, (255, 0, 0), [(400, 170), (390, 150), (410, 150)])
        
        # Aktueller Wert auf der Scheibe (Rotation simulieren)
        angle = (self.current_value / 20) * 360
        import math
        indicator_angle = math.radians(angle - 90)
        end_x = 400 + math.cos(indicator_angle) * 100
        end_y = 300 + math.sin(indicator_angle) * 100
        pygame.draw.line(screen, (255, 255, 255), center, (end_x, end_y), 5)
        
        # Aktueller Wert Text
        val_surf = font_large.render(str(self.current_value), True, (255, 215, 0))
        screen.blit(val_surf, (400 - val_surf.get_width()//2, 275))
        
        # Kombination Fortschritt (3 Lichter)
        for i in range(3):
            color = (0, 255, 0) if i < self.current_index else (50, 50, 50)
            pygame.draw.circle(screen, color, (350 + i * 50, 450), 15)
            pygame.draw.circle(screen, (200, 200, 200), (350 + i * 50, 450), 15, width=2)
        
        hint_surf = font_medium.render("Finde die Kombination!", True, (200, 200, 200))
        screen.blit(hint_surf, (400 - hint_surf.get_width()//2, 100))
