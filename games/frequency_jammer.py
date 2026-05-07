import pygame
import random
import math
from games.base_game import BaseGame

class FrequencyJammer(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "frequency_jammer"
        self.instructions = self._("game_frequency_jammer_instructions")
        
        self.target_freq = random.uniform(88.0, 108.0)
        self.current_freq = random.uniform(88.0, 108.0)
        
        self.round = 1
        self.max_rounds = 3
        self.threshold = 0.2
        
        self.static_channel = None
        self.signal_channel = None
        
        # Pre-generate noise surface
        self.noise_surf = pygame.Surface((800, 600), pygame.SRCALPHA)
        for _ in range(2000):
            x = random.randint(0, 799)
            y = random.randint(0, 599)
            self.noise_surf.set_at((x, y), (255, 255, 255, random.randint(20, 100)))

    def start(self):
        super().start()
        self.audio.speak(self._("tune_to_clear_signal"), interrupt=False)
        self.static_channel = self.audio.play_looping_sound("scratch_001")
        self.signal_channel = self.audio.create_tone_loop(440) # Signal als reiner Ton
        self.update_volumes()

    def update(self):
        self.update_volumes()

    def update_volumes(self):
        diff = abs(self.current_freq - self.target_freq)
        # Rauschen wird lauter, wenn man sich entfernt
        noise_vol = min(0.8, diff / 2.0)
        # Signal wird lauter, wenn man nah dran ist
        signal_vol = max(0.0, 1.0 - (diff / 0.5))
        
        if self.static_channel:
            self.audio.set_channel_volume(self.static_channel, noise_vol)
        if self.signal_channel:
            self.audio.set_channel_volume(self.signal_channel, signal_vol)

    def finish(self):
        if self.static_channel:
            self.audio.stop_sound(self.static_channel)
        if self.signal_channel:
            self.audio.stop_sound(self.signal_channel)
        super().finish()

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.current_freq -= 0.1
                if self.current_freq < 88.0: self.current_freq = 88.0
                self.audio.play_sound("click")
            elif event.key == pygame.K_RIGHT:
                self.current_freq += 0.1
                if self.current_freq > 108.0: self.current_freq = 108.0
                self.audio.play_sound("click")
            elif event.key == pygame.K_RETURN:
                diff = abs(self.current_freq - self.target_freq)
                if diff < self.threshold:
                    self.score += 100 // self.round
                    self.audio.play_sound("success")
                else:
                    self.audio.play_sound("error")
                
                self.round += 1
                if self.round > self.max_rounds:
                    self.finish()
                else:
                    self.next_round()

    def next_round(self):
        self.target_freq = random.uniform(88.0, 108.0)
        self.current_freq = random.uniform(88.0, 108.0)

    def draw(self, screen):
        screen.fill((20, 20, 20))
        font = pygame.font.SysFont("Courier New", 40)
        
        # Static visualization (blended noise)
        diff = abs(self.current_freq - self.target_freq)
        alpha = int(min(255, diff * 150))
        self.noise_surf.set_alpha(alpha)
        screen.blit(self.noise_surf, (0, 0))

        # Radio Scale
        pygame.draw.rect(screen, (50, 50, 50), (100, 300, 600, 50))
        for i in range(880, 1081, 2):
            freq = i / 10.0
            x = 100 + (freq - 88.0) / (108.0 - 88.0) * 600
            h = 20 if i % 10 == 0 else 10
            pygame.draw.line(screen, (150, 150, 150), (x, 300), (x, 300 + h), 2)
            
            if i % 50 == 0:
                txt = font.render(str(freq), True, (150, 150, 150))
                screen.blit(txt, (x - txt.get_width()//2, 360))

        # Tuning Needle
        needle_x = 100 + (self.current_freq - 88.0) / (108.0 - 88.0) * 600
        pygame.draw.line(screen, (255, 0, 0), (needle_x, 280), (needle_x, 350), 4)
        
        # Frequency Display
        display_text = font.render(f"{self.current_freq:.1f} MHz", True, (0, 255, 0))
        pygame.draw.rect(screen, (0, 40, 0), (300, 150, 200, 60))
        screen.blit(display_text, (400 - display_text.get_width()//2, 160))
