import random
import pygame
import time
from games.base_game import BaseGame

class MoleMaster(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "mole_master"
        self.instructions = self._("game_mole_master_instructions")
        self.moles = [None] * 4 # 4 Löcher: Links, Oben, Rechts, Unten
        self.active_mole = None
        self.mole_timer = 0
        self.game_timer = 30 # 30 Sekunden
        self.start_time = 0
        self.mole_spawn_rate = 1.5
        self.last_mole_time = 0
        self.reaction_times = []

    def start(self):
        super().start()
        self.start_time = time.time()
        self.last_mole_time = self.start_time
        self.audio.speak(self._("ready"), interrupt=False)

    def update(self):
        if not self.active: return
        
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if elapsed > self.game_timer:
            self.finish()
            return

        # Neuen Maulwurf spawnen
        if self.active_mole is None:
            if current_time - self.last_mole_time > self.mole_spawn_rate:
                self.active_mole = random.randint(0, 3)
                self.last_mole_time = current_time
                self.mole_timer = current_time
                
                # Akustisches Feedback für Richtung
                directions = ["key_left", "key_up", "key_right", "key_down"]
                pan = [-1.0, 0.0, 1.0, 0.0][self.active_mole]
                self.audio.play_panned_sound("click", pan)
                # Ansage optional, aber für Blindheit wichtig
                self.audio.speak(self._(directions[self.active_mole]))
        
        # Maulwurf verschwindet, wenn zu langsam
        elif current_time - self.mole_timer > 1.2:
            self.active_mole = None
            self.last_mole_time = current_time
            self.audio.play_sound("bump")

    def handle_input(self, event):
        super().handle_input(event)
        if not self.active: return
        if event.type == pygame.KEYDOWN:
            hit = False
            if self.active_mole == 0 and event.key == pygame.K_LEFT: hit = True
            elif self.active_mole == 1 and event.key == pygame.K_UP: hit = True
            elif self.active_mole == 2 and event.key == pygame.K_RIGHT: hit = True
            elif self.active_mole == 3 and event.key == pygame.K_DOWN: hit = True
            
            if hit:
                reaction = time.time() - self.mole_timer
                points = max(10, int(100 * (1.0 - reaction)))
                self.score += points
                self.audio.play_sound("confirm")
                self.active_mole = None
                self.last_mole_time = time.time()
                # Schwierigkeit leicht steigern
                self.mole_spawn_rate = max(0.5, self.mole_spawn_rate * 0.95)
            elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                self.audio.play_sound("error")
                self.score = max(0, self.score - 5)

    def draw(self, screen):
        # 4 Löcher im Kreis zeichnen
        center = (400, 300)
        radius = 150
        hole_radius = 50
        
        positions = [
            (center[0] - radius, center[1]), # Links
            (center[0], center[1] - radius), # Oben
            (center[0] + radius, center[1]), # Rechts
            (center[0], center[1] + radius)  # Unten
        ]
        
        colors = [
            (200, 50, 50),  # Rot
            (50, 200, 50),  # Grün
            (50, 50, 200),  # Blau
            (200, 200, 50)  # Gelb
        ]
        
        for i, pos in enumerate(positions):
            # Loch
            pygame.draw.circle(screen, (30, 30, 30), pos, hole_radius)
            pygame.draw.circle(screen, colors[i], pos, hole_radius, width=3)
            
            # Maulwurf, falls aktiv
            if self.active_mole == i:
                # Pulsierender Maulwurf
                pulse = (pygame.time.get_ticks() % 500) / 500.0
                mole_color = tuple(min(255, c + int(pulse * 55)) for c in colors[i])
                pygame.draw.circle(screen, mole_color, pos, hole_radius - 10)
                
                # Augen
                eye_color = (255, 255, 255)
                pygame.draw.circle(screen, eye_color, (pos[0]-15, pos[1]-10), 5)
                pygame.draw.circle(screen, eye_color, (pos[0]+15, pos[1]-10), 5)

        # Zeitbalken
        elapsed = time.time() - self.start_time
        remaining = max(0, self.game_timer - elapsed)
        bar_width = int(600 * (remaining / self.game_timer))
        pygame.draw.rect(screen, (50, 50, 50), (100, 500, 600, 20), border_radius=10)
        pygame.draw.rect(screen, (255, 215, 0), (100, 500, bar_width, 20), border_radius=10)
        
        # Punkte
        font = pygame.font.SysFont("Arial", 36, bold=True)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width()//2, 540))
