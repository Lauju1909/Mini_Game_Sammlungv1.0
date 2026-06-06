import pygame
import random
from games.base_game import BaseGame

class AudioBalance(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "audio_balance"
        self.instructions = self._("game_audio_balance_instructions")
        self.balance = 0.0  # -1.0 bis 1.0
        self.drift = 0.0
        self.last_drift_change = 0
        self.game_time = 30000 # 30 Sekunden
        self.start_ticks = 0
        self.is_running = False

    def start(self):
        super().start()
        self.balance = 0.0
        self.drift = random.uniform(-0.02, 0.02)
        self.start_ticks = pygame.time.get_ticks()
        self.is_running = True
        self.audio.speak(self._("welcome") + " " + self._("game_audio_balance"), interrupt=False)
        # Start continuous looping sound
        self.loop_channel = self.audio.play_looping_sound("back_001")
        if not self.loop_channel:
             self.loop_channel = self.audio.play_looping_sound("scratch_001")
        self.update_pan()

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.balance -= 0.15
                self.update_pan()
            elif event.key == pygame.K_RIGHT:
                self.balance += 0.15
                self.update_pan()

    def update_pan(self):
        if self.loop_channel:
            # Berechne Lautstärke für links und rechts
            left = max(0.0, min(1.0, (1.0 - self.balance)))
            right = max(0.0, min(1.0, (1.0 + self.balance)))
            self.audio.set_channel_volume(self.loop_channel, left, right)

    def update(self):
        if not self.is_running:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.start_ticks

        if elapsed > self.game_time:
            self.finish_game()
            return

        # Drift anwenden
        self.balance += self.drift
        self.update_pan()
        
        # Drift zufällig ändern
        if now - self.last_drift_change > 800:
            self.drift += random.uniform(-0.015, 0.015)
            self.drift = max(-0.06, min(0.06, self.drift))
            self.last_drift_change = now

        # Überprüfen ob verloren
        if abs(self.balance) > 1.2:
            self.audio.stop_sound(self.loop_channel)
            self.audio.play_sound("error")
            self.audio.speak(self._("out_of_balance"))
            self.finish()
            self.is_running = False

        # Score basierend auf Genauigkeit
        if abs(self.balance) < 0.25:
            self.score += 1

    def finish_game(self):
        self.audio.stop_sound(self.loop_channel)
        self.audio.play_sound("success")
        self.audio.speak(self._("game_over_score", score=self.score))
        self.finish()
        self.is_running = False

    def draw(self, screen):
        pygame.draw.line(screen, (100, 100, 100), (100, 300), (700, 300), 2)
        pygame.draw.circle(screen, (0, 255, 0), (400, 300), 10)
        
        # Balken
        bar_x = 400 + int(self.balance * 300)
        pygame.draw.rect(screen, (255, 215, 0), (bar_x - 5, 270, 10, 60))
        
        # Zeitbalken
        elapsed = pygame.time.get_ticks() - self.start_ticks
        progress = 1.0 - (elapsed / self.game_time)
        pygame.draw.rect(screen, (0, 150, 255), (100, 500, int(600 * progress), 20))
