import pygame
import random
from games.base_game import BaseGame

class MysteryDoor(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "mystery_door"
        self.instructions = self._("game_mystery_door_instructions")
        
        self.door_sounds = ["creak1", "metalLatch", "cloth1"]
        self.doors = [0, 1, 2]
        random.shuffle(self.doors)
        self.target_idx = random.randint(0, 2)
        self.target_sound = self.door_sounds[self.doors[self.target_idx]]
        
        self.round = 1
        self.max_rounds = 5
        self.state = "listening"
        self.focused_door = 0
        self.last_action_time = 0

    def start(self):
        super().start()
        self.audio.speak(self._("find_the_door_with", sound=self._(f"sound_{self.target_sound}")))
        self.audio.speak(self._("game_mystery_door_instructions"))
        self.state = "playing"

    def update(self):
        pass

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if self.state == "playing":
                if event.key == pygame.K_LEFT:
                    if self.focused_door > 0:
                        self.focused_door -= 1
                        self.audio.speak(self._("door_number", idx=self.focused_door + 1))
                    else:
                        self.audio.play_sound("bump")
                elif event.key == pygame.K_RIGHT:
                    if self.focused_door < 2:
                        self.focused_door += 1
                        self.audio.speak(self._("door_number", idx=self.focused_door + 1))
                    else:
                        self.audio.play_sound("bump")
                elif event.key == pygame.K_SPACE: # Knock
                    # Panning based on door position
                    pan = (self.focused_door - 1) * 0.8
                    self.audio.play_panned_sound(self.door_sounds[self.doors[self.focused_door]], pan)
                elif event.key == pygame.K_RETURN: # Select
                    if self.focused_door == self.target_idx:
                        self.score += 20
                        self.audio.play_sound("success")
                    else:
                        self.audio.play_sound("error")
                    
                    self.round += 1
                    if self.round > self.max_rounds:
                        self.finish()
                    else:
                        self.next_round()
            elif event.key == pygame.K_r: # Repeat target sound
                self.audio.speak(self._("find_the_door_with", sound=self._(f"sound_{self.target_sound}")))

    def next_round(self):
        random.shuffle(self.doors)
        self.target_idx = random.randint(0, 2)
        self.target_sound = self.door_sounds[self.doors[self.target_idx]]
        self.focused_door = 1 # Start at middle door
        self.audio.speak(self._("find_the_door_with", sound=self._(f"sound_{self.target_sound}")))

    def draw(self, screen):
        screen.fill((10, 10, 20))
        font = pygame.font.SysFont("Outfit, Arial", 40)
        title = font.render(self._("game_mystery_door"), True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        # Draw 3 doors
        for i in range(3):
            x = 150 + i * 200
            y = 250
            w, h = 100, 200
            
            color = (100, 100, 100)
            if self.focused_door == i:
                color = (0, 255, 255)
            
            pygame.draw.rect(screen, color, (x, y, w, h), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), width=2, border_radius=10)
            
            # Door knob
            pygame.draw.circle(screen, (255, 215, 0), (x + 80, y + 100), 5)
            
            num = font.render(str(i+1), True, (255, 255, 255))
            screen.blit(num, (x + w//2 - num.get_width()//2, y + h + 10))
