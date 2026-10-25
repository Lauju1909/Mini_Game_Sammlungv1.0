import pygame
from games.base_game import BaseGame

class CapitalHunter(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "capital_hunter"
        self.instructions = self._("game_capital_hunter_instructions")
        self.idx = 0

    def start(self):
        super().start()
        # Initialize data here to ensure correct language
        self.data = [
            {"country": self._("cap_germany"), "options": [self._("ch_berlin"), self._("ch_vienna"), self._("ch_bern")], "correct": 0},
            {"country": self._("cap_france"), "options": [self._("ch_london"), self._("ch_paris"), self._("ch_rome")], "correct": 1},
            {"country": self._("cap_italy"), "options": [self._("ch_madrid"), self._("ch_milan"), self._("ch_rome")], "correct": 2}
        ]
        self._ask()

    def _ask(self):
        q = self.data[self.idx]
        text = self._("cap_country", country=q["country"])
        text += f" 1: {q['options'][0]}, 2: {q['options'][1]}, 3: {q['options'][2]}"
        self.audio.speak(text)

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: self._check(0)
            elif event.key == pygame.K_2: self._check(1)
            elif event.key == pygame.K_3: self._check(2)
            elif event.key == pygame.K_ESCAPE: self.finish()

    def _check(self, choice):
        if choice == self.data[self.idx]["correct"]:
            self.audio.play_sound("success")
            self.score += 100
        else:
            self.audio.play_sound("error")
        self.idx += 1
        if self.idx >= len(self.data): self.finish()
        else: self._ask()

    def draw(self, screen):
        # Hauptstädte-Quiz
        pygame.draw.rect(screen, (20, 25, 40), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (80, 160, 255), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 22)
        
        title = font.render(f"HAUPTSTADT-JÄGER - FRAGE {self.idx + 1} / {len(self.data) if hasattr(self, 'data') else 3}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        if hasattr(self, 'data') and self.idx < len(self.data):
            q = self.data[self.idx]
            q_txt = font.render(f"Was ist die Hauptstadt von {q['country']}?", True, (230, 240, 255))
            screen.blit(q_txt, (400 - q_txt.get_width() // 2, 240))
            
            for i, opt in enumerate(q["options"]):
                oy = 300 + i * 45
                pygame.draw.rect(screen, (40, 50, 75), (160, oy, 480, 38), border_radius=8)
                opt_txt = small_font.render(f"Taste {i + 1}: {opt}", True, (255, 255, 255))
                screen.blit(opt_txt, (180, oy + 6))
                
        hint = small_font.render("Drücke Taste 1, 2 oder 3 auf deiner Tastatur", True, (170, 190, 220))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

