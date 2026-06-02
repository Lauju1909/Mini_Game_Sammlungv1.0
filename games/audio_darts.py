import pygame
import random
import time
from games.base_game import BaseGame

class AudioDarts(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_darts"
        self.instructions = self._("game_audio_darts_instructions")
        
        self.score = 0
        self.lives = 3
        self.level = 1
        
        self.cursor = -1.0
        self.prev_cursor = -1.0
        self.direction = 1
        self.speed = 1.5
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        self.last_tick = time.time()
        self.tick_timer = 0

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.start_timer = time.time() + 2.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.cursor = random.choice([-1.0, 1.0])
                self.direction = -1 if self.cursor > 0 else 1
            return

        if self.state == "playing":
            self.prev_cursor = self.cursor
            self.cursor += self.speed * self.direction * dt
            
            # Wenden an den Rändern
            if self.cursor >= 1.0:
                self.cursor = 1.0
                self.direction = -1
            elif self.cursor <= -1.0:
                self.cursor = -1.0
                self.direction = 1
                
            # Zentrum überschritten? (Ping)
            if (self.prev_cursor < 0 and self.cursor >= 0) or (self.prev_cursor > 0 and self.cursor <= 0):
                self.audio.play_tone(frequency=1000, duration_ms=60, volume=100, pan=0.0)
            else:
                # Normales Ticken (schneller je näher am Zentrum)
                if now > self.tick_timer:
                    dist = abs(self.cursor)
                    delay = 0.05 + (dist * 0.15)
                    self.tick_timer = now + delay
                    
                    freq = 400 + (1.0 - dist) * 200
                    self.audio.play_tone(frequency=int(freq), duration_ms=20, volume=50, pan=self.cursor)

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
                if event.key == pygame.K_SPACE:
                    dist = abs(self.cursor)
                    
                    if dist < 0.08:
                        # Bullseye
                        self.audio.play_sound("success")
                        self.score += 50
                        self.audio.speak("Bullseye!", priority=1)
                        self.speed += 0.2
                    elif dist < 0.25:
                        # Inner Ring
                        self.audio.play_sound("confirm")
                        self.score += 25
                        self.audio.speak("25", priority=1)
                        self.speed += 0.1
                    elif dist < 0.5:
                        # Outer Ring
                        self.audio.play_tone(frequency=300, duration_ms=100)
                        self.score += 10
                        self.audio.speak("10", priority=1)
                        self.speed += 0.05
                    else:
                        # Daneben
                        self.audio.play_sound("error")
                        self.audio.speak(self._("darts_miss"), priority=1)
                        self.lives -= 1
                        
                    if self.lives <= 0:
                        self.sleep(1)
                        self.audio.speak(self._("darts_gameover"), priority=2)
                        self.sleep(1.5)
                        self.finish()
                    else:
                        # Reset cursor für den nächsten Wurf
                        self.state = "starting"
                        self.start_timer = time.time() + 1.0

    def draw(self, screen):
        screen.fill((20, 40, 20))
        
        font = pygame.font.SysFont("Arial", 28)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        speed_surf = font.render(f"Geschwindigkeit: {self.speed:.1f}", True, (200, 200, 255))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
        screen.blit(speed_surf, (20, 60))
        
        # Dartscheibe (1D Linie)
        center_y = 300
        pygame.draw.line(screen, (100, 100, 100), (100, center_y), (700, center_y), 5)
        
        # Zonen
        # Bullseye
        pygame.draw.rect(screen, (255, 0, 0), (400 - 24, center_y - 20, 48, 40))
        # Inner
        pygame.draw.rect(screen, (0, 255, 0), (400 - 75, center_y - 15, 150, 30), 2)
        # Outer
        pygame.draw.rect(screen, (255, 255, 0), (400 - 150, center_y - 10, 300, 20), 2)
        
        # Cursor
        if self.state == "playing":
            cursor_x = 400 + int(self.cursor * 300)
            pygame.draw.circle(screen, (255, 255, 255), (cursor_x, center_y), 10)
