import random
import pygame
import time
from games.base_game import BaseGame

class SimonSays(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "simon_says"
        self.instructions = self._("game_simon_says_instructions")
        self.sequence = []
        self.player_sequence = []
        self.is_playing_sequence = False
        self.active_key = None
        self.active_timer = 0

    def start(self):
        super().start()
        self._add_to_sequence(interrupt=False)

    def _add_to_sequence(self, interrupt=True):
        self.sequence.append(random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]))
        self.player_sequence = []
        self.seq_idx = 0
        self.is_playing_sequence = True
        self.last_seq_time = time.time()
        self.audio.speak(self._("simon_listen"), interrupt=interrupt)

    def update(self):
        if self.is_tutorial:
            self.update_tutorial()
            return

        if self.active_timer > 0:
            self.active_timer -= 1
            if self.active_timer == 0: self.active_key = None

        if self.is_playing_sequence:
            now = time.time()
            if now - self.last_seq_time > 0.8:
                if self.seq_idx < len(self.sequence):
                    key = self.sequence[self.seq_idx]
                    names = {
                        pygame.K_UP: self._("simon_up"),
                        pygame.K_DOWN: self._("simon_down"),
                        pygame.K_LEFT: self._("simon_left"),
                        pygame.K_RIGHT: self._("simon_right")
                    }
                    self.audio.speak(names[key])
                    self.active_key = key
                    self.active_timer = 30
                    self.seq_idx += 1
                    self.last_seq_time = now
                else:
                    self.is_playing_sequence = False
                    self.audio.speak(self._("simon_your_turn"))

    def update_tutorial(self):
        if self.tutorial_step == 1:
            self.audio.speak(self._("tut_ss_1"), priority=1)
            self.tutorial_step = 2
        elif self.tutorial_step == 2:
            if not self.audio.is_speaking():
                self.audio.speak(self._("tut_ss_2"), priority=1)
                self.tutorial_step = 3
        elif self.tutorial_step == 3:
            if not self.audio.is_speaking():
                self.audio.speak(self._("tut_ss_3"), priority=1)
                self.tutorial_step = 4
        elif self.tutorial_step == 4:
            if not self.audio.is_speaking():
                self.audio.speak(self._("tut_ss_4"), priority=1)
                self.tutorial_step = 5
        elif self.tutorial_step == 6:
            if not self.audio.is_speaking():
                self.finish_tutorial()

    def handle_input(self, event):
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if self.is_playing_sequence: return
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                self.player_sequence.append(event.key)
                self.active_key = event.key
                self.active_timer = 20
                idx = len(self.player_sequence) - 1
                if self.player_sequence[idx] == self.sequence[idx]:
                    self.audio.play_sound("click")
                    if len(self.player_sequence) == len(self.sequence):
                        self.score += 10
                        self._add_to_sequence()
                else:
                    self.audio.play_sound("error")
                    self.audio.speak(self._("wrong"))
                    self.finish()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def handle_tutorial_input(self, event):
        super().handle_tutorial_input(event)
        if event.type == pygame.KEYDOWN:
            if self.tutorial_step == 5:
                if event.key == pygame.K_UP:
                    self.audio.play_sound("success")
                    self.audio.speak(self._("good"), priority=2)
                    self.tutorial_step = 6
                elif event.key in [pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self.audio.speak(self._("wrong"), priority=2)
                    self.audio.speak(self._("tut_ss_4"), priority=2)

    def draw(self, screen):
        # Zeichne das klassische 4-Farben-Kreuz
        center_x, center_y = 400, 300
        size = 120
        gap = 10
        
        # Positionen und Farben
        # Oben (Gelb), Unten (Blau), Links (Rot), Rechts (Grün)
        pads = [
            (pygame.K_UP, (center_x - size//2, center_y - size - gap), (200, 200, 0), (255, 255, 100)),
            (pygame.K_DOWN, (center_x - size//2, center_y + gap), (0, 0, 200), (100, 100, 255)),
            (pygame.K_LEFT, (center_x - size - gap, center_y - size//2), (200, 0, 0), (255, 100, 100)),
            (pygame.K_RIGHT, (center_x + gap, center_y - size//2), (0, 200, 0), (100, 255, 100))
        ]
        
        for key, pos, color, bright_color in pads:
            rect = pygame.Rect(pos[0], pos[1], size, size)
            final_color = bright_color if self.active_key == key else color
            pygame.draw.rect(screen, final_color, rect, border_radius=15)
            # Schatten/Tiefe
            pygame.draw.rect(screen, (255, 255, 255), rect, width=3, border_radius=15)

        # Titel und Score
        font = pygame.font.SysFont("Arial", 36, bold=True)
        title = font.render("SIMON SAYS", True, (255, 255, 255))
        screen.blit(title, (center_x - title.get_width()//2, 50))
        
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (center_x - score_surf.get_width()//2, 520))
        
        if self.is_playing_sequence:
            msg = "Zuhören..."
            color = (255, 100, 100)
        else:
            msg = "Du bist dran!"
            color = (100, 255, 100)
        
        msg_surf = font.render(msg, True, color)
        screen.blit(msg_surf, (center_x - msg_surf.get_width()//2, 470))
