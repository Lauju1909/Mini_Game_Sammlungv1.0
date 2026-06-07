import pygame
import random
import time
from games.base_game import BaseGame

class AudioMaze(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_maze"
        self.instructions = self._("game_audio_maze_instructions")
        
        self.width = 15
        self.height = 15
        self.maze = []
        self.px, self.py = 1, 1
        self.gx, self.gy = self.width - 2, self.height - 2
        
        self.last_wind_time = 0.0
        self.wind_interval = 0.3 # 300 ms
        self._generate_maze()
        
    def _generate_maze(self):
        # 1 = Wall, 0 = Path, 2 = Goal
        self.maze = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # Carve path using iterative DFS
        stack = [(1, 1)]
        self.maze[1][1] = 0
        
        while stack:
            cx, cy = stack[-1]
            # Find valid unvisited neighbors
            neighbors = []
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if self.maze[ny][nx] == 1:
                        neighbors.append((nx, ny, dx, dy))
                        
            if neighbors:
                nx, ny, dx, dy = neighbors[0]
                self.maze[cy + dy//2][cx + dx//2] = 0
                self.maze[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
                
        self.gx = self.width - 2
        self.gy = self.height - 2
        self.maze[self.gy][self.gx] = 2

    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def handle_input(self, event):
        super().handle_input(event)
        if not self.active or self.is_tutorial:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            nx, ny = self.px, self.py
            if event.key == pygame.K_UP:
                ny -= 1
            elif event.key == pygame.K_DOWN:
                ny += 1
            elif event.key == pygame.K_LEFT:
                nx -= 1
            elif event.key == pygame.K_RIGHT:
                nx += 1
                
            if (nx != self.px or ny != self.py):
                # Boundary check
                if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                    self.audio.play_sound("bump")
                    self.score = max(0, self.score - 5)
                elif self.maze[ny][nx] == 1:
                    self.audio.play_sound("bump")
                    self.score = max(0, self.score - 5)
                elif self.maze[ny][nx] == 2:
                    self.audio.play_sound("success")
                    self.audio.speak(self._("goal_reached"), interrupt=True)
                    self.score += 1000
                    self.finish()
                else:
                    self.px, self.py = nx, ny
                    # Valid step
                    self.audio.play_tone(250, duration_ms=80, volume=30)
                    
    def update(self):
        if not self.active or self.is_tutorial:
            return
            
        current_time = time.time()
        if current_time - self.last_wind_time > self.wind_interval:
            # Play wind hint
            dx = self.gx - self.px
            dy = self.gy - self.py
            
            # Panning
            # if dx > 0 (goal is right), pan is positive
            pan = max(-1.0, min(1.0, dx / (self.width / 2.0)))
            
            # Frequency
            # if dy < 0 (goal is up), frequency should be higher. 
            freq = max(100, min(800, 400 - dy * 30))
            
            self.audio.play_tone(freq, duration_ms=300, volume=15, pan=pan)
            self.last_wind_time = current_time

    def draw(self, screen):
        screen.fill((10, 10, 10))
        font = pygame.font.SysFont("Arial", 40, bold=True)
        title = font.render("AUDIO-LABYRINTH", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        info_font = pygame.font.SysFont("Arial", 20)
        info = info_font.render("Finde den Ausgang nur durch Hören!", True, (150, 150, 150))
        screen.blit(info, (400 - info.get_width()//2, 100))
        
        cell_size = 30
        offset_x = 400 - (self.width * cell_size) // 2
        offset_y = 300 - (self.height * cell_size) // 2
        
        # Player only
        player_rect = pygame.Rect(offset_x + self.px * cell_size + 5, offset_y + self.py * cell_size + 5, cell_size - 10, cell_size - 10)
        pygame.draw.ellipse(screen, (255, 215, 0), player_rect)
