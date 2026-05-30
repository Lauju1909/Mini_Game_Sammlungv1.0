import random
import pygame
from games.base_game import BaseGame

class BlindFarm(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "blind_farm"
        self.instructions = self._("game_blind_farm_instructions")
        # Verwende Schlüssel statt hartkodierter Namen
        self.item_keys = [f"farm_item_{i}" for i in range(1, 11)]
        random.shuffle(self.item_keys)
        self.pos = 0
        self.target_key = "farm_item_7" # Schatzkiste

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if self.pos < len(self.item_keys) - 1:
                    self.pos += 1
                    self._play_item_sound()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if self.pos > 0:
                    self.pos -= 1
                    self._play_item_sound()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_RETURN:
                if self.item_keys[self.pos] == self.target_key:
                    self.audio.play_sound("success")
                    self.audio.speak(self._("farm_found"))
                    self.score = 500
                    self.finish()
                else:
                    self.audio.play_sound("error")
                    item_name = self._(self.item_keys[self.pos])
                    self.audio.speak(self._("just_an_item", item=item_name))
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _play_item_sound(self):
        sounds = [
            "click", "confirm", "select", "typing", "bump", 
            "blip", "cash", "confirm", "select", "click"
        ]
        self.audio.play_sound(sounds[self.pos % len(sounds)])
        self.audio.speak(self._("item_number", idx=self.pos + 1))

    def draw(self, screen):
        # Zeichne Scheune / Heuhaufen
        pygame.draw.rect(screen, (80, 50, 30), (50, 200, 700, 300), border_radius=15)
        
        # Titel
        font = pygame.font.SysFont("Arial", 40, bold=True)
        title = font.render("DURCHSUCHE DIE SCHEUNE!", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 100))
        
        # Zeichne die Plätze
        for i in range(len(self.item_keys)):
            x = 100 + i * 65
            y = 350
            rect = pygame.Rect(x, y, 50, 80)
            
            # Farbe basierend auf Auswahl
            color = (150, 100, 50)
            if self.pos == i:
                color = (255, 200, 50)
                # Cursor-Effekt
                pygame.draw.rect(screen, (255, 255, 255), (x-5, y-5, 60, 90), 3, border_radius=10)
            
            pygame.draw.rect(screen, color, rect, border_radius=10)
            
            # Label
            idx_font = pygame.font.SysFont("Arial", 20)
            label = idx_font.render(str(i+1), True, (255, 255, 255))
            screen.blit(label, (x + 25 - label.get_width()//2, y + 90))
            
        # Info zum aktuellen Platz
        info_font = pygame.font.SysFont("Arial", 24)
        info_text = f"Platz {self.pos + 1} wird durchsucht..."
        info_surf = info_font.render(info_text, True, (200, 200, 200))
        screen.blit(info_surf, (400 - info_surf.get_width()//2, 480))
