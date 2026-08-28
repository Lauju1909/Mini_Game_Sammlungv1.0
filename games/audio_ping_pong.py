import pygame
import random
import time
from games.base_game import BaseGame

class AudioPingPong(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_ping_pong"
        self.instructions = self._("game_audio_ping_pong_instructions")
        
        self.lives = 3
        self.score = 0
        
        self.distance = 100.0
        self.side = random.choice([-1.0, 1.0])
        self.speed = 25.0
        
        self.last_tick = time.monotonic()
        self.last_beep = 0
        
        self.state = "starting"
        self.start_timer = time.monotonic() + 2.0

    def start(self):
        super().start()
        self.start_timer = time.monotonic() + 3.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.audio.speak(self._("start_go"), priority=2)
            return

        if self.state == "playing":
            self.distance -= self.speed * dt
            
            if self.distance <= 0:
                # Verfehlt!
                self.lives -= 1
                self.audio.play_sound("error")
                self.audio.speak(self._("ping_pong_miss", lives=self.lives), priority=2)
                
                if self.lives <= 0:
                    self.finish()
                else:
                    self.reset_ball()
                    self.start_timer = time.monotonic() + 1.5
                    self.state = "starting" # Kurze Pause nach Fehler
            
            # Ton spielen (Intervall wird kürzer je näher der Ball ist)
            beep_interval = max(0.08, (self.distance / 100.0) * 0.3)
            if now - self.last_beep > beep_interval:
                self.last_beep = now
                freq = int(800 - (self.distance * 4)) # 400Hz (weit) bis 800Hz (nah)
                vol = int(max(10, 100 - self.distance))
                self.audio.play_tone(frequency=freq, duration_ms=40, volume=vol, pan=self.side)

    def reset_ball(self):
        self.distance = 100.0
        self.side = random.choice([-1.0, 1.0])
        self.last_tick = time.monotonic()

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "playing":
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    pressed_side = -1.0 if event.key == pygame.K_LEFT else 1.0
                    
                    if pressed_side == self.side:
                        if self.distance <= 25.0:
                            # Perfekt getroffen
                            self.audio.play_sound("success") # Oder "confirm"
                            points = int(30 - self.distance) * 10
                            self.score += max(10, points)
                            
                            self.speed += 2.0 # Schneller werden
                            self.reset_ball()
                        else:
                            # Zu früh geschlagen (aber auf der richtigen Seite)
                            self.audio.play_sound("bump")
                            # Kleine Strafe? Oder ignorieren? Wir lassen es als "ins Leere geschlagen" gelten
                    else:
                        # Falsche Seite geschlagen
                        self.audio.play_sound("bump")

    def draw(self, screen):
        screen.fill((10, 40, 20))
        
        # Ping Pong Tisch Perspektive (vereinfacht)
        pygame.draw.polygon(screen, (0, 100, 0), [(200, 500), (600, 500), (450, 200), (350, 200)])
        pygame.draw.line(screen, (255, 255, 255), (400, 200), (400, 500), 2)
        
        # Ball zeichnen
        if self.state == "playing":
            # Berechne Größe und Position basierend auf Distanz
            size = int(max(5, 40 - (self.distance / 100.0) * 35))
            y_pos = int(500 - (self.distance / 100.0) * 300)
            x_pos = 250 if self.side == -1.0 else 550
            
            # Näher zum Zentrum bei größerer Distanz (Perspektive)
            x_pos = int(400 + (x_pos - 400) * (1.0 - (self.distance / 100.0) * 0.5))
            
            pygame.draw.circle(screen, (255, 255, 0), (x_pos, y_pos), size)

        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        speed_surf = font.render(f"Tempo: {int(self.speed)}", True, (200, 200, 200))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
        screen.blit(speed_surf, (350, 20))
