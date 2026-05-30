import random
import pygame
from games.base_game import BaseGame

class CodeBreaker(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "code_breaker"
        self.instructions = self._("game_code_breaker_instructions")
        
        # 3-stelliger Code aus den Zahlen 1-4
        self.target_code = [random.randint(1, 4) for _ in range(3)]
        self.current_guess = [1, 1, 1]
        self.selected_slot = 0
        self.attempts = 0
        self.max_attempts = 10
        
        # Sound-Mapping für die 4 möglichen Noten
        self.tones = {
            1: "click_001",
            2: "click_002",
            3: "click_003",
            4: "click_004"
        }

    def start(self):
        super().start()
        self.audio.speak(self._("instructions"), interrupt=False)
        self._announce_current_slot()

    def _announce_current_slot(self):
        self.audio.speak(f"Stelle {self.selected_slot + 1}: Ton {self.current_guess[self.selected_slot]}", interrupt=True)
        self.audio.play_sound(self.tones[self.current_guess[self.selected_slot]])

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.current_guess[self.selected_slot] < 4:
                    self.current_guess[self.selected_slot] += 1
                    self._announce_current_slot()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_DOWN:
                if self.current_guess[self.selected_slot] > 1:
                    self.current_guess[self.selected_slot] -= 1
                    self._announce_current_slot()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_RIGHT:
                if self.selected_slot < 2:
                    self.selected_slot += 1
                    self._announce_current_slot()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_LEFT:
                if self.selected_slot > 0:
                    self.selected_slot -= 1
                    self._announce_current_slot()
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_RETURN:
                self._check_combination()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _check_combination(self):
        self.attempts += 1
        self.audio.speak(self._("code_breaker_guess"))
        
        result_types = [] # 2 = Richtig, 1 = Falsche Stelle, 0 = Nicht dabei
        
        temp_target = list(self.target_code)
        temp_guess = list(self.current_guess)
        results = [0, 0, 0]
        
        # Erster Pass: Richtige Positionen
        for i in range(3):
            if temp_guess[i] == temp_target[i]:
                results[i] = 2
                temp_target[i] = None
                temp_guess[i] = -1
        
        # Zweiter Pass: Falsche Positionen
        for i in range(3):
            if temp_guess[i] != -1:
                if temp_guess[i] in temp_target:
                    results[i] = 1
                    temp_target[temp_target.index(temp_guess[i])] = None
        
        # Ansage der Ergebnisse
        correct_count = results.count(2)
        wrong_pos_count = results.count(1)
        
        # Feedback-Sounds
        for r in results:
            if r == 2: self.audio.play_sound("confirmation_001")
            elif r == 1: self.audio.play_sound("bong_001")
            else: self.audio.play_sound("error_001")
        
        if correct_count == 3:
            self.score = max(100, 1000 - (self.attempts - 1) * 100)
            self.audio.speak(self._("correct_number", number=" ".join(map(str, self.target_code)), tries=self.attempts))
            self.audio.play_sound("success")
            self.finish()
        elif self.attempts >= self.max_attempts:
            self.score = 0
            self.audio.speak(self._("game_over"))
            self.finish()
        else:
            self.audio.speak(f"{correct_count} an richtiger Stelle, {wrong_pos_count} an falscher Stelle.")

    def draw(self, screen):
        # Hintergrund
        pygame.draw.rect(screen, (30, 30, 40), (100, 150, 600, 300), border_radius=20)
        
        # Titel
        font_title = pygame.font.SysFont("Arial", 40, bold=True)
        title = font_title.render("CODE-KNACKER", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 80))
        
        # Zeichne die 3 Slots
        for i in range(3):
            x = 200 + i * 150
            y = 250
            rect = pygame.Rect(x, y, 100, 120)
            
            # Farbe des Slots
            color = (60, 60, 80)
            border_color = (150, 150, 200)
            
            if self.selected_slot == i:
                color = (100, 100, 150)
                border_color = (255, 255, 0) # Markierung für aktuellen Slot
            
            pygame.draw.rect(screen, color, rect, border_radius=15)
            pygame.draw.rect(screen, border_color, rect, width=4, border_radius=15)
            
            # Wert im Slot
            font_val = pygame.font.SysFont("Arial", 50, bold=True)
            val_surf = font_val.render(str(self.current_guess[i]), True, (255, 255, 255))
            screen.blit(val_surf, (x + 50 - val_surf.get_width()//2, y + 35))
            
            # Pfeile hoch/runter Indikatoren
            if self.selected_slot == i:
                # Kleiner Pfeil oben/unten
                pygame.draw.polygon(screen, (255, 255, 255), [(x+50, y+10), (x+40, y+25), (x+60, y+25)])
                pygame.draw.polygon(screen, (255, 255, 255), [(x+50, y+110), (x+40, y+95), (x+60, y+95)])

        # Versuche anzeigen
        font_info = pygame.font.SysFont("Arial", 24)
        attempts_text = f"Versuch: {self.attempts} / {self.max_attempts}"
        attempts_surf = font_info.render(attempts_text, True, (200, 200, 200))
        screen.blit(attempts_surf, (400 - attempts_surf.get_width()//2, 400))
