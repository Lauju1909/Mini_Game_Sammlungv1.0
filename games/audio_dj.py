import random
import pygame
import time
import math
from games.base_game import BaseGame

class AudioDJ(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_dj"
        self.instructions = self._("game_audio_dj_instructions")
        
        self.score = 0
        self.lives = 3
        self.state = "waiting_for_start" # waiting_for_start, playing
        
        self.bpm = 120.0
        self.beat_interval = 60.0 / self.bpm # 0.5s per beat
        self.current_beat = 0 # 0, 1, 2 = kick, 3 = scratch cue
        self.last_beat_time = 0.0
        self.scratch_needed = False
        self.scratch_done = False
        self.measures_completed = 0
        self.target_measures = 12

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_dj(self):
        self.state = "playing"
        self.current_beat = 0
        self.last_beat_time = time.monotonic()
        self.scratch_needed = False
        self.scratch_done = False
        self.measures_completed = 0
        self.audio.speak(self._("start_go"), interrupt=True)

    def update(self):
        if not self.active:
            return

        now = time.monotonic()

        if self.state == "playing":
            if now - self.last_beat_time >= self.beat_interval:
                self.last_beat_time = now
                self.current_beat = (self.current_beat + 1) % 4
                
                if self.current_beat in [0, 1, 2]:
                    # Kick beat
                    if self.scratch_needed and not self.scratch_done:
                        # Missed beat 4 scratch
                        self.lives -= 1
                        self.audio.play_sound("error")
                        if self.lives <= 0:
                            self.audio.speak(self._("dj_gameover"), interrupt=True)
                            self.finish()
                            return
                            
                    self.scratch_needed = False
                    self.scratch_done = False
                    self.audio.play_tone(frequency=140, duration_ms=70, volume=85)
                elif self.current_beat == 3:
                    # Cue beat für Scratch!
                    self.scratch_needed = True
                    self.scratch_done = False
                    self.audio.play_tone(frequency=580, duration_ms=60, volume=70, pan=0.3)
                    self.measures_completed += 1
                    
                    if self.measures_completed >= self.target_measures:
                        self.audio.speak(self._("dj_set_complete"), interrupt=True)
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
                    self._start_dj()
            elif self.state == "playing":
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE]:
                    self._scratch()

    def _scratch(self):
        if self.scratch_needed and not self.scratch_done:
            self.scratch_done = True
            self.score += 150
            self.audio.play_sound("knifeSlice")
            self.audio.play_sound("success")
        else:
            # Zu früh oder zu spät gekratzt
            self.score = max(0, self.score - 50)
            self.audio.play_sound("bump")

    def draw(self, screen):
        # Plattenspieler Turntable
        pygame.draw.rect(screen, (20, 20, 30), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (255, 60, 140), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-DJ TURNTABLE - TAKTE: {self.measures_completed} / {self.target_measures}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        info = small_font.render(f"Punkte: {self.score}   |   Leben: {self.lives}   |   BPM: {int(self.bpm)}", True, (255, 215, 0))
        screen.blit(info, (400 - info.get_width() // 2, 195))
        
        # Schallplatte
        center = (400, 330)
        pygame.draw.circle(screen, (35, 35, 45), center, 95)
        for r in [40, 60, 80]:
            pygame.draw.circle(screen, (60, 60, 75), center, r, width=1)
        pygame.draw.circle(screen, (255, 60, 140), center, 24)
        
        # Tonarm
        pygame.draw.line(screen, (200, 200, 220), (530, 260), (450, 330), 4)
        
        # 4 Beat-LEDs
        for i in range(4):
            bx = 310 + i * 60
            is_active = (i == self.current_beat)
            led_col = (255, 255, 255) if is_active else ((255, 60, 140) if i == 3 else (60, 60, 80))
            pygame.draw.circle(screen, led_col, (bx, 440), 12)
            
        hint = small_font.render("Zähle 1-2-3-SCRATCH! Auf Schlag 4 Pfeil LINKS oder RECHTS drücken!", True, (230, 180, 210))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))
