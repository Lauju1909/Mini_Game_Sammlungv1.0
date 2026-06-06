import random
import pygame
import math
import time
from games.base_game import BaseGame

class SoundMemo(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "sound_memo"
        self.instructions = self._("game_sound_memo_instructions")
        # Mehr Sounds für das Gitter nutzen
        all_available = ["click", "confirm", "select", "success", "error", "bump", "cash", "blip", "warn", "typing", "buy", "drumroll"]
        self.sounds = random.sample(all_available, 6) * 2
        random.shuffle(self.sounds)
        self.grid = self.sounds
        self.revealed = [False] * 12
        self.pos = 0
        self.first_choice = None
        self.second_choice = None
        self.timer = 0
        self.start_time = 0

    def start(self):
        super().start()
        self.start_time = time.time()
        self.audio.speak(self._("grid_field", pos=self.pos + 1), interrupt=False)

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.first_choice = None
                self.second_choice = None

    def handle_input(self, event):
        if self.timer > 0: return # Eingabe sperren während Anzeige
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if self.pos < 11:
                    self.pos += 1
                    if self.revealed[self.pos]:
                        self.audio.play_sound("confirm")
                        self.audio.speak(self._("grid_field_revealed", pos=self.pos + 1, item=self.grid[self.pos].capitalize()))
                    else:
                        self.audio.speak(self._("grid_field", pos=self.pos + 1))
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if self.pos > 0:
                    self.pos -= 1
                    if self.revealed[self.pos]:
                        self.audio.play_sound("confirm")
                        self.audio.speak(self._("grid_field_revealed", pos=self.pos + 1, item=self.grid[self.pos].capitalize()))
                    else:
                        self.audio.speak(self._("grid_field", pos=self.pos + 1))
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_RETURN:
                self._reveal()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _reveal(self):
        if self.revealed[self.pos] or self.pos == self.first_choice:
            self.audio.speak(self._("already_revealed"))
            return
        
        self.audio.play_sound(self.grid[self.pos])
        if self.first_choice is None:
            self.first_choice = self.pos
        else:
            self.second_choice = self.pos
            if self.grid[self.first_choice] == self.grid[self.pos]:
                self.audio.speak(self._("pair_found"))
                self.revealed[self.first_choice] = True
                self.revealed[self.pos] = True
                
                # Bonus-Punkte für Geschwindigkeit
                elapsed = time.time() - self.start_time
                time_bonus = max(0, int(50 - elapsed / 2))
                self.score += 20 + time_bonus
                
                if all(self.revealed): self.finish()
                self.first_choice = None
                self.second_choice = None
            else:
                self.audio.speak(self._("no_pair"))
                self.timer = 60 # 1 Sekunde zeigen

    def draw(self, screen):
        # Zeichne 4x3 Gitter
        font_large = pygame.font.SysFont("Arial", 28, bold=True)
        font_small = pygame.font.SysFont("Arial", 18)
        
        for i in range(12):
            col = i % 4
            row = i // 4
            x = 100 + col * 160
            y = 150 + row * 120
            rect = pygame.Rect(x, y, 140, 100)
            
            # Hintergrundfarbe basierend auf Status
            if self.revealed[i]:
                color = (50, 160, 80)  # Helleres Grün für gelöste Paare (offen)
                border_color = (150, 255, 180)
                # 3D Schatteneffekt
                pygame.draw.rect(screen, (0, 60, 20), (x+5, y+5, 140, 100), border_radius=15)
            elif self.first_choice == i or self.second_choice == i:
                color = (230, 160, 50)  # Leuchtendes Orange für aktive Auswahl
                border_color = (255, 255, 255)
            elif self.pos == i:
                color = (80, 80, 140) # Cursor-Farbe
                border_color = (255, 220, 50) # Goldener Rand
            else:
                color = (40, 40, 70)    # Verdeckt (Rückseite)
                border_color = (100, 100, 160)
            
            # Zeichne Karte mit abgerundeten Ecken
            pygame.draw.rect(screen, color, rect, border_radius=15)
            
            # Rückseiten-Muster für verdeckte Karten
            if not self.revealed[i] and self.first_choice != i and self.second_choice != i:
                # Ein dezentes Muster auf der Rückseite
                for dx in range(10, 140, 30):
                    pygame.draw.line(screen, (60, 60, 100), (x + dx, y + 5), (x + dx + 10, y + 95), 2)
            
            # Spezial-Effekt für gelöste Karten (Glow)
            if self.revealed[i]:
                for r in range(1, 6):
                    glow_surf = pygame.Surface((rect.width + r*4, rect.height + r*4), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (0, 255, 100, 30 // r), (0, 0, rect.width + r*4, rect.height + r*4), border_radius=15)
                    screen.blit(glow_surf, (x - r*2, y - r*2))
            
            # Glanzeffekt für alle Karten
            pygame.Rect(x, y, 140, 35)
            shine_surf = pygame.Surface((140, 35), pygame.SRCALPHA)
            pygame.draw.rect(shine_surf, (255, 255, 255, 20), (0, 0, 140, 35), border_top_left_radius=15, border_top_right_radius=15)
            screen.blit(shine_surf, (x, y))

            pygame.draw.rect(screen, border_color, rect, width=4 if self.pos == i else 2, border_radius=15)
            
            # Inhalt anzeigen, wenn aufgedeckt oder erste Wahl
            if self.revealed[i] or self.first_choice == i or self.second_choice == i:
                # Zeige den Namen des Sounds (Inhalt)
                sound_name = self.grid[i].capitalize()
                
                # Wenn gelöst, Text anzeigen (lokalisiert)
                # Wenn gelöst, Text anzeigen (lokalisiert)
                if self.revealed[i]:
                    solved_font = pygame.font.SysFont("Arial", 16, bold=True)
                    label_match = "MATCH!" # Etwas universelles
                    solved_surf = solved_font.render(label_match, True, (255, 255, 255))
                    # Glow pulsieren lassen
                    pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0
                    for r in range(1, 4):
                        alpha = int(100 * pulse / r)
                        if alpha > 0:
                            inf_rect = rect.inflate(r*4, r*4)
                            glow_s = pygame.Surface(inf_rect.size, pygame.SRCALPHA)
                            pygame.draw.rect(glow_s, (255, 255, 255, alpha), (0, 0, inf_rect.width, inf_rect.height), border_radius=15, width=2)
                            screen.blit(glow_s, inf_rect.topleft)
                    screen.blit(solved_surf, (x + 70 - solved_surf.get_width()//2, y + 80))
                
                content_surf = font_small.render(sound_name, True, (255, 255, 255))
                screen.blit(content_surf, (x + 70 - content_surf.get_width()//2, y + 55))
                
                # Ein Symbol-Ersatz (Erster Buchstabe groß)
                symbol_surf = font_large.render(sound_name[0], True, (255, 255, 255))
                screen.blit(symbol_surf, (x + 70 - symbol_surf.get_width()//2, y + 15))
                
                # Häkchen für fest aufgedeckte Karten
                if self.revealed[i]:
                    check_surf = font_large.render("✓", True, (0, 255, 0))
                    # Leuchteffekt um das Häkchen
                    pulse_val = int(abs(math.sin(time.time() * 4)) * 5)
                    circ_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(circ_surf, (0, 255, 100, 50), (20, 20), 10 + pulse_val, width=1)
                    screen.blit(circ_surf, (x + 120 - 20, y + 20 - 20))
                    screen.blit(check_surf, (x + 112, y + 5))
            else:
                # Zeige nur die Nummer des Feldes
                label_color = (255, 255, 255) if self.pos == i else (150, 150, 150)
                label = font_large.render(str(i+1), True, label_color)
                screen.blit(label, (x + 70 - label.get_width()//2, y + 50 - label.get_height()//2))

        # Punktestand oben anzeigen
        score_font = pygame.font.SysFont("Arial", 36, bold=True)
        score_text = self._("points") + f": {self.score}"
        score_surf = score_font.render(score_text, True, (255, 255, 255))
        screen.blit(score_surf, (400 - score_surf.get_width()//2, 80))
