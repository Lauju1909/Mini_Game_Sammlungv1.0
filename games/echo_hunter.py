import pygame
import random
import math
from games.base_game import BaseGame

class EchoHunter(BaseGame):
    """
    Echo Hunter: Finde das Ziel durch Schallwellen.
    Das Ziel sendet in regelmäßigen Abständen einen Piep-Ton aus.
    Je näher man dem Ziel kommt, desto schneller und höher wird der Piep-Ton.
    """
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "echo_hunter"
        self.target_x = random.uniform(-1, 1)
        self.target_y = random.uniform(-1, 1)
        self.player_x = 0
        self.player_y = 0
        self.start_time = pygame.time.get_ticks() / 1000.0
        
        self.pulse_timer = 0
        self.pulse_rate = 1.0 # Sekunden
        
        self.max_dist = 2.0 # Diagonale von (-1,-1) bis (1,1) ist ca 2.8, aber wir nehmen 2
        self.last_pulse_time = 0

    def update(self):
        dist = math.sqrt((self.target_x - self.player_x)**2 + (self.target_y - self.player_y)**2)
        
        # Rate skaliert von 1.5s (weit weg) bis 0.1s (nah dran)
        self.pulse_rate = 0.1 + (dist / self.max_dist) * 1.4
        
        now = pygame.time.get_ticks() / 1000.0
        if now - self.last_pulse_time > self.pulse_rate:
            self.last_pulse_time = now
            # Pitch skaliert von 0.5 bis 2.0
            pitch = 2.0 - (dist / self.max_dist) * 1.5
            pitch = max(0.5, min(2.0, pitch))
            
            # Panning
            pan = self.target_x - self.player_x
            pan = max(-1.0, min(1.0, pan))
            
            # Wir nutzen play_tone für das Ziel (Frequenz skaliert von 440Hz bis 1760Hz)
            freq = 1760 - (dist / self.max_dist) * 1320
            self.audio.play_tone(freq, duration_ms=150, pan=pan)
            
            if dist < 0.1:
                self.finish_game()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            step = 0.05
            if event.key == pygame.K_LEFT:
                self.player_x = max(-1, self.player_x - step)
                self.audio.play_sound("click")
            elif event.key == pygame.K_RIGHT:
                self.player_x = min(1, self.player_x + step)
                self.audio.play_sound("click")
            elif event.key == pygame.K_UP:
                self.player_y = max(-1, self.player_y - step)
                self.audio.play_sound("click")
            elif event.key == pygame.K_DOWN:
                self.player_y = min(1, self.player_y + step)
                self.audio.play_sound("click")
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def finish_game(self):
        self.audio.play_sound("success")
        # Punkte basierend auf Zeit (desto schneller desto besser)
        elapsed = pygame.time.get_ticks() / 1000.0 - self.start_time
        self.score = max(10, int(500 - elapsed * 5))
        self.audio.speak(self._("goal_reached"))
        self.finish()

    def draw(self, screen):
        # Visuelle Darstellung für Sehende
        # Zeichne Radar-Kreise
        center = (400, 300)
        pygame.draw.circle(screen, (30, 30, 50), center, 250)
        pygame.draw.circle(screen, (50, 50, 100), center, 250, 2)
        
        # Spieler Position
        px = 400 + self.player_x * 200
        py = 300 + self.player_y * 200
        pygame.draw.circle(screen, (0, 255, 100), (int(px), int(py)), 10)
        
        # Ziel Position (nur als kleiner Schimmer, wenn nah dran)
        dist = math.sqrt((self.target_x - self.player_x)**2 + (self.target_y - self.player_y)**2)
        if dist < 0.5:
            alpha = int(255 * (1 - dist/0.5))
            tx = 400 + self.target_x * 200
            ty = 300 + self.target_y * 200
            s = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 0, alpha // 2), (20, 20), 20)
            screen.blit(s, (int(tx)-20, int(ty)-20))
