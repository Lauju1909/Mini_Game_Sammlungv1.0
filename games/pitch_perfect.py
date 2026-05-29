import pygame
import random
import math
from games.base_game import BaseGame

class PitchPerfect(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "pitch_perfect"
        self.instructions = self._("game_pitch_perfect_instructions")
        
        self.reference_freq = random.uniform(220, 880)
        self.player_freq = random.uniform(220, 880)
        while abs(self.player_freq - self.reference_freq) < 50:
            self.player_freq = random.uniform(220, 880)
            
        self.round = 1
        self.max_rounds = 3
        self.state = "playing"
        self.playing_reference = True
        self.last_toggle = 0
        self.toggle_interval = 1000 # ms
        
        self.diff_threshold = 5.0 # Hz for success
        self.current_channel = None

    def start(self):
        super().start()
        self.audio.speak(self._("adjust_pitch_to_match"))
        self.last_toggle = pygame.time.get_ticks()
        self.playing_reference = True
        self.current_channel = self.audio.create_tone_loop(self.reference_freq)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_toggle > self.toggle_interval:
            self.playing_reference = not self.playing_reference
            self.last_toggle = now
            if self.current_channel:
                self.audio.stop_sound(self.current_channel)
            
            freq = self.reference_freq if self.playing_reference else self.player_freq
            self.current_channel = self.audio.create_tone_loop(freq)

        # Since we don't have dynamic sound generation in AudioManager yet, 
        # let's assume we use specific sounds for low/high or a beep tool.
        # For the sake of this demo, we'll use a placeholder "beep" sound if it exists.
        
    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.player_freq < 2000:
                    self.player_freq += 10
                    if not self.playing_reference:
                        if self.current_channel:
                            self.audio.stop_sound(self.current_channel)
                        self.current_channel = self.audio.create_tone_loop(self.player_freq)
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_DOWN:
                if self.player_freq > 50:
                    self.player_freq -= 10
                    if not self.playing_reference:
                        if self.current_channel:
                            self.audio.stop_sound(self.current_channel)
                        self.current_channel = self.audio.create_tone_loop(self.player_freq)
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_RETURN:
                diff = abs(self.player_freq - self.reference_freq)
                if diff < self.diff_threshold:
                    self.score += 100 // self.round
                    self.audio.play_sound("success")
                else:
                    self.audio.play_sound("error")
                
                if self.current_channel:
                    self.audio.stop_sound(self.current_channel)
                    self.current_channel = None

                self.round += 1
                if self.round > self.max_rounds:
                    self.finish()
                else:
                    self.next_round()

    def next_round(self):
        self.reference_freq = random.uniform(220, 880)
        self.player_freq = random.uniform(220, 880)
        while abs(self.player_freq - self.reference_freq) < 50:
            self.player_freq = random.uniform(220, 880)
        self.last_toggle = pygame.time.get_ticks()
        self.playing_reference = True
        self.current_channel = self.audio.create_tone_loop(self.reference_freq)

    def draw(self, screen):
        screen.fill((30, 20, 50))
        font = pygame.font.SysFont("Outfit, Arial", 40)
        title = font.render(self._("game_pitch_perfect"), True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        # Visualizing the waves
        for i in range(800):
            # Reference wave (dimmed)
            ref_y = 300 + math.sin(i * 0.05 * (self.reference_freq/440)) * 50
            pygame.draw.circle(screen, (100, 100, 255, 100), (i, int(ref_y)), 1)
            
            # Player wave
            play_y = 300 + math.sin(i * 0.05 * (self.player_freq/440)) * 50
            pygame.draw.circle(screen, (0, 255, 255), (i, int(play_y)), 2)
            
        # Indicator for who is playing
        color = (255, 255, 255) if self.playing_reference else (0, 255, 255)
        label = "REFERENCE" if self.playing_reference else "YOUR PITCH"
        txt = font.render(label, True, color)
        screen.blit(txt, (400 - txt.get_width()//2, 500))
