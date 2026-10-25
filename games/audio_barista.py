import random
import pygame
import time
import math
from games.base_game import BaseGame

class AudioBarista(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_barista"
        self.instructions = self._("game_audio_barista_instructions")
        
        self.score = 0
        self.round = 1
        self.max_rounds = 5
        self.state = "waiting_for_start" # waiting_for_start, pouring, round_over
        self.is_pouring = False
        self.fill_level = 0.0 # 0.0 to 1.2 (1.0 = rim, >1.0 = spill)
        self.pour_speed = 0.35 # per second
        self.pour_start_time = 0.0
        self.last_audio_tick = 0.0
        self.result_timer = 0.0

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_order(self):
        self.state = "pouring"
        self.fill_level = 0.0
        self.is_pouring = False
        self.pour_speed = random.uniform(0.3, 0.45) + (self.round * 0.03)
        self.audio.speak(self._("barista_order_ready", round=self.round), interrupt=True)

    def update(self):
        if not self.active:
            return

        now = time.monotonic()

        if self.state == "pouring" and self.is_pouring:
            dt = now - self.pour_start_time
            self.pour_start_time = now
            self.fill_level += self.pour_speed * dt
            
            # Akustische Resonanz: Frequenz steigt mit Füllstand (220 Hz bis 880 Hz)
            if now - self.last_audio_tick > 0.08:
                self.last_audio_tick = now
                freq = int(220 + min(self.fill_level, 1.1) * 600)
                vol = min(100, int(50 + self.fill_level * 50))
                self.audio.play_tone(frequency=freq, duration_ms=70, volume=vol)
                
            # Überlauf bei > 1.05
            if self.fill_level >= 1.08:
                self._stop_pouring(overflow=True)
                
        elif self.state == "round_over":
            if now >= self.result_timer:
                if self.round < self.max_rounds:
                    self.round += 1
                    self._start_order()
                else:
                    self.finish()

    def handle_input(self, event):
        if not self.active:
            return

        super().handle_input(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return

            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_order()
            elif self.state == "pouring":
                if event.key == pygame.K_SPACE and not self.is_pouring:
                    self.is_pouring = True
                    self.pour_start_time = time.monotonic()
                    self.last_audio_tick = time.monotonic()
                    self.audio.play_sound("blip")
                    
        elif event.type == pygame.KEYUP:
            if self.state == "pouring" and self.is_pouring:
                if event.key == pygame.K_SPACE:
                    self._stop_pouring(overflow=False)

    def _stop_pouring(self, overflow=False):
        self.is_pouring = False
        self.state = "round_over"
        self.result_timer = time.monotonic() + 2.0
        
        if overflow:
            self.audio.play_sound("error")
            self.audio.speak(self._("barista_overflow"), interrupt=True)
        else:
            diff = abs(1.0 - self.fill_level)
            if diff <= 0.08:
                # Perfekt eingeschenkt
                self.score += 300
                self.audio.play_sound("success")
                self.audio.speak(self._("barista_perfect"), interrupt=True)
            elif diff <= 0.2:
                # Gut
                self.score += 150
                self.audio.play_sound("confirm")
                self.audio.speak(self._("barista_good"), interrupt=True)
            else:
                # Zu wenig
                self.audio.play_sound("bump")
                self.audio.speak(self._("barista_too_low"), interrupt=True)

    def draw(self, screen):
        # Barista-Kaffee-Station
        pygame.draw.rect(screen, (35, 25, 20), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (200, 140, 80), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-BARISTA - TASSE {self.round} / {self.max_rounds}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        # Kaffeetasse Kontur
        cup_rect = pygame.Rect(320, 250, 160, 170)
        pygame.draw.rect(screen, (60, 50, 45), cup_rect, border_radius=12)
        pygame.draw.rect(screen, (220, 220, 220), cup_rect, width=4, border_radius=12)
        # Henkel
        pygame.draw.arc(screen, (220, 220, 220), (460, 280, 50, 100), -math.pi/2, math.pi/2, 4)
        
        # Flüssigkeits-Füllstand
        clamped_level = min(1.0, max(0.0, self.fill_level))
        fill_h = int(clamped_level * 160)
        if fill_h > 0:
            fill_y = 420 - fill_h
            fill_col = (110, 60, 30) if self.fill_level <= 1.0 else (255, 70, 50)
            pygame.draw.rect(screen, fill_col, (324, fill_y, 152, fill_h), border_radius=8)
            # Schaumkrone oben
            pygame.draw.rect(screen, (240, 220, 190), (324, fill_y, 152, 12), border_radius=4)
            
        # Rand-Markierung (100% Markierung)
        pygame.draw.line(screen, (255, 215, 0), (315, 260), (485, 260), 2)
        
        hint = small_font.render("LEERTASTE gedrückt halten zum Eingießen, am Rand loslassen!", True, (230, 200, 170))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))
