import pygame
import random
import time
from games.base_game import BaseGame

class DialMaster(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "dial_master"
        self.instructions = self._("game_dial_master_instructions")
        
        self.max_number = 40
        self.combination = [random.randint(0, self.max_number) for _ in range(3)]
        self.current_stage = 0
        self.current_number = 0
        
        self.lives = 3
        self.score = 1000
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        self.game_start_time = 0

    def start(self):
        super().start()
        self.start_timer = time.time() + 3.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.game_start_time = now
                self.audio.speak(self._("start_go"), priority=2)
            return

        if self.state == "playing":
            # Zeitstrafe kontinuierlich
            elapsed = now - self.game_start_time
            self.score = max(0, 1000 - int(elapsed * 10))

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
                if event.key == pygame.K_LEFT:
                    self.current_number -= 1
                    if self.current_number < 0:
                        self.current_number = self.max_number
                        self.audio.play_sound("bump") # Anschlag/Übergang
                    self.play_dial_sound()
                    
                elif event.key == pygame.K_RIGHT:
                    self.current_number += 1
                    if self.current_number > self.max_number:
                        self.current_number = 0
                        self.audio.play_sound("bump")
                    self.play_dial_sound()
                    
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.check_combination()

    def play_dial_sound(self):
        target = self.combination[self.current_stage]
        # Standard Tonhöhe ist 400Hz. Wenn es die richtige Zahl ist, ist es 480Hz (subtil höher)
        freq = 480 if self.current_number == target else 400
        
        # Leiseres Klicken für das Rad
        self.audio.play_tone(frequency=freq, duration_ms=40, volume=60)

    def check_combination(self):
        target = self.combination[self.current_stage]
        if self.current_number == target:
            # Richtig!
            self.audio.play_sound("success")
            self.current_stage += 1
            self.audio.speak(self._("dial_locked", stage=self.current_stage), priority=1)
            
            if self.current_stage >= len(self.combination):
                # Alle gefunden!
                self.audio.play_sound("win")
                self.audio.speak(self._("safe_open"))
                self.sleep(0.5)
                self.finish()
        else:
            # Falsch!
            self.lives -= 1
            self.score = max(0, self.score - 100)
            self.audio.play_sound("error")
            self.audio.speak(self._("dial_error", lives=self.lives), priority=1)
            
            if self.lives <= 0:
                self.finish()

    def draw(self, screen):
        screen.fill((20, 20, 20))
        
        # Rad Zeichnen
        center = (400, 300)
        pygame.draw.circle(screen, (50, 50, 50), center, 150)
        pygame.draw.circle(screen, (100, 100, 100), center, 150, 5)
        
        import math
        angle = (self.current_number / self.max_number) * 360
        rad = math.radians(angle - 90)
        ex = center[0] + math.cos(rad) * 130
        ey = center[1] + math.sin(rad) * 130
        pygame.draw.line(screen, (255, 0, 0), center, (ex, ey), 8)
        
        font = pygame.font.SysFont("Arial", 48, bold=True)
        val_surf = font.render(str(self.current_number), True, (255, 255, 255))
        screen.blit(val_surf, (400 - val_surf.get_width()//2, 275))
        
        # Lichter für Stufen
        for i in range(len(self.combination)):
            color = (0, 255, 0) if i < self.current_stage else (50, 0, 0)
            pygame.draw.circle(screen, color, (350 + i * 50, 500), 15)
            
        font_small = pygame.font.SysFont("Arial", 24)
        lives_surf = font_small.render(f"Leben: {self.lives}", True, (255, 100, 100))
        score_surf = font_small.render(f"Punkte: {self.score}", True, (255, 255, 255))
        screen.blit(lives_surf, (20, 20))
        screen.blit(score_surf, (650, 20))
