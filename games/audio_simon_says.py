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
        self.audio.speak(self.instructions, interrupt=False)
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
        self.last_tone_time = time.time()

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
            current_time = time.time()
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
                            self.last_tone_time = time.time() + 1.0
                        else:
                            self.state = "game_over"
                            self.audio.speak(self._("simon_gameover"), interrupt=True)
                            self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                            self.finish()

        if event.type == pygame.USEREVENT + 1 and self.state == "waiting_next_round":
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            self._next_round()
