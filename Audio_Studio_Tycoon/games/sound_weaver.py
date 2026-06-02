import pygame
import random
from games.base_game import BaseGame

class SoundWeaver(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "sound_weaver"
        self.instructions = self._("game_sound_weaver_instructions")
        
        self.melody = [0, 1, 2, 3]
        random.shuffle(self.melody)
        self.current_order = list(range(4))
        random.shuffle(self.current_order)
        
        self.selected_idx = 0
        self.state = "playing_melody"
        self.last_action_time = 0
        self.preview_idx = 0

    def start(self):
        super().start()
        self.audio.speak(self._("restore_the_melody"))
        self.last_action_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "playing_melody":
            if now - self.last_action_time > 1000:
                # self.audio.play_sound(f"note_{self.melody[self.preview_idx]}")
                self.preview_idx += 1
                if self.preview_idx >= 4:
                    self.state = "arranging"
                    self.preview_idx = 0
                self.last_action_time = now

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if self.state == "arranging":
                if event.key == pygame.K_LEFT:
                    if self.selected_idx > 0:
                        self.current_order[self.selected_idx], self.current_order[self.selected_idx-1] = \
                            self.current_order[self.selected_idx-1], self.current_order[self.selected_idx]
                        self.selected_idx -= 1
                        self.audio.play_sound("click")
                elif event.key == pygame.K_RIGHT:
                    if self.selected_idx < 3:
                        self.current_order[self.selected_idx], self.current_order[self.selected_idx+1] = \
                            self.current_order[self.selected_idx+1], self.current_order[self.selected_idx]
                        self.selected_idx += 1
                        self.audio.play_sound("click")
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    self.selected_idx = event.key - pygame.K_1
                    # self.audio.play_sound(f"note_{self.current_order[self.selected_idx]}")
                elif event.key == pygame.K_RETURN:
                    if self.current_order == self.melody:
                        self.score += 100
                        self.audio.play_sound("success")
                        self.finish()
                    else:
                        self.audio.play_sound("error")
                elif event.key == pygame.K_r: # Replay melody
                    self.state = "playing_melody"
                    self.preview_idx = 0
                    self.last_action_time = now

    def draw(self, screen):
        screen.fill((50, 30, 50))
        font = pygame.font.SysFont("Outfit, Arial", 40)
        title = font.render(self._("game_sound_weaver"), True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        # Draw sound blocks
        for i in range(4):
            x = 100 + i * 160
            y = 250
            w, h = 140, 140
            
            color = (150, 100, 200)
            if self.state == "arranging" and self.selected_idx == i:
                color = (0, 255, 255)
            elif self.state == "playing_melody" and self.preview_idx - 1 == i:
                color = (255, 255, 255)
                
            pygame.draw.rect(screen, color, (x, y, w, h), border_radius=20)
            pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), width=3, border_radius=20)
            
            num = font.render(str(self.current_order[i] + 1), True, (255, 255, 255))
            screen.blit(num, (x + w//2 - num.get_width()//2, y + h//2 - num.get_height()//2))
