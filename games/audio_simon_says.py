import pygame
import time
import random
from games.base_game import BaseGame

class AudioSimonSays(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_simon_says"
        self.instructions = self._("game_audio_simon_says_instructions")
        
        self.score = 0
        self.lives = 3
        self.sequence = []
        self.player_sequence = []
        
        self.state = "waiting_for_start" # waiting_for_start, playing_sequence, player_turn, waiting_next_round
        self.seq_idx = 0
        self.last_tone_time = 0.0
        
    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_game(self):
        self.score = 0
        self.lives = 3
        self.sequence = []
        self._next_round()

    def _next_round(self):
        self.sequence.append(random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]))
        self.player_sequence = []
        self.state = "playing_sequence"
        self.seq_idx = 0
        self.last_tone_time = time.monotonic()

    def _play_tone_for_key(self, key):
        if key == pygame.K_UP:
            self.audio.play_tone(600, duration_ms=400, pan=0.0)
        elif key == pygame.K_DOWN:
            self.audio.play_tone(300, duration_ms=400, pan=0.0)
        elif key == pygame.K_LEFT:
            self.audio.play_tone(450, duration_ms=400, pan=-1.0)
        elif key == pygame.K_RIGHT:
            self.audio.play_tone(450, duration_ms=400, pan=1.0)

    def update(self):
        if not self.active:
            return
            
        if self.state == "playing_sequence":
            current_time = time.monotonic()
            if current_time - self.last_tone_time > 0.6: # Wait 600ms between tones
                if self.seq_idx < len(self.sequence):
                    key = self.sequence[self.seq_idx]
                    self._play_tone_for_key(key)
                    self.seq_idx += 1
                    self.last_tone_time = current_time
                else:
                    self.state = "player_turn"
                    self.audio.speak(self._("simon_your_turn"), interrupt=False)

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
                    self._start_game()
                    
            elif self.state == "player_turn":
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self._play_tone_for_key(event.key)
                    self.player_sequence.append(event.key)
                    
                    idx = len(self.player_sequence) - 1
                    if self.player_sequence[idx] == self.sequence[idx]:
                        # Correct so far
                        if len(self.player_sequence) == len(self.sequence):
                            # Completed sequence correctly
                            self.audio.play_sound("success")
                            self.score += 10 * len(self.sequence)
                            # Wait a bit before next round
                            self.state = "waiting_next_round"
                            pygame.time.set_timer(pygame.USEREVENT + 1, 1500) # trigger next round in 1.5s
                    else:
                        # Wrong key
                        self.lives -= 1
                        self.audio.play_sound("error")
                        if self.lives > 0:
                            self.audio.speak(self._("simon_wrong_lives", lives=self.lives), interrupt=True)
                            # Repeat the SAME sequence
                            self.player_sequence = []
                            self.state = "playing_sequence"
                            self.seq_idx = 0
                            self.last_tone_time = time.monotonic() + 1.0
                        else:
                            self.state = "game_over"
                            self.audio.speak(self._("simon_gameover"), interrupt=True)
                            self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                            self.finish()

        if event.type == pygame.USEREVENT + 1 and self.state == "waiting_next_round":
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            self._next_round()

    def draw(self, screen):
        # Simon-Pads
        pygame.draw.rect(screen, (20, 20, 35), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (100, 140, 240), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-SENSO - FOLGE: {len(self.sequence)}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        info = small_font.render(f"Punkte: {self.score}   |   Leben: {self.lives}", True, (255, 215, 0))
        screen.blit(info, (400 - info.get_width() // 2, 195))
        
        # 4 Pads: Oben (Rot), Unten (Blau), Links (Grün), Rechts (Gelb)
        pads = [
            (pygame.K_UP, (400, 250), (255, 60, 60), "OBEN (HOCH)"),
            (pygame.K_DOWN, (400, 390), (60, 120, 255), "UNTEN (TIEF)"),
            (pygame.K_LEFT, (280, 320), (50, 220, 80), "LINKS"),
            (pygame.K_RIGHT, (520, 320), (255, 220, 50), "RECHTS"),
        ]
        
        active_key = None
        if self.state == "playing_sequence" and self.seq_idx > 0 and self.seq_idx <= len(self.sequence):
            active_key = self.sequence[self.seq_idx - 1]
            
        for k, (px, py), col, label in pads:
            is_active = (k == active_key)
            radius = 38 if is_active else 30
            pad_col = (255, 255, 255) if is_active else col
            pygame.draw.circle(screen, pad_col, (px, py), radius)
            pygame.draw.circle(screen, col, (px, py), radius - 4)
            
        hint = small_font.render("Wiederhole die Tonfolge mit den Pfeiltasten", True, (180, 180, 220))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

