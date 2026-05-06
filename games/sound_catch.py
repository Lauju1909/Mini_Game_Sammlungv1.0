import random
import pygame
import math
from games.base_game import BaseGame

class SoundCatch(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "sound_catch"
        self.instructions = self._("game_sound_catch_instructions")
        
        self.pan = -1.0
        self.direction = 1
        self.speed = 0.02
        self.attempts = 0
        self.max_attempts = 5
        self.total_score = 0
        self.last_tick = pygame.time.get_ticks()

    def start(self):
        super().start()
        self.audio.speak(self._("instructions"), interrupt=False)

    def update(self):
        if not self.active: return
        
        now = pygame.time.get_ticks()
        if now - self.last_tick > 30:
            self.pan += self.direction * self.speed
            if self.pan >= 1.0 or self.pan <= -1.0:
                self.direction *= -1
                self.audio.play_sound("click") # Rand-Feedback
            
            # Alle 100ms ein Tick-Geräusch an der aktuellen Position
            if now % 100 < 30:
                self.audio.play_panned_sound("blip", self.pan)
            
            self.last_tick = now

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                self._catch()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _catch(self):
        self.attempts += 1
        diff = abs(self.pan)
        points = 0
        if diff < 0.05:
            points = 250
            self.audio.play_sound("success")
            self.audio.speak(self._("hit_perfect"))
        elif diff < 0.15:
            points = 150
            self.audio.play_sound("confirm")
            self.audio.speak(self._("hit_good"))
        elif diff < 0.3:
            points = 50
            self.audio.play_sound("select")
            self.audio.speak(self._("hit_ok"))
        else:
            self.audio.play_sound("error")
            self.audio.speak(self._("miss"))
        
        self.total_score += points
        
        if self.attempts >= self.max_attempts:
            self.score = self.total_score
            self.audio.speak(self._("final_score", score=self.score))
            self.finish()
        else:
            # Geschwindigkeit erhöhen
            self.speed += 0.01
            self.pan = -1.0 if random.random() > 0.5 else 1.0
            self.direction = 1 if self.pan < 0 else -1
            
    def draw(self, screen):
        # Radar-Hintergrund
        center = (400, 300)
        pygame.draw.circle(screen, (20, 40, 20), center, 200)
        pygame.draw.circle(screen, (0, 255, 0), center, 200, 2)
        pygame.draw.circle(screen, (0, 100, 0), center, 100, 1)
        
        # Radar-Linien
        pygame.draw.line(screen, (0, 100, 0), (200, 300), (600, 300))
        pygame.draw.line(screen, (0, 100, 0), (400, 100), (400, 500))
        
        # Scanner-Strahl (Visualisierung des Pans)
        angle = (self.pan * 90) # -90 bis 90 Grad
        rad = math.radians(angle - 90)
        end_x = 400 + math.cos(rad) * 190
        end_y = 300 + math.sin(rad) * 190
        pygame.draw.line(screen, (100, 255, 100), center, (end_x, end_y), 3)
        
        # Ziel-Signal (blinkend in der Mitte)
        if int(pygame.time.get_ticks() / 200) % 2 == 0:
            pygame.draw.circle(screen, (255, 50, 50), center, 15)
            pygame.draw.circle(screen, (255, 255, 255), center, 15, 2)
            
        # UI Info
        font = pygame.font.SysFont("Arial", 36, bold=True)
        title = font.render("SOUND-CATCH", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        font_small = pygame.font.SysFont("Arial", 24)
        info = f"Versuch: {self.attempts} / {self.max_attempts} | Punkte: {self.total_score}"
        info_surf = font_small.render(info, True, (0, 255, 0))
        screen.blit(info_surf, (400 - info_surf.get_width()//2, 520))
