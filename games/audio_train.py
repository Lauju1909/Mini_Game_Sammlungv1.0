import random
import pygame
import time
from games.base_game import BaseGame

class AudioTrain(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_train"
        self.instructions = self._("game_audio_train_instructions")
        
        self.score = 0
        self.lives = 3
        self.round = 1
        
        self.state = "waiting_for_start" # waiting_for_start, approaching, resolution
        self.train_type = "" # "fast" or "slow"
        self.current_track = "fast" # player's current switch state
        self.arrival_time = 0
        self.last_chug = 0

    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_round(self):
        self.audio.speak(self._("round_number", idx=self.round), interrupt=True)
        self.state = "approaching"
        
        # Decide train type
        self.train_type = random.choice(["fast", "slow"])
        
        # Reset track to middle or random? Let's say it always starts on "fast"
        # Or better: player must actively set it. We won't reset it, let player remember.
        
        duration = max(1.5, 4.0 - (self.round * 0.2))
        self.arrival_time = time.time() + duration
        self.last_chug = time.time()
        
        # Play the horn
        if self.train_type == "fast":
            self.audio.play_sound("blip") # High pitch substitute for whistle
        else:
            self.audio.play_sound("bump") # Low pitch substitute for horn

    def update(self):
        if not self.active:
            return
            
        current_time = time.time()
        
        if self.state == "approaching":
            # Play chug sound based on speed
            chug_interval = 0.2 if self.train_type == "fast" else 0.5
            if current_time - self.last_chug > chug_interval:
                self.last_chug = current_time
                # Slight panning effect just for atmosphere
                pan = random.uniform(-0.3, 0.3)
                self.audio.play_sound("hit", pan=pan)
                
            if current_time >= self.arrival_time:
                self._resolve_train()
                
        elif self.state == "resolution":
            if current_time - self.arrival_time > 1.5:
                if self.lives > 0:
                    self._start_round()
                else:
                    self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                    self.finish()

    def _resolve_train(self):
        self.state = "resolution"
        self.arrival_time = time.time()
        
        if self.current_track == self.train_type:
            # Success
            self.score += 10 * self.round
            self.round += 1
            self.audio.play_sound("confirm")
            self.audio.speak(self._("train_success"), interrupt=True)
        else:
            # Crash
            self.lives -= 1
            self.audio.play_sound("error")
            self.audio.speak(self._("train_crash", lives=self.lives), interrupt=True)

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_round()
            elif self.state == "approaching":
                if event.key == pygame.K_UP:
                    self.current_track = "fast"
                    self.audio.play_sound("blip") # Feedback for switch
                elif event.key == pygame.K_DOWN:
                    self.current_track = "slow"
                    self.audio.play_sound("bump") # Feedback for switch
