import random
import pygame
import time
from games.base_game import BaseGame

class AudioFishing(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_fishing"
        self.instructions = self._("game_audio_fishing_instructions")
        
        self.round = 1
        self.max_rounds = 5
        self.score = 0
        
        self.state = "waiting_for_start" # waiting_for_start, casting, waiting_for_bite, biting
        self.fish_timer = 0
        self.bite_time = 0
        self.bite_duration = 0
        self.last_splash = 0

    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_round(self):
        self.audio.speak(self._("round_number", round=self.round), interrupt=True)
        self.state = "casting"
        self.audio.speak(self._("press_space_to_cast"), interrupt=False)

    def _cast_line(self):
        self.audio.play_sound("confirm") # Simulate casting sound
        self.state = "waiting_for_bite"
        # Fish will bite randomly between 2 to 6 seconds
        self.fish_timer = time.time() + random.uniform(2.0, 6.0)

    def _trigger_bite(self):
        self.state = "biting"
        self.bite_time = time.time()
        # The player has a small window to react (0.5 to 1.2 seconds depending on round)
        self.bite_duration = max(0.5, 1.2 - (self.round * 0.1))
        self.audio.play_sound("blip") # The bite sound!

    def update(self):
        if not self.active:
            return
            
        current_time = time.time()
        
        if self.state == "waiting_for_bite":
            # Ambient water sounds
            if current_time - self.last_splash > random.uniform(1.0, 2.5):
                self.last_splash = current_time
                self.audio.play_sound("bump") # Ambient substitute
                
            if current_time >= self.fish_timer:
                self._trigger_bite()
                
        elif self.state == "biting":
            # Rapid beeping to indicate struggle
            if current_time - self.last_splash > 0.15:
                self.last_splash = current_time
                self.audio.play_sound("blip")
                
            if current_time - self.bite_time > self.bite_duration:
                # Fish escaped
                self.audio.play_sound("error")
                self.audio.speak(self._("fish_escaped"), interrupt=True)
                self._end_round(False)

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
            elif self.state == "casting":
                if event.key == pygame.K_SPACE:
                    self._cast_line()
            elif self.state == "waiting_for_bite":
                if event.key == pygame.K_SPACE:
                    # Pulled too early!
                    self.audio.play_sound("error")
                    self.audio.speak(self._("too_early"), interrupt=True)
                    self._end_round(False)
            elif self.state == "biting":
                if event.key == pygame.K_SPACE:
                    # Caught the fish!
                    reaction_time = time.time() - self.bite_time
                    points = int(max(10, 1000 - (reaction_time * 1000)))
                    self.score += points
                    self.audio.play_sound("confirm")
                    self.audio.speak(self._("fish_caught", points=points), interrupt=True)
                    self._end_round(True)

    def _end_round(self, success):
        self.round += 1
        self.state = "waiting_for_start"
        if self.round > self.max_rounds:
            self.audio.speak(self._("final_score", score=self.score), interrupt=False)
            self.finish()
        else:
            self.audio.speak(self._("press_enter_to_continue"), interrupt=False)
