import pygame
import random
import time
from games.base_game import BaseGame

class AudioWaiter(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_waiter"
        self.instructions = self._("game_audio_waiter_instructions")
        
        self.grid_size = 5
        self.player_x = 2
        self.player_y = 2
        
        self.score = 0
        self.lives = 3
        self.time_limit = 12.0
        
        self.obstacles = []
        self.target = None
        self.target_timer = 0
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        self.last_tick = time.time()
        self.last_call = 0
        
        self.generate_level()

    def generate_level(self):
        self.player_x = 2
        self.player_y = 2
        
        self.obstacles = []
        # 3 Hindernisse platzieren
        while len(self.obstacles) < 3:
            ox = random.randint(0, self.grid_size - 1)
            oy = random.randint(0, self.grid_size - 1)
            if (ox, oy) != (2, 2) and (ox, oy) not in self.obstacles:
                # Prüfen, ob es den Spieler nicht komplett einschließt (rudimentär)
                self.obstacles.append((ox, oy))
                
        self.spawn_target()

    def spawn_target(self):
        self.target = None
        while self.target is None:
            tx = random.randint(0, self.grid_size - 1)
            ty = random.randint(0, self.grid_size - 1)
            if (tx, ty) != (self.player_x, self.player_y) and (tx, ty) not in self.obstacles:
                self.target = (tx, ty)
                
        self.target_timer = time.time() + self.time_limit

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.start_timer = time.time() + 2.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.target_timer = now + self.time_limit
            return

        if self.state == "playing":
            if now > self.target_timer:
                # Zu spät!
                self.audio.play_sound("error")
                self.lives -= 1
                
                if self.lives <= 0:
                    self.audio.speak(self._("waiter_gameover"), priority=2)
                    time.sleep(2)
                    self.finish()
                else:
                    self.audio.speak(self._("waiter_too_late"), priority=1)
                    self.spawn_target()
                    
            elif now - self.last_call > 0.6:
                self.last_call = now
                
                if self.target:
                    dx = self.target[0] - self.player_x
                    dy = self.target[1] - self.player_y
                    
                    # Panning basierend auf x (Links/Rechts)
                    pan = dx / float(self.grid_size - 1) * 2.0
                    pan = max(-1.0, min(1.0, pan))
                    
                    # Lautstärke basierend auf Distanz
                    dist = abs(dx) + abs(dy)
                    vol = int(max(20, 100 - dist * 15))
                    
                    # Tonhöhe basierend auf y (Vorne/Hinten)
                    # dy < 0 bedeutet Vorne (höherer Ton)
                    freq = 600 - (dy * 60)
                    
                    # Gläser-Klirren simulieren (zwei schnelle helle Töne)
                    self.audio.play_tone(frequency=int(freq), duration_ms=80, volume=vol, pan=pan)
                    time.sleep(0.1)
                    self.audio.play_tone(frequency=int(freq+150), duration_ms=100, volume=vol, pan=pan)

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
                new_x, new_y = self.player_x, self.player_y
                moved = False
                
                if event.key == pygame.K_UP:
                    new_y -= 1
                    moved = True
                elif event.key == pygame.K_DOWN:
                    new_y += 1
                    moved = True
                elif event.key == pygame.K_LEFT:
                    new_x -= 1
                    moved = True
                elif event.key == pygame.K_RIGHT:
                    new_x += 1
                    moved = True
                
                if moved:
                    # Grenzen prüfen
                    if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
                        # Hindernis prüfen
                        if (new_x, new_y) in self.obstacles:
                            self.audio.play_sound("bump")
                        else:
                            self.player_x, self.player_y = new_x, new_y
                            # Kurzer Schritt-Sound
                            self.audio.play_tone(frequency=200, duration_ms=30, volume=30)
                            
                            # Wenn wir das Ziel erreicht haben, sofort das Klirren zentriert abspielen
                            if self.target and self.player_x == self.target[0] and self.player_y == self.target[1]:
                                self.audio.play_tone(frequency=800, duration_ms=50, volume=100, pan=0.0)
                    else:
                        # Wand
                        self.audio.play_sound("bump")
                        
                elif event.key == pygame.K_SPACE:
                    if self.target and self.player_x == self.target[0] and self.player_y == self.target[1]:
                        # Bedienung erfolgreich
                        self.audio.play_sound("success")
                        self.score += 10
                        self.time_limit = max(4.0, self.time_limit - 0.5)
                        self.spawn_target()
                    else:
                        # Falscher Tisch
                        self.audio.play_sound("error")

    def draw(self, screen):
        screen.fill((40, 20, 20))
        
        # Grid zeichnen
        cell_size = 80
        offset_x = 200
        offset_y = 100
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)
                
                color = (60, 30, 30)
                if (x, y) in self.obstacles:
                    color = (100, 50, 0) # Hindernis
                elif self.target and (x, y) == self.target:
                    color = (255, 255, 100) # Ziel
                    
                if x == self.player_x and y == self.player_y:
                    color = (0, 255, 0) # Spieler
                    
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (100, 100, 100), rect, 2)
                
        font = pygame.font.SysFont("Arial", 28)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        
        # Timer Balken
        if self.state == "playing" and self.target:
            time_left = max(0, self.target_timer - time.time())
            ratio = time_left / self.time_limit
            pygame.draw.rect(screen, (255, 0, 0), (20, 550, int(760 * ratio), 20))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
