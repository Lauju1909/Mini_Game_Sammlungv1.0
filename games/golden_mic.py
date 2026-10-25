import pygame
import random
import math
import time
from games.base_game import BaseGame

class GoldenMic(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "golden_mic"
        self.instructions = self._("game_golden_mic_instructions")
        self.target_x = random.randint(0, 10)
        self.target_y = random.randint(0, 10)
        self.player_x = 5
        self.player_y = 5

    def start(self):
        super().start()
        self.target_x = random.randint(0, 10)
        self.target_y = random.randint(0, 10)
        self.player_x = 5
        self.player_y = 5
        self.score = 0
        self.last_beep = 0
    def update(self):
        now = time.monotonic()
        dist = math.sqrt((self.target_x - self.player_x)**2 + (self.target_y - self.player_y)**2)
        
        # Beep-Intervall basierend auf Distanz (0.1 bis 1.0 Sekunden)
        interval = max(0.1, min(1.0, dist / 5.0))
        
        if not hasattr(self, "last_beep"): self.last_beep = 0
        if now - self.last_beep > interval:
            # Panning basierend auf X-Position (-1 bis 1)
            pan = (self.target_x - self.player_x) / 10.0
            pan = max(-1.0, min(1.0, pan))
            self.audio.play_panned_sound("tick_001", pan)
            self.last_beep = now

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.player_y > 0: self.player_y -= 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_DOWN:
                if self.player_y < 10: self.player_y += 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if self.player_x > 0: self.player_x -= 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_RIGHT:
                if self.player_x < 10: self.player_x += 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_ESCAPE: self.finish()
            
            # Check ob Ziel erreicht
            if self.player_x == self.target_x and self.player_y == self.target_y:
                self.score = 500
                self.audio.play_sound("success")
                self.audio.speak(self._("mic_found"))
                self.finish()

    def draw(self, screen):
        # 11x11 Audio-Raster
        pygame.draw.rect(screen, (25, 25, 20), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (255, 215, 0), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render("DAS GOLDENE MIKROFON", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 190))
        
        # Grid zeichnen
        cell_size = 20
        grid_start_x = 400 - (11 * cell_size) // 2
        grid_start_y = 230
        
        for y in range(11):
            for x in range(11):
                gx = grid_start_x + x * cell_size
                gy = grid_start_y + y * cell_size
                pygame.draw.rect(screen, (40, 40, 35), (gx, gy, cell_size - 2, cell_size - 2))
                
        # Spieler
        px = grid_start_x + self.player_x * cell_size + cell_size // 2
        py = grid_start_y + self.player_y * cell_size + cell_size // 2
        pygame.draw.circle(screen, (100, 200, 255), (px, py), 8)
        
        # Goldenes Mikrofon (wenn gefunden oder leuchtend)
        if self.score > 0:
            tx = grid_start_x + self.target_x * cell_size + cell_size // 2
            ty = grid_start_y + self.target_y * cell_size + cell_size // 2
            pygame.draw.circle(screen, (255, 215, 0), (tx, ty), 9)
            
        hint = small_font.render("Pfeiltasten zum Bewegen  |  Folge dem immer schneller werdenden Ticken!", True, (220, 210, 170))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

