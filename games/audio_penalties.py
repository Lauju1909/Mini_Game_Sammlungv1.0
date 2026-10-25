import random
import pygame
import time
import math
from games.base_game import BaseGame

class AudioPenalties(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_penalties"
        self.instructions = self._("game_audio_penalties_instructions")
        
        self.score = 0
        self.round = 1
        self.max_rounds = 5
        self.state = "waiting_for_start" # waiting_for_start, keeper_shuffling, ready_to_shoot, shot_result
        self.keeper_pos = "center" # "left", "center", "right"
        self.shot_taken = None
        self.shuffle_end_time = 0.0
        self.last_shuffle_tick = 0.0
        self.result_timer = 0.0

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_penalty(self):
        self.state = "keeper_shuffling"
        # Torwart entscheidet sich für eine Ecke oder bleibt mittig
        self.keeper_pos = random.choice(["left", "center", "right"])
        self.shot_taken = None
        self.shuffle_end_time = time.monotonic() + random.uniform(1.8, 3.2)
        self.last_shuffle_tick = time.monotonic()
        self.audio.speak(self._("round_number", idx=self.round), interrupt=True)

    def update(self):
        if not self.active:
            return
            
        now = time.monotonic()
        
        if self.state == "keeper_shuffling":
            # Torwart-Schritte akustisch pannen
            if now - self.last_shuffle_tick > 0.35:
                self.last_shuffle_tick = now
                pan = -0.75 if self.keeper_pos == "left" else (0.75 if self.keeper_pos == "right" else 0.0)
                freq = 240 if self.keeper_pos == "center" else (320 if self.keeper_pos == "right" else 200)
                self.audio.play_tone(frequency=freq, duration_ms=60, volume=65, pan=pan)
                
            if now >= self.shuffle_end_time:
                self.state = "ready_to_shoot"
                self.audio.play_sound("confirm")
                self.audio.speak(self._("penalties_shoot_now"), interrupt=False)
                
        elif self.state == "shot_result":
            if now >= self.result_timer:
                if self.round < self.max_rounds:
                    self.round += 1
                    self._start_penalty()
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
                    self._start_penalty()
            elif self.state == "ready_to_shoot":
                if event.key == pygame.K_LEFT:
                    self._shoot("left")
                elif event.key == pygame.K_RIGHT:
                    self._shoot("right")
                elif event.key in [pygame.K_UP, pygame.K_SPACE, pygame.K_RETURN]:
                    self._shoot("center")

    def _shoot(self, aim):
        self.state = "shot_result"
        self.shot_taken = aim
        self.result_timer = time.monotonic() + 2.0
        
        # Schuss-Sound mit Panning
        pan = -0.8 if aim == "left" else (0.8 if aim == "right" else 0.0)
        self.audio.play_sound("bump", pan=pan)
        
        if aim != self.keeper_pos:
            # Tor!
            self.score += 200
            self.audio.play_sound("success")
            self.audio.speak(self._("penalties_goal", score=self.score), interrupt=True)
        else:
            # Gehalten!
            self.audio.play_sound("error")
            self.audio.speak(self._("penalties_saved"), interrupt=True)

    def draw(self, screen):
        # Elfmeter-Stadion
        pygame.draw.rect(screen, (20, 35, 20), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (80, 220, 100), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-ELFMETER - SCHUSS {self.round} / {self.max_rounds}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        # Tor-Rahmen
        goal_rect = pygame.Rect(200, 240, 400, 160)
        pygame.draw.rect(screen, (240, 240, 240), goal_rect, width=4)
        pygame.draw.line(screen, (100, 150, 100), (200, 400), (600, 400), 2)
        
        # Torwart Position
        keeper_x = {"left": 280, "center": 400, "right": 520}.get(self.keeper_pos, 400)
        pygame.draw.rect(screen, (255, 140, 30), (keeper_x - 22, 280, 44, 90), border_radius=8)
        pygame.draw.circle(screen, (255, 200, 160), (keeper_x, 265), 16)
        
        # Elfmeterpunkt & Ball
        ball_pos = (400, 450)
        if self.shot_taken:
            ball_pos = {"left": (280, 300), "center": (400, 300), "right": (520, 300)}.get(self.shot_taken, (400, 300))
        pygame.draw.circle(screen, (255, 255, 255), ball_pos, 12)
        pygame.draw.circle(screen, (0, 0, 0), ball_pos, 12, width=2)
        
        hint = small_font.render("Pfeil LINKS / RECHTS = Ecke anvisieren  |  OBEN / LEERTASTE = Mitte", True, (190, 230, 190))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))
