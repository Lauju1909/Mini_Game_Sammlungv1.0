import random
from games.base_game import BaseGame

class NumberGuess(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "number_guess"
        self.target = random.randint(1, 100)
        self.attempts = 0
        self.current_guess = 50
        self.instructions = self._("game_number_guess_instructions")

    def handle_input(self, event):
        import pygame
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.current_guess < 100:
                    self.current_guess += 1
                    self.audio.speak(str(self.current_guess))
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_DOWN:
                if self.current_guess > 1:
                    self.current_guess -= 1
                    self.audio.speak(str(self.current_guess))
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_PAGEUP:
                if self.current_guess < 100:
                    self.current_guess = min(100, self.current_guess + 10)
                    self.audio.speak(str(self.current_guess))
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_PAGEDOWN:
                if self.current_guess > 1:
                    self.current_guess = max(1, self.current_guess - 10)
                    self.audio.speak(str(self.current_guess))
                else:
                    self.audio.play_sound("bump")
            elif event.key == pygame.K_RETURN:
                self.attempts += 1
                if self.current_guess == self.target:
                    # Skaliere auf 1000 Punkte Basis
                    self.score = max(100, 1000 - (self.attempts - 1) * 50)
                    self.audio.speak(self._("correct_number", number=self.target, tries=self.attempts))
                    self.finish()
                elif self.current_guess < self.target:
                    self.audio.speak(self._("higher"))
                else:
                    self.audio.speak(self._("lower"))
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def draw(self, screen):
        font_large = pygame.font.SysFont("Arial", 48, bold=True)
        font_medium = pygame.font.SysFont("Arial", 32)
        
        # Hintergrund-Box
        rect = pygame.Rect(150, 150, 500, 300)
        pygame.draw.rect(screen, (40, 40, 60), rect, border_radius=20)
        pygame.draw.rect(screen, (255, 215, 0), rect, width=3, border_radius=20)
        
        # Titel
        title_surf = font_medium.render(self._("game_number_guess"), True, (255, 255, 255))
        screen.blit(title_surf, (400 - title_surf.get_width()//2, 170))
        
        # Aktuelle Zahl
        guess_surf = font_large.render(str(self.current_guess), True, (255, 255, 0))
        screen.blit(guess_surf, (400 - guess_surf.get_width()//2, 230))
        
        # Balken zur Orientierung (1-100)
        pygame.draw.line(screen, (100, 100, 100), (200, 320), (600, 320), 5)
        pos_x = 200 + (self.current_guess - 1) * 4
        pygame.draw.circle(screen, (255, 215, 0), (pos_x, 320), 10)
        
        # Versuche
        attempts_text = f"Versuche: {self.attempts}"
        attempts_surf = font_medium.render(attempts_text, True, (200, 200, 200))
        screen.blit(attempts_surf, (400 - attempts_surf.get_width()//2, 380))
