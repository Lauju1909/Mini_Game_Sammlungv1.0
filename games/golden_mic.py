import pygame
import random
import math
import time
from games.base_game import BaseGame

class GoldenMic(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "golden_mic"
        self.instructions = self._("game_golden_mic_instructions")
        self.target_x = random.randint(0, 10)
        self.target_y = random.randint(0, 10)
        self.player_x = 5
        self.player_y = 5

    def start(self):
        super().start()
        self.target_x = random.randint(0, 10)
        self.target_y = random.randint(0, 10)
        self.player_x = 5
        self.player_y = 5
        self.score = 0
        self.last_beep = 0
    def update(self):
        now = time.time()
        dist = math.sqrt((self.target_x - self.player_x)**2 + (self.target_y - self.player_y)**2)
        
        # Beep-Intervall basierend auf Distanz (0.1 bis 1.0 Sekunden)
        interval = max(0.1, min(1.0, dist / 5.0))
        
        if not hasattr(self, "last_beep"): self.last_beep = 0
        if now - self.last_beep > interval:
            # Panning basierend auf X-Position (-1 bis 1)
            pan = (self.target_x - self.player_x) / 10.0
            pan = max(-1.0, min(1.0, pan))
            self.audio.play_panned_sound("tick_001", pan)
            self.last_beep = now

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.player_y > 0: self.player_y -= 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_DOWN:
                if self.player_y < 10: self.player_y += 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if self.player_x > 0: self.player_x -= 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_RIGHT:
                if self.player_x < 10: self.player_x += 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_ESCAPE: self.finish()
            
            # Check ob Ziel erreicht
            if self.player_x == self.target_x and self.player_y == self.target_y:
                self.score = 500
                self.audio.play_sound("success")
                self.audio.speak(self._("mic_found"))
                self.finish()
