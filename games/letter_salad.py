import random
from games.base_game import BaseGame

class LetterSalad(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "letter_salad"
        self.instructions = self._("game_letter_salad_instructions")
        self.words = [
            self._("ls_word1"), self._("ls_word2"), self._("ls_word3"), 
            self._("ls_word4"), self._("ls_word5")
        ]
        self.target = random.choice(self.words)
        self.shuffled = list(self.target.lower())
        random.shuffle(self.shuffled)
        self.audio.speak(self._("letters_shuffled", letters=', '.join(self.shuffled)))
        self.current_input = ""

    def handle_input(self, event):
        import pygame
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.current_input.lower() == self.target.lower():
                    self.audio.play_sound("success")
                    self.score = 500
                    self.finish()
                else:
                    self.audio.speak(self._("try_again"))
                    self.current_input = ""
            elif event.key == pygame.K_ESCAPE: self.finish()
            else:
                char = event.unicode
                if char.isalpha():
                    self.current_input += char
                    self.audio.speak(char)

    def draw(self, screen):
        import pygame
        font = pygame.font.SysFont("Arial", 40, bold=True)
        # Salat-Hintergrund
        pygame.draw.rect(screen, (60, 40, 60), (100, 150, 600, 300), border_radius=20)
        
        # Buchstabensalat
        salad_text = ", ".join(self.shuffled).upper()
        salad_surf = font.render(salad_text, True, (255, 200, 255))
        screen.blit(salad_surf, (400 - salad_surf.get_width()//2, 200))
        
        # Eingabe
        input_surf = font.render(f"> {self.current_input}_", True, (255, 255, 255))
        screen.blit(input_surf, (400 - input_surf.get_width()//2, 300))
        
        title = font.render("BUCHSTABEN-SALAT", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 80))
