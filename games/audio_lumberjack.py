import pygame
import time
import random
from games.base_game import BaseGame

class AudioLumberjack(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_lumberjack"
        self.instructions = self._("game_audio_lumberjack_instructions")
        
        self.score = 0
        self.state = "waiting_for_start"
        self.lives = 3
        self.round_num = 1
        
        self.tree_state = "chopping" # chopping, falling
        self.chops_needed = 0
        self.chops_done = 0
        self.fall_direction = 0 # -1 left, 1 right
        self.fall_time = 0.0
        self.action_delay = 0.0
        
    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_game(self):
        self.state = "playing"
        self.score = 0
        self.lives = 3
        self.round_num = 1
        self._reset_tree()

    def _reset_tree(self):
        self.tree_state = "chopping"
        self.chops_needed = random.randint(3, 8)
        self.chops_done = 0
        self.audio.speak(self._("lumberjack_tree_ready"), interrupt=True)

    def update(self):
        if not self.active or self.state != "playing":
            return
            
        current_time = time.time()
        
        if self.tree_state == "falling":
            if current_time >= self.fall_time:
                # Tree fell on the player!
                self.lives -= 1
                self.audio.play_sound("error")
                if self.lives > 0:
                    self.audio.speak(self._("lumberjack_crushed", lives=self.lives), interrupt=True)
                    self._reset_tree()
                else:
                    self.state = "game_over"
                    self.audio.speak(self._("lumberjack_gameover"), interrupt=True)
                    self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                    self.finish()

    def handle_input(self, event):
        if not self.active:
            return

        # Explicitly call super() to ensure ESC handles boundary/menu events if needed
        super().handle_input(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_game()
                    
            elif self.state == "playing":
                if self.tree_state == "chopping":
                    if event.key == pygame.K_SPACE:
                        self._chop()
                elif self.tree_state == "falling":
                    if event.key == pygame.K_LEFT:
                        self._dodge(-1)
                    elif event.key == pygame.K_RIGHT:
                        self._dodge(1)

    def _chop(self):
        # Play a chop sound
        self.audio.play_sound("tick_001")
        self.chops_done += 1
        if self.chops_done >= self.chops_needed:
            # Tree starts falling
            self.tree_state = "falling"
            self.fall_direction = random.choice([-1, 1])
            # Play a long creaking sound panned to the direction it falls
            self.audio.play_panned_sound("scratch_004", pan=self.fall_direction)
            self.action_delay = max(0.6, 2.0 - (self.round_num * 0.15))
            self.fall_time = time.time() + self.action_delay

    def _dodge(self, direction):
        if self.tree_state == "falling":
            # You must dodge away from the tree. If it falls right (1), you dodge left (-1).
            if direction != self.fall_direction:
                # Success
                self.audio.play_sound("success")
                self.score += 100 * self.round_num
                self.round_num += 1
                self._reset_tree()
            else:
                # Dodged into the tree
                self.fall_time = 0 # Force immediate crush
