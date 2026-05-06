import random
import pygame
import time
from games.base_game import BaseGame

class AudioSequence(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_sequence"
        self.instructions = self._("game_audio_sequence_instructions")
        
        # 4 verschiedene Sounds für die 4 Richtungen
        self.direction_sounds = {
            pygame.K_UP: "confirm",
            pygame.K_DOWN: "bump",
            pygame.K_LEFT: "select",
            pygame.K_RIGHT: "cash"
        }
        
        self.sequence = []
        self.player_sequence = []
        self.is_playing_sequence = False
        self.active_key = None
        self.active_timer = 0
        self.seq_idx = 0
        self.last_seq_time = 0

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
        if self.active_timer > 0:
            self.active_timer -= 1
            if self.active_timer == 0: self.active_key = None

        if self.is_playing_sequence:
            now = time.time()
            if now - self.last_seq_time > 1.0: # Langsamere Abfolge für bessere Merkfähigkeit
                if self.seq_idx < len(self.sequence):
                    key = self.sequence[self.seq_idx]
                    
                    # Sound abspielen UND Richtung ansagen
                    self.audio.play_sound(self.direction_sounds[key])
                    
                    names = {
                        pygame.K_UP: self._("simon_up"),
                        pygame.K_DOWN: self._("simon_down"),
                        pygame.K_LEFT: self._("simon_left"),
                        pygame.K_RIGHT: self._("simon_right")
                    }
                    # Kurze Pause nach Sound, dann Name
                    self.audio.speak(names[key], interrupt=False)
                    
                    self.active_key = key
                    self.active_timer = 40
                    self.seq_idx += 1
                    self.last_seq_time = now
                else:
                    self.is_playing_sequence = False
                    self.audio.speak(self._("simon_your_turn"))

    def handle_input(self, event):
        if self.is_playing_sequence: return
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                self.player_sequence.append(event.key)
                self.active_key = event.key
                self.active_timer = 25
                
                # Feedback für Tastendruck
                self.audio.play_sound(self.direction_sounds[event.key])
                
                idx = len(self.player_sequence) - 1
                if self.player_sequence[idx] == self.sequence[idx]:
                    if len(self.player_sequence) == len(self.sequence):
                        self.score += 10 + len(self.sequence) * 5
                        self.audio.play_sound("success")
                        self._add_to_sequence()
                else:
                    self.audio.play_sound("error")
                    self.audio.speak(self._("wrong"))
                    self.finish()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def draw(self, screen):
        # Visuelle Darstellung ähnlich wie Simon Says, aber mit Icons/Effekten
        center_x, center_y = 400, 300
        size = 130
        gap = 15
        
        pads = [
            (pygame.K_UP, (center_x - size//2, center_y - size - gap), (255, 200, 0), "↑"),
            (pygame.K_DOWN, (center_x - size//2, center_y + gap), (0, 150, 255), "↓"),
            (pygame.K_LEFT, (center_x - size - gap, center_y - size//2), (255, 80, 80), "←"),
            (pygame.K_RIGHT, (center_x + gap, center_y - size//2), (50, 220, 100), "→")
        ]
        
        for key, pos, color, arrow in pads:
            rect = pygame.Rect(pos[0], pos[1], size, size)
            is_active = (self.active_key == key)
            
            # Hintergrund mit Verlauf/Glow wenn aktiv
            if is_active:
                for r in range(10):
                    pygame.draw.rect(screen, (*color, 100 - r*10), rect.inflate(r*2, r*2), border_radius=20, width=1)
                final_color = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            else:
                final_color = color
            
            pygame.draw.rect(screen, final_color, rect, border_radius=20)
            pygame.draw.rect(screen, (255, 255, 255, 100), rect, width=3, border_radius=20)
            
            # Pfeil-Symbol
            font = pygame.font.SysFont("Arial", 60, bold=True)
            arr_surf = font.render(arrow, True, (255, 255, 255))
            screen.blit(arr_surf, (rect.centerx - arr_surf.get_width()//2, rect.centery - arr_surf.get_height()//2))

        # Status und Score
        font_main = pygame.font.SysFont("Arial", 36, bold=True)
        title = font_main.render(self._("game_audio_sequence").upper(), True, (255, 255, 255))
        screen.blit(title, (center_x - title.get_width()//2, 40))
        
        score_text = f"{self._('points')}: {self.score}"
        score_surf = font_main.render(score_text, True, (255, 215, 0))
        screen.blit(score_surf, (center_x - score_surf.get_width()//2, 530))
        
        status_msg = self._("simon_listen") if self.is_playing_sequence else self._("simon_your_turn")
        status_color = (255, 150, 0) if self.is_playing_sequence else (0, 255, 150)
        status_surf = font_main.render(status_msg, True, status_color)
        screen.blit(status_surf, (center_x - status_surf.get_width()//2, 480))
