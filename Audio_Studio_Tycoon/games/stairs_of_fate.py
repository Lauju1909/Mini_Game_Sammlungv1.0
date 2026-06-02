import pygame
import random
from games.base_game import BaseGame

class StairsOfFate(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "stairs_of_fate"
        self.instructions = self._("game_stairs_of_fate_instructions")
        
        self.round = 1
        self.max_rounds = 10
        self.current_step_is_creaky = random.choice([True, False])
        self.state = "waiting_step"
        self.last_action_time = 0
        self.bg_loop = None

    def start(self):
        super().start()
        self.audio.speak(self._("climb_the_stairs"), priority=2)
        self.bg_loop = self.audio.play_looping_sound("music_back")
        if self.bg_loop:
            self.audio.set_channel_volume(self.bg_loop, 0.1)
        self.next_step()

    def next_step(self):
        self.current_step_is_creaky = random.choice([True, False])
        # Wir spielen den Sound des nächsten Schrittes an, damit der Spieler entscheiden kann
        if self.current_step_is_creaky:
            self.audio.play_sound("creak1")
        else:
            self.audio.play_sound("footstep01")
        self.state = "waiting_step"
        self.last_action_time = pygame.time.get_ticks()

    def finish(self):
        if self.bg_loop:
            self.audio.stop_sound(self.bg_loop)
        super().finish()

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if self.state == "waiting_step":
                if event.key == pygame.K_UP: # Walk
                    if self.current_step_is_creaky:
                        self.audio.play_sound("error")
                        self.finish()
                    else:
                        self.score += 10
                        self.audio.play_sound("success")
                        self.round += 1
                        if self.round > self.max_rounds:
                            self.finish()
                        else:
                            self.next_step()
                elif event.key == pygame.K_SPACE: # Jump
                    if self.current_step_is_creaky:
                        self.score += 15
                        self.audio.play_sound("success")
                        self.round += 1
                        if self.round > self.max_rounds:
                            self.finish()
                        else:
                            self.next_step()
                    else:
                        self.audio.play_sound("error")
                        self.finish()

    def draw(self, screen):
        screen.fill((40, 30, 20))
        font = pygame.font.SysFont("Outfit, Arial", 40)
        title = font.render(self._("game_stairs_of_fate"), True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        # Draw Stairs
        for i in range(12):
            x = 100 + i * 50
            y = 500 - i * 40
            color = (150, 100, 50)
            if i == self.round - 1:
                color = (255, 255, 0) if self.current_step_is_creaky else (0, 255, 0)
            
            pygame.draw.rect(screen, color, (x, y, 100, 20))
            pygame.draw.rect(screen, (0, 0, 0), (x, y, 100, 20), width=1)
            
        # Character
        char_x = 100 + (self.round - 1) * 50 + 40
        char_y = 500 - (self.round - 1) * 40 - 50
        pygame.draw.circle(screen, (255, 255, 255), (char_x, char_y), 20)
