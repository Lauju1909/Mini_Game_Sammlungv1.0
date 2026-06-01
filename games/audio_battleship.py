import pygame
import random
import time
from games.base_game import BaseGame

class AudioBattleship(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_battleship"
        self.instructions = self._("game_audio_battleship_instructions")
        
        self.grid_size = 5
        self.cursor_x = 0
        self.cursor_y = 0
        self.shots_taken = 0
        self.ships = []
        self.board = [["empty" for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        
        self.generate_ships()

    def generate_ships(self):
        # Platziere 3 Schiffe (1x Größe 3, 2x Größe 2)
        ship_lengths = [3, 2, 2]
        
        for length in ship_lengths:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                attempts += 1
                vertical = random.choice([True, False])
                if vertical:
                    sx = random.randint(0, self.grid_size - 1)
                    sy = random.randint(0, self.grid_size - length)
                    parts = [(sx, sy + i) for i in range(length)]
                else:
                    sx = random.randint(0, self.grid_size - length)
                    sy = random.randint(0, self.grid_size - 1)
                    parts = [(sx + i, sy) for i in range(length)]
                
                # Check collision
                collision = any(p in self.ships for p in parts)
                if not collision:
                    self.ships.extend(parts)
                    placed = True

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.start_timer = time.time() + 2.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        if self.state == "starting":
            if time.time() > self.start_timer:
                self.state = "playing"

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
                # Bewegung
                moved = False
                if event.key == pygame.K_UP:
                    if self.cursor_y > 0:
                        self.cursor_y -= 1
                        moved = True
                elif event.key == pygame.K_DOWN:
                    if self.cursor_y < self.grid_size - 1:
                        self.cursor_y += 1
                        moved = True
                elif event.key == pygame.K_LEFT:
                    if self.cursor_x > 0:
                        self.cursor_x -= 1
                        moved = True
                elif event.key == pygame.K_RIGHT:
                    if self.cursor_x < self.grid_size - 1:
                        self.cursor_x += 1
                        moved = True
                        
                if moved:
                    # Panning basierend auf x Position (0 bis 4 -> -1.0 bis 1.0)
                    pan = (self.cursor_x / (self.grid_size - 1)) * 2.0 - 1.0
                    # Tonhöhe basierend auf y Position (0 bis 4 -> hell bis dunkel)
                    freq = 600 - (self.cursor_y * 50)
                    self.audio.play_tone(frequency=freq, duration_ms=40, volume=30, pan=pan)
                    
                # Sonar
                elif event.key == pygame.K_s:
                    if self.ships:
                        dist = min(abs(px - self.cursor_x) + abs(py - self.cursor_y) for (px, py) in self.ships)
                        # Je näher, desto höher der Ton
                        freq = 300 + (max(0, 8 - dist) * 100)
                        self.audio.play_tone(frequency=int(freq), duration_ms=150, volume=60)
                        self.audio.speak(str(dist), priority=1)
                
                # Schießen
                elif event.key == pygame.K_SPACE:
                    state = self.board[self.cursor_y][self.cursor_x]
                    
                    if state != "empty":
                        # Schon hier geschossen
                        self.audio.play_sound("error")
                        return
                        
                    self.shots_taken += 1
                    target = (self.cursor_x, self.cursor_y)
                    
                    if target in self.ships:
                        # Treffer (Explosion)
                        self.audio.play_sound("bump")
                        self.audio.play_tone(frequency=100, duration_ms=400, volume=100)
                        self.audio.speak(self._("battleship_hit"), priority=1)
                        
                        self.ships.remove(target)
                        self.board[self.cursor_y][self.cursor_x] = "hit"
                        
                        if not self.ships:
                            # Gewonnen!
                            self.audio.speak(self._("battleship_win", shots=self.shots_taken), priority=2)
                            time.sleep(2)
                            self.finish()
                    else:
                        # Wasser (Platsch)
                        self.audio.play_sound("swipe")
                        self.audio.play_tone(frequency=800, duration_ms=80, volume=40)
                        self.audio.speak(self._("battleship_miss"), priority=1)
                        self.board[self.cursor_y][self.cursor_x] = "miss"

    def draw(self, screen):
        screen.fill((10, 20, 50))
        
        # Grid zeichnen
        cell_size = 80
        offset_x = 200
        offset_y = 100
        
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = (offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)
                
                state = self.board[y][x]
                color = (30, 40, 80)
                
                if state == "miss":
                    color = (100, 150, 255)
                elif state == "hit":
                    color = (255, 50, 50)
                    
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (200, 200, 200), rect, 2)
                
        # Cursor
        cursor_rect = (offset_x + self.cursor_x * cell_size, offset_y + self.cursor_y * cell_size, cell_size, cell_size)
        pygame.draw.rect(screen, (0, 255, 0), cursor_rect, 4)
        
        font = pygame.font.SysFont("Arial", 28)
        shots_surf = font.render(f"Schüsse: {self.shots_taken}", True, (255, 255, 255))
        ships_surf = font.render(f"Übrige Schiffsteile: {len(self.ships)}", True, (255, 100, 100))
        
        screen.blit(shots_surf, (20, 20))
        screen.blit(ships_surf, (20, 60))
