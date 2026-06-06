import pygame
import random
import math
from games.base_game import BaseGame

class TickingClock(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "ticking_clock"
        self.instructions = self._("game_ticking_clock_instructions")
        self.correct_clock = random.randint(0, 2)
        self.clock_speeds = [1.0, 1.0, 1.0]
        self.clock_speeds[self.correct_clock] = random.choice([0.7, 1.5])
        self.round = 1
        self.max_rounds = 3
        
        self.state = "announcing_clock"
        self.current_clock_idx = 0
        self.tick_count = 0
        self.max_ticks = 4
        self.last_action_time = 0
        self.interval = 500 # ms for announcing
        self.tick_timer = 0
        self.options_announced = False

    def start(self):
        super().start()
        self.last_action_time = pygame.time.get_ticks()
        self.state = "announcing_clock"
        self.current_clock_idx = 0
        self.audio.speak(self._("clock_number", idx=1))

    def update(self):
        now = pygame.time.get_ticks()
        
        if self.state == "announcing_clock":
            if now - self.last_action_time > 800:
                self.state = "ticking"
                self.tick_count = 0
                self.tick_timer = now
                self.last_action_time = now
        
        elif self.state == "ticking":
            tick_interval = 500 / self.clock_speeds[self.current_clock_idx]
            if now - self.tick_timer > tick_interval:
                self.audio.play_sound("tick_001")
                self.tick_count += 1
                self.tick_timer = now
                
                if self.tick_count >= self.max_ticks:
                    if self.current_clock_idx < 2:
                        self.current_clock_idx += 1
                        self.state = "announcing_clock"
                        self.audio.speak(self._("clock_number", idx=self.current_clock_idx + 1))
                        self.last_action_time = now
                    else:
                        self.state = "waiting_input"
                        if not self.options_announced:
                            self.audio.speak(self._("select_different_clock"))
                            self.options_announced = True

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if self.state == "waiting_input":
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3]:
                    if event.key in [pygame.K_1, pygame.K_KP1]:
                        idx = 0
                    elif event.key in [pygame.K_2, pygame.K_KP2]:
                        idx = 1
                    else:
                        idx = 2
                    if idx == self.correct_clock:
                        self.score += 33
                        self.audio.play_sound("success")
                    else:
                        self.audio.play_sound("error")
                    
                    self.round += 1
                    if self.round > self.max_rounds:
                        self.finish()
                    else:
                        self.reset_round()
            elif event.key == pygame.K_r: # Repeat
                if self.state == "waiting_input":
                    self.reset_round(next_round=False)

    def reset_round(self, next_round=True):
        if next_round:
            self.correct_clock = random.randint(0, 2)
            self.clock_speeds = [1.0, 1.0, 1.0]
            self.clock_speeds[self.correct_clock] = random.choice([0.7, 1.5])
        
        self.current_clock_idx = 0
        self.state = "announcing_clock"
        self.last_action_time = pygame.time.get_ticks()
        self.options_announced = False
        self.audio.speak(self._("clock_number", idx=1))

    def draw(self, screen):
        # Premium Visuals
        screen.fill((20, 20, 40))
        font = pygame.font.SysFont("Outfit, Arial", 50)
        title = font.render(self._("game_ticking_clock"), True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        # Round info
        round_text = font.render(f"{self._('round_number', idx=self.round)} / {self.max_rounds}", True, (150, 150, 150))
        screen.blit(round_text, (400 - round_text.get_width()//2, 120))

        # Clocks visualization
        for i in range(3):
            color = (100, 100, 100)
            if self.state != "waiting_input" and i == self.current_clock_idx:
                color = (0, 255, 255) if self.state == "ticking" else (255, 255, 255)
            elif self.state == "waiting_input":
                color = (255, 215, 0)
                
            x = 200 + i * 200
            y = 350
            
            # Glass Circle
            pygame.draw.circle(screen, (*color, 30), (x, y), 80)
            pygame.draw.circle(screen, color, (x, y), 80, width=3)
            
            # Clock Hands (static for now, maybe animate?)
            angle = 0
            if self.state == "ticking" and i == self.current_clock_idx:
                angle = (pygame.time.get_ticks() * 0.01 * self.clock_speeds[i])
            
            end_x = x + math.cos(angle) * 60
            end_y = y + math.sin(angle) * 60
            pygame.draw.line(screen, color, (x, y), (end_x, end_y), 4)
            
            num_surf = font.render(str(i+1), True, color)
            screen.blit(num_surf, (x - num_surf.get_width()//2, y + 90))

