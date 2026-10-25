import random
import pygame
import time
from games.base_game import BaseGame

class AudioTrain(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_train"
        self.instructions = self._("game_audio_train_instructions")
        
        self.score = 0
        self.lives = 3
        self.round = 1
        
        self.state = "waiting_for_start" # waiting_for_start, approaching, resolution
        self.train_type = "" # "fast" or "slow"
        self.current_track = "fast" # player's current switch state
        self.arrival_time = 0
        self.last_chug = 0

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_round(self):
        self.audio.speak(self._("round_number", idx=self.round), interrupt=True)
        self.state = "approaching"
        
        # Decide train type
        self.train_type = random.choice(["fast", "slow"])
        
        # Reset track to middle or random? Let's say it always starts on "fast"
        # Or better: player must actively set it. We won't reset it, let player remember.
        
        duration = max(1.5, 4.0 - (self.round * 0.2))
        self.arrival_time = time.monotonic() + duration
        self.last_chug = time.monotonic()
        
        # Play the horn
        if self.train_type == "fast":
            self.audio.play_sound("blip") # High pitch substitute for whistle
        else:
            self.audio.play_sound("bump") # Low pitch substitute for horn

    def update(self):
        if not self.active:
            return
            
        current_time = time.monotonic()
        
        if self.state == "approaching":
            # Play chug sound based on speed
            chug_interval = 0.2 if self.train_type == "fast" else 0.5
            if current_time - self.last_chug > chug_interval:
                self.last_chug = current_time
                # Slight panning effect just for atmosphere
                pan = random.uniform(-0.3, 0.3)
                self.audio.play_sound("hit", pan=pan)
                
            if current_time >= self.arrival_time:
                self._resolve_train()
                
        elif self.state == "resolution":
            if current_time - self.arrival_time > 1.5:
                if self.lives > 0:
                    self._start_round()
                else:
                    self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                    self.finish()

    def _resolve_train(self):
        self.state = "resolution"
        self.arrival_time = time.monotonic()
        
        if self.current_track == self.train_type:
            # Success
            self.score += 10 * self.round
            self.round += 1
            self.audio.play_sound("confirm")
            self.audio.speak(self._("train_success"), interrupt=True)
        else:
            # Crash
            self.lives -= 1
            self.audio.play_sound("error")
            self.audio.speak(self._("train_crash", lives=self.lives), interrupt=True)

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_round()
            elif self.state == "approaching":
                if event.key == pygame.K_UP:
                    self.current_track = "fast"
                    self.audio.play_sound("blip") # Feedback for switch
                elif event.key == pygame.K_DOWN:
                    self.current_track = "slow"
                    self.audio.play_sound("bump") # Feedback for switch

    def draw(self, screen):
        # Weichen-Visualisierung
        pygame.draw.rect(screen, (25, 25, 30), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (220, 160, 50), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-WEICHENSTELLER - RUNDE {self.round}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        info = small_font.render(f"Punkte: {self.score}   |   Leben: {self.lives}", True, (255, 215, 0))
        screen.blit(info, (400 - info.get_width() // 2, 195))
        
        # Gleise: Oben = Schnellzug (260), Unten = Güterzug (380)
        pygame.draw.line(screen, (160, 160, 170), (120, 270), (680, 270), 6)
        pygame.draw.line(screen, (160, 160, 170), (120, 390), (680, 390), 6)
        
        lbl_fast = small_font.render("SCHNELLZUG-GLEIS (Pfeil OBEN)", True, (100, 220, 255) if self.current_track == "fast" else (120, 120, 120))
        lbl_slow = small_font.render("GÜTERZUG-GLEIS (Pfeil UNTEN)", True, (255, 180, 80) if self.current_track == "slow" else (120, 120, 120))
        screen.blit(lbl_fast, (140, 240))
        screen.blit(lbl_slow, (140, 360))
        
        # Weichen-Hebel
        active_y = 270 if self.current_track == "fast" else 390
        pygame.draw.circle(screen, (255, 215, 0), (620, active_y), 16)
        
        # Herannahender Zug
        now = time.monotonic()
        if self.state == "approaching":
            time_left = max(0.0, self.arrival_time - now)
            prog = max(0.0, min(1.0, 1.0 - (time_left / 3.0)))
            tx = int(140 + prog * 440)
            col = (100, 220, 255) if self.train_type == "fast" else (255, 160, 60)
            pygame.draw.rect(screen, col, (tx, active_y - 14, 40, 28), border_radius=6)
            
        hint = small_font.render("Pfeil OBEN = Schnelles Gleis  |  Pfeil UNTEN = Langsames Gleis", True, (200, 200, 210))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

