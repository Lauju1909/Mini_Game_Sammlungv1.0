import pygame
import random
import time
from games.base_game import BaseGame

class AudioMorseCode(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_morse_code"
        self.instructions = self._("game_audio_morse_code_instructions")
        
        self.score = 0
        self.lives = 3
        self.level = 1
        
        self.sequence = []
        self.play_index = 0
        self.input_index = 0
        
        self.state = "starting"
        self.play_timer = time.time() + 2.0
        
        self.is_space_pressed = False
        self.space_down_time = 0
        self.last_beep = 0
        
        self.generate_sequence()

    def generate_sequence(self):
        length = min(10, 2 + self.level)
        self.sequence = [random.choice([".", "-"]) for _ in range(length)]
        self.play_index = 0
        self.input_index = 0

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.state = "playing_sequence"
        self.play_timer = time.time() + 2.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()

        if self.state == "playing_sequence":
            if now > self.play_timer:
                if self.play_index < len(self.sequence):
                    symbol = self.sequence[self.play_index]
                    dur = 150 if symbol == "." else 400
                    self.audio.play_tone(frequency=800, duration_ms=dur, volume=80)
                    self.play_index += 1
                    self.play_timer = now + (dur / 1000.0) + 0.25 # Ton-Dauer + Pause
                else:
                    self.audio.play_sound("swipe") # Signal: Du bist dran!
                    self.state = "player_turn"
                    self.input_index = 0

        elif self.state == "player_turn":
            # Kontinuierlichen Ton erzeugen, wenn Leertaste gehalten wird
            if self.is_space_pressed:
                if now - self.last_beep > 0.04:
                    self.last_beep = now
                    self.audio.play_tone(frequency=800, duration_ms=60, volume=80)

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if event.key == pygame.K_r and self.state == "player_turn":
                self.state = "playing_sequence"
                self.play_index = 0
                self.input_index = 0
                self.play_timer = time.time() + 0.5
                return

            if self.state == "player_turn":
                if event.key == pygame.K_SPACE:
                    self.is_space_pressed = True
                    self.space_down_time = time.time()

        elif event.type == pygame.KEYUP:
            if self.state == "player_turn":
                if event.key == pygame.K_SPACE and self.is_space_pressed:
                    self.is_space_pressed = False
                    duration = time.time() - self.space_down_time
                    
                    entered = "." if duration < 0.25 else "-"
                    expected = self.sequence[self.input_index]
                    
                    if entered == expected:
                        # Richtiges Zeichen
                        self.input_index += 1
                        
                        if self.input_index >= len(self.sequence):
                            # Sequenz erfolgreich beendet!
                            self.audio.play_sound("success")
                            self.score += len(self.sequence) * 10
                            self.level += 1
                            self.generate_sequence()
                            self.audio.speak(self._("morse_code_level_up", level=self.level), priority=2)
                            self.state = "playing_sequence"
                            self.play_timer = time.time() + 2.5
                    else:
                        # Falsches Zeichen
                        self.audio.play_sound("error")
                        self.lives -= 1
                        
                        if self.lives <= 0:
                            self.audio.speak(self._("morse_code_gameover"), priority=2)
                            self.sleep(2)
                            self.finish()
                        else:
                            self.audio.speak(self._("morse_code_wrong"), priority=1)
                            self.state = "playing_sequence"
                            self.play_index = 0
                            self.input_index = 0
                            self.play_timer = time.time() + 2.0

    def draw(self, screen):
        screen.fill((10, 30, 10))
        
        font = pygame.font.SysFont("Arial", 28)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        level_surf = font.render(f"Level: {self.level}", True, (100, 255, 100))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
        screen.blit(level_surf, (20, 60))
        
        # Zeige die Ziel-Sequenz (nur visuell, da blindengerecht)
        seq_text = " ".join(self.sequence)
        seq_surf = font.render(f"Sequenz: {seq_text}", True, (150, 150, 150))
        screen.blit(seq_surf, (20, 150))
        
        # Zeige den Fortschritt
        entered_seq = " ".join(self.sequence[:self.input_index])
        prog_surf = font.render(f"Eingegeben: {entered_seq}", True, (255, 255, 0))
        screen.blit(prog_surf, (20, 200))
        
        state_text = ""
        if self.state == "playing_sequence":
            state_text = "Höre gut zu..."
        elif self.state == "player_turn":
            state_text = "Tippe die Sequenz! (kurz = Punkt, lang = Strich)"
            
        state_surf = font.render(state_text, True, (0, 255, 255))
        screen.blit(state_surf, (20, 300))
