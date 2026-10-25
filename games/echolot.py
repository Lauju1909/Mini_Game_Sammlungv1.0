import math
import time
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
            now = time.monotonic()
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
                    self.last_ping_time = time.monotonic()
                    self.ping_delay = max(0.0, self.current_dist / 50.0)
            elif event.key == pygame.K_SPACE:
                diff = abs(self.current_dist - 5.0)
                self.score = int(max(0, 1000 - diff * 50))
                self.audio.speak(self._("distance_feedback", dist=round(self.current_dist, 1)))
                self.finish()

    def draw(self, screen):
        # Echolot Sonar-Radar
        pygame.draw.rect(screen, (5, 20, 25), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (0, 220, 180), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render("ECHOLOT-SONAR", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        radar_center = (400, 320)
        for r in [30, 60, 90]:
            pygame.draw.circle(screen, (0, 80, 60), radar_center, r, width=1)
        pygame.draw.circle(screen, (0, 220, 180), radar_center, 90, width=2)
        
        # Radar-Zeiger (Rotation)
        angle = time.monotonic() * 2.5
        rx = radar_center[0] + int(math.cos(angle) * 88)
        ry = radar_center[1] + int(math.sin(angle) * 88)
        pygame.draw.line(screen, (0, 255, 180), radar_center, (rx, ry), 2)
        
        # Distanzanzeige
        dist_color = (255, 60, 60) if self.current_dist < 15.0 else (0, 255, 180)
        dist_txt = font.render(f"Distanz: {self.current_dist:.1f} m", True, dist_color)
        screen.blit(dist_txt, (400 - dist_txt.get_width() // 2, 425))
        
        hint = small_font.render("EINGABE = Sonar-Ping aussenden  |  LEERTASTE = Stoppen bei 5 Metern!", True, (150, 210, 200))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

