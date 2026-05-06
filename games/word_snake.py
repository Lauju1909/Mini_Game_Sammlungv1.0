import random
from games.base_game import BaseGame

class WordSnake(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "word_snake"
        self.instructions = self._("game_word_snake_instructions")
        self.last_word = "Audio"
        self.current_input = ""
        # Startwort wird jetzt in start() angesagt
    def start(self):
        super().start()
        self.audio.speak(self._("word_snake_start", word=self.last_word), interrupt=False)

    def handle_input(self, event):
        import pygame
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.current_input.lower().startswith(self.last_word[-1].lower()):
                    self.audio.play_sound("success")
                    self.score += 50
                    self.last_word = self.current_input
                    self.current_input = ""
                    if self.score >= 250: self.finish()
                    else: self.audio.speak(self._("word_snake_next", char=self.last_word[-1]))
                else:
                    self.audio.speak(self._("word_snake_wrong", char=self.last_word[-1]))
                    self.current_input = ""
            elif event.key == pygame.K_ESCAPE:
                self.finish()
            else:
                char = event.unicode
                if char.isalpha():
                    self.current_input += char
                    self.audio.speak(char)

    def draw(self, screen):
        import pygame
        font = pygame.font.SysFont("Arial", 40, bold=True)
        # Snake-Körper-Hintergrund
        pygame.draw.rect(screen, (40, 60, 40), (100, 150, 600, 300), border_radius=20)
        
        # Letztes Wort
        last_surf = font.render(f"Letztes Wort: {self.last_word}", True, (200, 255, 200))
        screen.blit(last_surf, (400 - last_surf.get_width()//2, 200))
        
        # Nächster Buchstabe Hint
        hint_surf = font.render(f"Nächster Buchstabe: {self.last_word[-1].upper()}", True, (255, 215, 0))
        screen.blit(hint_surf, (400 - hint_surf.get_width()//2, 260))
        
        # Aktuelle Eingabe
        input_surf = font.render(f"> {self.current_input}_", True, (255, 255, 255))
        screen.blit(input_surf, (400 - input_surf.get_width()//2, 350))
        
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (100, 100))
