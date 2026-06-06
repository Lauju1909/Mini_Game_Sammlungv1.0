import pygame
import random
from games.base_game import BaseGame

class MorseRunner(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "morse_runner"
        self.instructions = self._("game_morse_runner_instructions")
        self.codes = {
            "A": [0, 1],
            "B": [1, 0, 0, 0],
            "C": [1, 0, 1, 0],
            "D": [1, 0, 0],
            "E": [0],
            "S": [0, 0, 0],
            "O": [1, 1, 1],
            "T": [1]
        }
        self.current_char = random.choice(list(self.codes.keys()))
        self.state = "playing_code"
        self.round = 1
        self.max_rounds = 10
        self.code_index = 0
        self.last_action_time = 0
        self.tone_interval = 400 # ms
        self.options = []

    def start(self):
        super().start()
        self.last_action_time = pygame.time.get_ticks()
        self.code_index = 0
        self.state = "playing_code"

    def update(self):
        now = pygame.time.get_ticks()
        
        if self.state == "playing_code":
            if now - self.last_action_time > self.tone_interval:
                code = self.codes[self.current_char]
                if self.code_index < len(code):
                    tone = code[self.code_index]
                    if tone == 0:
                        self.audio.play_tone(800, duration_ms=150) # Dot
                        self.tone_interval = 300
                    else:
                        self.audio.play_tone(800, duration_ms=400) # Dash
                        self.tone_interval = 550
                    self.code_index += 1
                    self.last_action_time = now
                else:
                    # Fertig mit Abspielen
                    self.state = "giving_options"
                    self.last_action_time = now
                    self.announce_options()

    def announce_options(self):
        # Pick 2 other random characters as distractions
        other_chars = [c for c in self.codes.keys() if c != self.current_char]
        distractions = random.sample(other_chars, 2)
        self.options = [self.current_char] + distractions
        random.shuffle(self.options)
        
        opt_parts = []
        for i, opt in enumerate(self.options):
            char_name = self._(f"morse_{opt.lower()}")
            opt_parts.append(f"{i+1}: {char_name}")
        
        self.audio.speak(", ".join(opt_parts))

    def handle_input(self, event):
        super().handle_input(event)
        if not self.active: return
        if event.type == pygame.KEYDOWN:
            if self.state == "giving_options":
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    idx = event.key - pygame.K_1
                    if self.options[idx] == self.current_char:
                        self.score += 20
                        self.audio.play_sound("success")
                    else:
                        self.audio.play_sound("error")
                    
                    self.round += 1
                    if self.round > self.max_rounds:
                        self.finish()
                    else:
                        self.current_char = random.choice(list(self.codes.keys()))
                        self.code_index = 0
                        self.state = "playing_code"
                        self.last_action_time = pygame.time.get_ticks()
            elif event.key == pygame.K_r: # Repeat
                if self.state == "giving_options":
                    self.code_index = 0
                    self.state = "playing_code"
                    self.last_action_time = pygame.time.get_ticks()

    def draw(self, screen):
        # Premium Visuals for Morse Runner
        screen.fill((10, 20, 30))
        font = pygame.font.SysFont("Outfit, Arial", 50)
        title = font.render(self._("game_morse_runner"), True, (0, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        # Round info
        round_text = font.render(f"{self._('round_number', idx=self.round)} / {self.max_rounds}", True, (200, 200, 200))
        screen.blit(round_text, (400 - round_text.get_width()//2, 120))
        
        # Status
        status_text = ""
        if self.state == "playing_code":
            status_text = "..."
            # Visualizing the dots and dashes
            code = self.codes[self.current_char]
            for i in range(self.code_index):
                x = 400 - (len(code)*40)//2 + i*40
                if code[i] == 0:
                    pygame.draw.circle(screen, (0, 255, 0), (x, 300), 10)
                else:
                    pygame.draw.rect(screen, (0, 255, 0), (x-15, 290, 30, 20))
        elif self.state == "giving_options":
            status_text = "?"
            # Show keys 1, 2, 3
            for i in range(3):
                rect = pygame.Rect(150 + i*180, 400, 140, 80)
                pygame.draw.rect(screen, (50, 50, 80), rect, border_radius=15)
                key_surf = font.render(str(i+1), True, (255, 255, 255))
                screen.blit(key_surf, (rect.centerx - key_surf.get_width()//2, rect.centery - key_surf.get_height()//2))
        
        st_surf = font.render(status_text, True, (255, 255, 0))
        screen.blit(st_surf, (400 - st_surf.get_width()//2, 280))
