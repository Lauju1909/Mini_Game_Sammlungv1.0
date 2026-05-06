import pygame
import random
import math
from .base_game import BaseGame

class AudioArchery(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "audio_archery"
        self.points = 0
        self.round = 1
        self.max_rounds = 5
        self.pan = -1.0
        self.speed = 0.02
        self.direction = 1
        self.state = "aiming" # aiming, result, finished
        self.last_result_time = 0
        self.result_text = ""
        self.arrow_pos = -1.0
        
    def start(self):
        super().start()
        self.audio.speak(self._("game_audio_archery_instructions"))
        self.next_arrow()

    def next_arrow(self):
        self.state = "aiming"
        self.pan = -1.0 if random.random() > 0.5 else 1.0
        self.direction = 1 if self.pan < 0 else -1
        # Geschwindigkeit leicht variieren
        self.speed = 0.015 + random.random() * 0.02
        self.audio.play_sound("click")
        
    def update(self):
        if self.state == "aiming":
            self.pan += self.direction * self.speed
            if self.pan > 1.1 or self.pan < -1.1:
                self.direction *= -1
            
            # Kontinuierliches Audio-Feedback
            if pygame.time.get_ticks() % 150 < 20:
                self.audio.play_panned_sound("click", self.pan)

        # Timer-Events verarbeiten (simuliert durch Zeitabgleich)
        now = pygame.time.get_ticks()
        if self.state == "result" and now - self.last_result_time > 2000:
            if self.round >= self.max_rounds:
                self.finish()
            else:
                self.round += 1
                self.next_arrow()

    def shoot(self):
        self.arrow_pos = self.pan
        diff = abs(self.pan)
        
        if diff < 0.05:
            round_points = 100
            self.result_text = self._("hit_perfect")
            self.audio.play_sound("confirm")
        elif diff < 0.15:
            round_points = 70
            self.result_text = self._("hit_good")
            self.audio.play_sound("hit")
        elif diff < 0.3:
            round_points = 40
            self.result_text = self._("hit_ok")
            self.audio.play_sound("click")
        else:
            round_points = 0
            self.result_text = self._("miss")
            self.audio.play_sound("bump")
            
        self.score += round_points
        self.state = "result"
        self.last_result_time = pygame.time.get_ticks()
        self.audio.speak(f"{self.result_text}. {round_points} {self._('points')}.")

    def draw(self, screen):
        # Hintergrund (Zielscheibe)
        center = (400, 300)
        colors = [(255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 215, 0)]
        for i, color in enumerate(colors):
            radius = 200 - i * 40
            pygame.draw.circle(screen, color, center, radius)
            pygame.draw.circle(screen, (100, 100, 100), center, radius, width=1)
            
        # Visuelle Hilfe für den Sound (Wandernder Punkt)
        if self.state == "aiming":
            x = 400 + self.pan * 350
            pygame.draw.circle(screen, (0, 255, 0), (int(x), 300), 15)
            # Glow
            for r in range(5):
                pygame.draw.circle(screen, (0, 255, 0, 50), (int(x), 300), 15 + r*5, width=1)
        
        # Geschossener Pfeil
        if self.state == "result":
            x = 400 + self.arrow_pos * 350
            pygame.draw.line(screen, (255, 255, 255), (int(x), 100), (int(x), 500), 5)
            # Treffermarkierung
            pygame.draw.circle(screen, (255, 255, 255), (int(x), 300), 10)
            
            # Ergebnis-Text
            font = pygame.font.SysFont("Arial", 48, bold=True)
            text_surf = font.render(self.result_text, True, (255, 255, 255))
            screen.blit(text_surf, (400 - text_surf.get_width()//2, 520))

        # Status
        font_small = pygame.font.SysFont("Arial", 24)
        status = font_small.render(f"Pfeil: {self.round}/{self.max_rounds} | Score: {self.score}", True, (255, 255, 255))
        screen.blit(status, (40, 40))
