import pygame
import time
import random
from games.base_game import BaseGame

class AudioFencer(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_fencer"
        self.instructions = self._("game_audio_fencer_instructions")
        
        self.score = 0
        self.state = "waiting_for_start"
        self.lives = 3
        self.opponent_health = 3
        self.round_num = 1
        
        self.fencer_state = "idle" # idle, approaching, attacking, blocked, hit
        self.state_time = 0.0
        self.action_delay = 0.0
        
        self.last_update = time.monotonic()

    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_game(self):
        self.state = "playing"
        self.score = 0
        self.lives = 3
        self.opponent_health = 3
        self.round_num = 1
        self.audio.speak(self._("fencer_fight_start"), interrupt=True)
        self._reset_round()

    def _reset_round(self):
        self.fencer_state = "idle"
        self.action_delay = random.uniform(1.0, 3.0)
        self.state_time = time.monotonic()

    def update(self):
        if not self.active or self.state != "playing":
            return
            
        current_time = time.monotonic()
        elapsed = current_time - self.state_time
        
        if self.fencer_state == "idle":
            if elapsed >= self.action_delay:
                self.fencer_state = "approaching"
                self.state_time = current_time
                self.action_delay = random.uniform(0.5, 1.5)
                # Play footstep or inhale
                self.audio.play_sound("scroll_001") # Using scroll as a stand-in for rustling/approaching
                
        elif self.fencer_state == "approaching":
            if elapsed >= self.action_delay:
                self.fencer_state = "attacking"
                self.state_time = current_time
                self.action_delay = 0.4 # Window to block
                # Play whoosh
                self.audio.play_sound("scratch_001") # Using scratch as sword swing
                
        elif self.fencer_state == "attacking":
            if elapsed >= self.action_delay:
                # Player missed the block window
                self._player_hit()
                
        elif self.fencer_state == "blocked":
            # Window for player to counter attack
            if elapsed >= 1.0:
                # Player missed the counter attack window, opponent resets
                self.audio.play_sound("toggle_001")
                self._reset_round()

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_game()
                    
            elif self.state == "playing":
                if event.key == pygame.K_DOWN:
                    self._try_block()
                elif event.key == pygame.K_UP:
                    self._try_attack()

    def _try_block(self):
        current_time = time.monotonic()
        elapsed = current_time - self.state_time
        
        if self.fencer_state == "attacking" and elapsed < self.action_delay:
            # Successful block!
            self.fencer_state = "blocked"
            self.state_time = current_time
            self.audio.play_sound("metalClick")
            self.score += 50
        else:
            # Blocked at the wrong time! Open to attack
            if self.fencer_state in ["idle", "approaching"]:
                self._player_hit()

    def _try_attack(self):
        if self.fencer_state == "blocked":
            # Successful counter attack!
            self.audio.play_sound("success")
            self.opponent_health -= 1
            self.score += 200
            
            if self.opponent_health <= 0:
                self.audio.speak(self._("fencer_enemy_defeated"), interrupt=True)
                self.round_num += 1
                self.opponent_health = 3 + self.round_num
                self.lives = min(3, self.lives + 1)
                self.score += 500
                self._reset_round()
            else:
                self.audio.speak(self._("fencer_enemy_hit", hp=self.opponent_health), interrupt=True)
                self._reset_round()
        else:
            # Attacked blindly, get hit
            self._player_hit()

    def _player_hit(self):
        self.lives -= 1
        self.audio.play_sound("error")
        if self.lives > 0:
            self.audio.speak(self._("fencer_player_hit", lives=self.lives), interrupt=True)
            self._reset_round()
        else:
            self.state = "game_over"
            self.audio.speak(self._("fencer_gameover"), interrupt=True)
            self.audio.speak(self._("final_score", score=self.score), interrupt=False)
            self.finish()
