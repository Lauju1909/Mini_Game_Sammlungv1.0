import random
import pygame
import time
from games.base_game import BaseGame

class AudioSniper(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_sniper"
        self.instructions = self._("game_audio_sniper_instructions")
        
        self.score = 0
        self.state = "waiting_for_start"
        
        self.target_pos = 0.0 # From -1.0 (left) to 1.0 (right)
        self.aim_pos = 0.0 # From -1.0 to 1.0
        
        self.target_move_timer = 0.0
        self.breathe_timer = 0.0
        self.speed = 1.0
        self.lives = 3

    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_game(self):
        self.state = "playing"
        self.audio.speak(self._("start_go"), interrupt=True)
        self._spawn_target()

    def _spawn_target(self):
        self.target_pos = random.uniform(-0.8, 0.8)
        self.aim_pos = 0.0 # Reset aim to center
        self.target_move_timer = time.time() + max(1.0, 3.0 / self.speed)
        self.breathe_timer = time.time() + 0.5
        
    def update(self):
        if not self.active or self.state != "playing":
            return
            
        current_time = time.time()
        
        # Target moves if you take too long!
        if current_time >= self.target_move_timer:
            # Target escapes!
            self.lives -= 1
            self.audio.play_sound("error")
            
            if self.lives > 0:
                self.audio.speak(self._("sniper_target_escaped", lives=self.lives), interrupt=True)
                self._spawn_target()
            else:
                self.state = "game_over"
                self.audio.speak(self._("sniper_gameover"), interrupt=True)
                self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                self.finish()
            return
            
        # Play breathing sound every interval
        if current_time >= self.breathe_timer:
            # Calculate distance between aim and target
            distance = self.target_pos - self.aim_pos
            
            # Distance determines panning
            pan = max(-1.0, min(1.0, distance))
            
            # The closer you are, the louder the breathing
            abs_dist = abs(distance)
            vol = 1.0 - (abs_dist * 0.5)
            
            # Assuming we have a 'radar' or similar ping sound we can use
            self.audio.play_sound("radar", pan=pan, volume=vol)
            self.breathe_timer = current_time + max(0.4, 0.8 / self.speed)

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
                if event.key == pygame.K_LEFT:
                    self.aim_pos -= 0.1
                    self.aim_pos = max(-1.0, self.aim_pos)
                    self.audio.play_sound("menu_move", pan=self.aim_pos, volume=0.5)
                elif event.key == pygame.K_RIGHT:
                    self.aim_pos += 0.1
                    self.aim_pos = min(1.0, self.aim_pos)
                    self.audio.play_sound("menu_move", pan=self.aim_pos, volume=0.5)
                elif event.key == pygame.K_SPACE:
                    self._shoot()

    def _shoot(self):
        distance = abs(self.target_pos - self.aim_pos)
        
        if distance <= 0.15: # Hit window
            self.score += int(100 * self.speed)
            self.speed += 0.2
            self.audio.play_sound("explosion") # BANG!
            self.audio.play_sound("success")
            self._spawn_target()
        else:
            self.lives -= 1
            self.audio.play_sound("bump") # Miss
            self.audio.play_sound("error")
            
            if self.lives > 0:
                self.audio.speak(self._("sniper_missed", lives=self.lives), interrupt=True)
                self._spawn_target()
            else:
                self.state = "game_over"
                self.audio.speak(self._("sniper_gameover"), interrupt=True)
                self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                self.finish()
