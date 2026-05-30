import pygame
from games.base_game import BaseGame

class AudioMaze(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_maze"
        self.instructions = self._("game_audio_maze_instructions")
        # 0 = leer, 1 = Wand, 2 = Ziel
        self.maze = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [1, 2, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ]
        self.px, self.py = 1, 1

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        
        if event.type == pygame.KEYDOWN:
            nx, ny = self.px, self.py
            if event.key == pygame.K_UP:
                if ny > 0: ny -= 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_DOWN:
                if ny < len(self.maze) - 1: ny += 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if nx > 0: nx -= 1
                else: self.audio.play_sound("bump")
            elif event.key == pygame.K_RIGHT:
                if nx < len(self.maze[0]) - 1: nx += 1
                else: self.audio.play_sound("bump")

            if self.maze[ny][nx] == 1:
                self.audio.play_sound("bump")
                self.audio.speak(self._("wall"))
            elif self.maze[ny][nx] == 2:
                self.audio.play_sound("success")
                self.audio.speak(self._("goal_reached"))
                self.score = 300
                self.finish()
            else:
                self.px, self.py = nx, ny
                # Richtungs-Hint: Wo ist das Ziel (2)?
                target_pos = None
                for y in range(len(self.maze)):
                    for x in range(len(self.maze[y])):
                        if self.maze[y][x] == 2: target_pos = (x, y)
                
                if target_pos:
                    dx = target_pos[0] - self.px
                    # Pan: -1 (ganz links) bis 1 (ganz rechts)
                    pan = max(-1.0, min(1.0, dx / 5.0))
                    self.audio.play_panned_sound("blip", pan)
                
                self.audio.speak(self._("position_feedback", x=self.px, y=self.py))
    def draw(self, screen):
        # Zeichne Gitter
        cell_size = 80
        offset_x = 400 - (len(self.maze[0]) * cell_size) // 2
        offset_y = 300 - (len(self.maze) * cell_size) // 2
        
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                rect = pygame.Rect(offset_x + x * cell_size, offset_y + y * cell_size, cell_size, cell_size)
                if cell == 1: # Wand
                    pygame.draw.rect(screen, (50, 50, 70), rect, border_radius=5)
                    pygame.draw.rect(screen, (100, 100, 150), rect, 2, border_radius=5)
                elif cell == 2: # Ziel
                    pygame.draw.rect(screen, (50, 150, 50), rect, border_radius=20)
                    # Stern/Ziel-Icon Ersatz
                    pygame.draw.circle(screen, (255, 255, 255), rect.center, 15, 3)
                else: # Weg
                    pygame.draw.rect(screen, (30, 30, 40), rect)
                    pygame.draw.rect(screen, (40, 40, 50), rect, 1)

        # Zeichne Spieler
        player_rect = pygame.Rect(offset_x + self.px * cell_size + 10, offset_y + self.py * cell_size + 10, cell_size - 20, cell_size - 20)
        pygame.draw.ellipse(screen, (255, 215, 0), player_rect)
        pygame.draw.ellipse(screen, (255, 255, 255), player_rect, 3)
        
        # Titel
        font = pygame.font.SysFont("Arial", 40, bold=True)
        title = font.render("AUDIO-LABYRINTH", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
