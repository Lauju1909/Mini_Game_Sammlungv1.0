import pygame
import random
import time
import math
from games.base_game import BaseGame

class AudioMosquito(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_mosquito"
        self.instructions = self._("game_audio_mosquito_instructions")
        
        self.mosquitos_caught = 0
        self.target_mosquitos = 5
        
        self.mosquito_x = 0.0
        self.mosquito_z = 0.0
        self.angle = 0.0
        self.dist_angle = 0.0
        
        self.angle_speed = 0.0
        self.distance_speed = 0.0
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        self.last_tick = time.time()
        self.last_buzz = 0

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.start_mosquito()
        self.start_timer = time.time() + 2.0

    def start_mosquito(self):
        self.angle_speed = random.uniform(1.5, 3.5) + (self.mosquitos_caught * 0.5)
        self.distance_speed = random.uniform(1.0, 2.5) + (self.mosquitos_caught * 0.3)
        self.angle = random.uniform(0, math.pi * 2)
        self.dist_angle = random.uniform(0, math.pi * 2)

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
            return

        if self.state == "playing":
            # Mücke bewegen
            self.angle += self.angle_speed * dt
            self.dist_angle += self.distance_speed * dt
            
            # x = links/rechts (-1.0 bis 1.0)
            self.mosquito_x = math.sin(self.angle)
            
            # z = entfernung (0.0 = nah, 1.0 = fern)
            self.mosquito_z = (math.sin(self.dist_angle) + 1.0) / 2.0
            
            if now - self.last_buzz > 0.04:
                self.last_buzz = now
                
                pan = max(-1.0, min(1.0, self.mosquito_x))
                # Lautstärke: 100 wenn z=0, 10 wenn z=1
                vol = int(10 + (1.0 - self.mosquito_z) * 90)
                
                # Vibrato für das Summen
                vibrato = math.sin(now * 60) * 15
                freq = 700 + vibrato
                
                self.audio.play_tone(frequency=int(freq), duration_ms=60, volume=vol, pan=pan)

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "playing":
                if event.key == pygame.K_SPACE:
                    # Klatsch-Geräusch
                    self.audio.play_sound("bump")
                    
                    # Trefferzone: Mitte (x nah an 0) und sehr nah (z nah an 0)
                    if abs(self.mosquito_x) < 0.25 and self.mosquito_z < 0.25:
                        # Getroffen!
                        self.audio.play_sound("success")
                        self.mosquitos_caught += 1
                        
                        if self.mosquitos_caught >= self.target_mosquitos:
                            self.audio.speak(self._("mosquito_win"), priority=2)
                            time.sleep(2)
                            self.finish()
                        else:
                            self.audio.speak(str(self.mosquitos_caught), priority=1)
                            self.start_mosquito()
                            self.state = "starting"
                            self.start_timer = time.time() + 1.0
                    else:
                        # Verfehlt!
                        self.audio.play_sound("swipe")
                        # Höhnisches Summen
                        self.audio.play_tone(frequency=900, duration_ms=300, volume=100, pan=self.mosquito_x)

    def draw(self, screen):
        screen.fill((20, 20, 40))
        
        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Erwischt: {self.mosquitos_caught} / {self.target_mosquitos}", True, (255, 255, 255))
        screen.blit(score_surf, (20, 20))
        
        # Mücke visualisieren
        if self.state == "playing":
            center_x, center_y = 400, 300
            
            # x-achse
            screen_x = center_x + int(self.mosquito_x * 300)
            
            # z-achse (Größe)
            size = int(5 + (1.0 - self.mosquito_z) * 45)
            
            pygame.draw.circle(screen, (255, 0, 0), (screen_x, center_y), size)
            
            # Trefferzone in der Mitte
            pygame.draw.rect(screen, (0, 255, 0), (center_x - 75, center_y - 75, 150, 150), 2)
