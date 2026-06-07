import pygame
import random
import time
from games.base_game import BaseGame

class AudioArchery(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_archery"
        self.instructions = self._("game_audio_archery_instructions")
        
        self.score = 0
        self.lives = 3
        self.round = 1
        
        # Target state
        self.target_distance = 0.0 # 0.3 to 1.0
        self.target_pan = -1.0
        self.target_dir = 1
        self.target_speed = 0.02
        
        # Bow state
        self.is_drawing = False
        self.tension = 0.0
        
        self.state = "waiting_start" # waiting_start, playing, result, game_over
        self.last_target_sound = 0
        self.last_bow_sound = 0
        
        self._next_round()
        
    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)
        self.state = "waiting_start"

    def _next_round(self):
        self.target_distance = random.uniform(0.3, 1.0)
        self.target_pan = random.choice([-1.0, 1.0])
        self.target_dir = 1 if self.target_pan < 0 else -1
        self.target_speed = random.uniform(0.01, 0.025)
        
        self.is_drawing = False
        self.tension = 0.0
        self.state = "playing"
        self.round += 1
        
    def handle_input(self, event):
        super().handle_input(event)
        if not self.active or self.is_tutorial:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_start" and event.key == pygame.K_RETURN:
                self.state = "playing"
                
            elif self.state == "playing" and event.key == pygame.K_SPACE:
                if not self.is_drawing:
                    self.is_drawing = True
                    self.tension = 0.0
                    
        elif event.type == pygame.KEYUP:
            if self.state == "playing" and event.key == pygame.K_SPACE and self.is_drawing:
                self._shoot()
                
        elif event.type == pygame.USEREVENT + 1 and self.state == "result":
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            self._next_round()
            
        elif event.type == pygame.USEREVENT + 2 and self.state == "game_over":
            pygame.time.set_timer(pygame.USEREVENT + 2, 0)
            self.finish()
                
    def _shoot(self):
        self.is_drawing = False
        
        # Check pan error and tension error
        pan_err = abs(self.target_pan)
        tension_err = abs(self.tension - self.target_distance)
        
        # Perfect shot: pan within 0.15, tension within 0.15
        if pan_err < 0.2 and tension_err < 0.2:
            self.audio.play_sound("success")
            # Thwack sound
            self.audio.play_tone(150, duration_ms=100, volume=100)
            
            pts = int(100 * (1.0 - (pan_err + tension_err)))
            self.score += pts
            self.audio.speak(self._("hit_perfect"), interrupt=True)
            self.state = "result"
            pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
        else:
            self.lives -= 1
            self.audio.play_sound("error")
            self.audio.speak(self._("miss"), interrupt=True)
            
            if self.lives <= 0:
                self.state = "game_over"
                self.audio.speak(self._("game_over"), interrupt=False)
                self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                pygame.time.set_timer(pygame.USEREVENT + 2, 3000)
            else:
                self.state = "result"
                pygame.time.set_timer(pygame.USEREVENT + 1, 1500)
                
    def update(self):
        if not self.active or self.is_tutorial:
            return
            
        current_time = time.time()
        
        if self.state == "playing":
            # Move target
            self.target_pan += self.target_dir * self.target_speed
            if self.target_pan > 1.0 or self.target_pan < -1.0:
                self.target_dir *= -1
                
            # Play target sound
            if current_time - self.last_target_sound > 0.3:
                # Frequency mapped to distance. 0.3 = near (high freq), 1.0 = far (low freq)
                freq = 800 - ((self.target_distance - 0.3) / 0.7) * 500
                self.audio.play_tone(int(freq), duration_ms=100, volume=20, pan=self.target_pan)
                self.last_target_sound = current_time
                
            # Bow tension
            if self.is_drawing:
                # Tension increases over ~2 seconds
                self.tension += 0.015
                if self.tension > 1.0:
                    self.tension = 1.0 # max draw
                    
                if current_time - self.last_bow_sound > 0.05:
                    # Creaking sound -> rising tone
                    bow_freq = 200 + self.tension * 400
                    self.audio.play_tone(int(bow_freq), duration_ms=40, volume=40, pan=0.0)
                    self.last_bow_sound = current_time

    def draw(self, screen):
        screen.fill((20, 20, 20))
        font = pygame.font.SysFont("Arial", 40, bold=True)
        title = font.render("AUDIO-BOGENSCHIESSEN", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        info_font = pygame.font.SysFont("Arial", 24)
        info = info_font.render(f"Punkte: {self.score} | Leben: {self.lives}", True, (200, 200, 200))
        screen.blit(info, (400 - info.get_width()//2, 100))
        
        # Visual cues for sighted players
        if self.state == "playing":
            # Target
            tx = 400 + self.target_pan * 300
            ty = 300 - (1.0 - self.target_distance) * 150
            pygame.draw.circle(screen, (255, 0, 0), (int(tx), int(ty)), 15)
            
            # Bow tension bar
            bar_width = 300
            bar_height = 20
            bx = 400 - bar_width // 2
            by = 500
            pygame.draw.rect(screen, (50, 50, 50), (bx, by, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (bx, by, int(bar_width * self.tension), bar_height))
