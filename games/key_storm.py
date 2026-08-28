import random
import pygame
import time
from games.base_game import BaseGame

class KeyStorm(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "key_storm"
        self.instructions = self._("game_key_storm_instructions")
        self.keys = {
            pygame.K_UP: self._("key_up"),
            pygame.K_DOWN: self._("key_down"),
            pygame.K_LEFT: self._("key_left"),
            pygame.K_RIGHT: self._("key_right"),
            pygame.K_SPACE: self._("key_space")
        }
        self.end_time = 0
        self.target_key = None

    def start(self):
        super().start()
        self.end_time = time.monotonic() + 20
        self.score = 0
        self._next_key(interrupt=False)

    def _next_key(self, interrupt=True):
        self.target_key = random.choice(list(self.keys.keys()))
        self.audio.speak(self.keys[self.target_key], interrupt=interrupt)
        self.key_start_time = time.monotonic()

    def update(self):
        if time.monotonic() > self.end_time:
            self.audio.speak(self._("time_up"))
            self.finish()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.target_key:
                # Punkte: 100 + Zeitbonus (bis zu 200)
                reaction_time = time.monotonic() - self.key_start_time
                bonus = max(0, int((1.5 - reaction_time) * 100))
                self.score += (100 + bonus)
                
                self.audio.play_sound("success")
                self._next_key()
            elif event.key == pygame.K_ESCAPE:
                self.finish()
            elif event.key in self.keys: # Falsche Taste
                self.audio.play_sound("error")

    def draw(self, screen):
        # Hintergrund
        pygame.draw.rect(screen, (30, 50, 30), (100, 150, 600, 300), border_radius=20)
        
        # Titel
        font_title = pygame.font.SysFont("Arial", 40, bold=True)
        title_text = self._("game_key_storm_title")
        if title_text == "game_key_storm_title": title_text = "TASTEN-GEWITTER!"
        title = font_title.render(title_text, True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 80))
        
        # Die gesuchte Taste groß anzeigen
        if self.target_key is not None and self.target_key in self.keys:
            key_name = self.keys[self.target_key].upper()
        else:
            key_name = "?"
        font_key = pygame.font.SysFont("Arial", 100, bold=True)
        key_surf = font_key.render(key_name, True, (255, 255, 0))
        screen.blit(key_surf, (400 - key_surf.get_width()//2, 230))
        
        # Zeitbalken
        remaining = max(0, self.end_time - time.monotonic())
        width = int((remaining / 20) * 600)
        pygame.draw.rect(screen, (50, 50, 50), (100, 420, 600, 20), border_radius=10)
        pygame.draw.rect(screen, (200, 50, 50), (100, 420, width, 20), border_radius=10)
        
        # Punkte
        font_info = pygame.font.SysFont("Arial", 30)
        score_text = self._("score")
        if score_text == "score": score_text = "Score"
        score_surf = font_info.render(f"{score_text}: {self.score}", True, (255, 255, 255))
        screen.blit(score_surf, (100, 110))
