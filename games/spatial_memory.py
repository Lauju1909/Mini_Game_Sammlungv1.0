import pygame
import random
import time
from games.base_game import BaseGame

class SpatialMemory(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "spatial_memory"
        self.instructions = self._("game_spatial_memory_instructions")
        
        self.sequence = []
        self.player_index = 0
        self.lives = 3
        self.score = 0
        
        self.state = "starting"
        self.start_timer = time.monotonic() + 2.0
        
        self.playback_timer = 0
        self.playback_index = 0
        self.playback_interval = 0.8
        
        self.directions = ["UP", "DOWN", "LEFT", "RIGHT"]

    def start(self):
        super().start()
        self.start_timer = time.monotonic() + 3.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.monotonic()

        if self.state == "starting":
            if now > self.start_timer:
                self.audio.speak(self._("start_go"), priority=2)
                self.add_to_sequence()
            return

        if self.state == "playback":
            if now > self.playback_timer:
                if self.playback_index < len(self.sequence):
                    self.play_direction(self.sequence[self.playback_index])
                    self.playback_index += 1
                    self.playback_timer = now + self.playback_interval
                else:
                    self.state = "waiting"
                    # Kleiner Hinweiston, dass der Spieler dran ist
                    self.audio.play_sound("click_001")

    def add_to_sequence(self):
        self.sequence.append(random.choice(self.directions))
        self.playback_index = 0
        self.player_index = 0
        self.state = "playback"
        self.playback_timer = time.monotonic() + 1.0 # 1 Sekunde Pause vor dem Vorspielen
        
        # Geschwindigkeit wird leicht erhöht bei längeren Sequenzen
        self.playback_interval = max(0.3, 0.8 - (len(self.sequence) * 0.02))

    def play_direction(self, direction):
        if direction == "UP":
            self.audio.play_tone(frequency=800, duration_ms=200, volume=80, pan=0.0)
        elif direction == "DOWN":
            self.audio.play_tone(frequency=300, duration_ms=200, volume=80, pan=0.0)
        elif direction == "LEFT":
            self.audio.play_tone(frequency=500, duration_ms=200, volume=80, pan=-1.0)
        elif direction == "RIGHT":
            self.audio.play_tone(frequency=500, duration_ms=200, volume=80, pan=1.0)

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "waiting":
                pressed_dir = None
                if event.key == pygame.K_UP:
                    pressed_dir = "UP"
                elif event.key == pygame.K_DOWN:
                    pressed_dir = "DOWN"
                elif event.key == pygame.K_LEFT:
                    pressed_dir = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    pressed_dir = "RIGHT"
                
                if pressed_dir:
                    self.play_direction(pressed_dir)
                    
                    if pressed_dir == self.sequence[self.player_index]:
                        # Richtig
                        self.player_index += 1
                        self.score += 10
                        if self.player_index == len(self.sequence):
                            # Sequenz komplett
                            self.score += 100
                            self.audio.play_sound("success")
                            self.state = "success_pause"
                            self.playback_timer = time.monotonic() + 1.0
                    else:
                        # Falsch
                        self.lives -= 1
                        self.audio.play_sound("error")
                        self.audio.speak(self._("spatial_error", lives=self.lives), priority=2)
                        
                        if self.lives <= 0:
                            self.finish()
                        else:
                            # Sequenz nochmal abspielen
                            self.state = "success_pause" # Missbrauche diesen State als Pause
                            self.playback_timer = time.monotonic() + 1.5

        if self.state == "success_pause" and time.monotonic() > self.playback_timer:
            if self.player_index == len(self.sequence):
                self.add_to_sequence()
            else:
                # Falsch geraten, spiele alte Sequenz nochmal
                self.playback_index = 0
                self.player_index = 0
                self.state = "playback"
                self.playback_timer = time.monotonic() + 0.5

    def draw(self, screen):
        screen.fill((10, 10, 20))
        
        font_large = pygame.font.SysFont("Arial", 48, bold=True)
        font_small = pygame.font.SysFont("Arial", 24)
        
        center_x, center_y = 400, 300
        
        # Pfeile zeichnen (vereinfacht als Kreise)
        colors = {
            "UP": (0, 255, 0),
            "DOWN": (255, 0, 0),
            "LEFT": (255, 255, 0),
            "RIGHT": (0, 0, 255)
        }
        
        pygame.draw.circle(screen, colors["UP"], (center_x, center_y - 100), 30)
        pygame.draw.circle(screen, colors["DOWN"], (center_x, center_y + 100), 30)
        pygame.draw.circle(screen, colors["LEFT"], (center_x - 100, center_y), 30)
        pygame.draw.circle(screen, colors["RIGHT"], (center_x + 100, center_y), 30)
        
        # UI
        status = "MERKEN!" if self.state == "playback" else ("NACHSPIELEN!" if self.state == "waiting" else "")
        status_surf = font_large.render(status, True, (255, 255, 255))
        screen.blit(status_surf, (400 - status_surf.get_width()//2, 100))
        
        seq_len_surf = font_small.render(f"Länge: {len(self.sequence)}", True, (200, 200, 200))
        screen.blit(seq_len_surf, (400 - seq_len_surf.get_width()//2, 450))
        
        lives_surf = font_small.render(f"Leben: {self.lives}", True, (255, 100, 100))
        score_surf = font_small.render(f"Punkte: {self.score}", True, (255, 255, 255))
        screen.blit(lives_surf, (20, 20))
        screen.blit(score_surf, (650, 20))
