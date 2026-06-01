import pygame
import random
import time
from games.base_game import BaseGame

class AudioBouncer(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_bouncer"
        self.instructions = self._("game_audio_bouncer_instructions")
        
        self.notes = [261, 293, 329, 349, 392, 440, 493, 523] # C-Dur Tonleiter
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.guests_served = 0
        
        self.target_sequence = []
        self.current_sequence = []
        self.is_valid_guest = False
        
        self.state = "starting"
        self.play_idx = 0
        self.play_timer = time.time() + 2.0
        
        self.generate_target()

    def generate_target(self):
        seq_length = min(7, 3 + self.level)
        self.target_sequence = [random.choice(self.notes) for _ in range(seq_length)]

    def generate_guest(self):
        self.is_valid_guest = random.choice([True, False])
        if self.is_valid_guest:
            self.current_sequence = self.target_sequence.copy()
        else:
            self.current_sequence = self.target_sequence.copy()
            
            # Verändere 1 oder 2 Töne
            num_changes = 1 if self.level < 3 else random.choice([1, 2])
            indices_to_change = random.sample(range(len(self.current_sequence)), num_changes)
            
            for idx in indices_to_change:
                note_idx = self.notes.index(self.current_sequence[idx])
                change = random.choice([-1, 1, -2, 2])
                new_idx = max(0, min(len(self.notes) - 1, note_idx + change))
                if new_idx == note_idx:
                    new_idx = note_idx + (1 if note_idx == 0 else -1)
                self.current_sequence[idx] = self.notes[new_idx]

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.state = "starting_shift"
        self.play_timer = time.time() + 2.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()

        if self.state == "starting_shift":
            if now > self.play_timer:
                self.state = "playing_target"
                self.play_idx = 0
                self.play_timer = now

        elif self.state == "playing_target":
            if now > self.play_timer:
                if self.play_idx < len(self.target_sequence):
                    freq = self.target_sequence[self.play_idx]
                    self.audio.play_tone(frequency=freq, duration_ms=250, volume=100)
                    self.play_idx += 1
                    self.play_timer = now + 0.4
                else:
                    self.state = "waiting_for_guest"
                    self.play_timer = now + 1.0

        elif self.state == "waiting_for_guest":
            if now > self.play_timer:
                self.generate_guest()
                self.audio.play_sound("bump") # Klopfen
                self.state = "playing_guest"
                self.play_idx = 0
                self.play_timer = now + 0.5

        elif self.state == "playing_guest":
            if now > self.play_timer:
                if self.play_idx < len(self.current_sequence):
                    freq = self.current_sequence[self.play_idx]
                    self.audio.play_tone(frequency=freq, duration_ms=250, volume=60) # Flüsternd
                    self.play_idx += 1
                    self.play_timer = now + 0.4
                else:
                    self.state = "waiting_for_input"

    def next_guest(self):
        if self.lives <= 0:
            self.audio.speak(self._("bouncer_gameover"), priority=2)
            time.sleep(1.5)
            self.finish()
            return

        self.guests_served += 1
        if self.guests_served >= 5:
            self.audio.play_sound("confirm")
            self.level += 1
            self.guests_served = 0
            self.score += 50
            self.generate_target()
            self.audio.speak(self._("bouncer_new_shift", level=self.level), priority=2)
            self.state = "starting_shift"
            self.play_timer = time.time() + 2.5
        else:
            self.state = "waiting_for_guest"
            self.play_timer = time.time() + 1.0

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if event.key == pygame.K_r:
                if self.state in ["waiting_for_input", "waiting_for_guest"]:
                    self.state = "playing_target"
                    self.play_idx = 0
                    self.play_timer = time.time()
                return
                
            if self.state == "waiting_for_input":
                if event.key == pygame.K_UP:
                    if self.is_valid_guest:
                        self.audio.play_sound("success")
                        self.score += 10
                    else:
                        self.audio.play_sound("error")
                        self.lives -= 1
                    self.next_guest()
                    
                elif event.key == pygame.K_DOWN:
                    if not self.is_valid_guest:
                        self.audio.play_sound("success")
                        self.score += 10
                    else:
                        self.audio.play_sound("error")
                        self.lives -= 1
                    self.next_guest()

    def draw(self, screen):
        screen.fill((20, 20, 20))
        
        font = pygame.font.SysFont("Arial", 28)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        level_surf = font.render(f"Schicht (Level): {self.level}", True, (100, 255, 100))
        guests_surf = font.render(f"Gäste in Schicht: {self.guests_served} / 5", True, (200, 200, 255))
        
        state_text = ""
        if self.state == "starting_shift": state_text = "Mache dich bereit..."
        elif self.state == "playing_target": state_text = "Passwort wird vorgespielt..."
        elif self.state == "waiting_for_guest": state_text = "Warte auf Gast..."
        elif self.state == "playing_guest": state_text = "Gast flüstert..."
        elif self.state == "waiting_for_input": state_text = "Pfeil Oben (Herein) oder Unten (Abweisen)?"
        
        state_surf = font.render(state_text, True, (255, 200, 0))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
        screen.blit(level_surf, (20, 60))
        screen.blit(guests_surf, (20, 100))
        screen.blit(state_surf, (20, 300))
