import random
import pygame
import time
from games.base_game import BaseGame

class MathBlitz(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "math_blitz"
        self.instructions = self._("game_math_blitz_instructions")
        self.current_answer = ""
        self.start_time = time.time()
        self.questions = 0
        self.time_limit = 30
        self.end_time = time.time() + self.time_limit
        self.a = 0
        self.b = 0
        self.op_char = "+"
        self.target = 0

    def update(self):
        if time.time() > self.end_time:
            self.audio.speak(self._("time_up"))
            self.finish()

    def start(self):
        super().start()
        self._next_question(interrupt=False)

    def _next_question(self, interrupt=True):
        self.a = random.randint(1, 15)
        self.b = random.randint(1, 15)
        self.op_char = random.choice(["+", "-"])
        self.target = self.a + self.b if self.op_char == "+" else self.a - self.b
        
        op_word = self._("math_plus") if self.op_char == "+" else self._("math_minus")
        self.audio.speak(self._("what_is", a=self.a, op=op_word, b=self.b), interrupt=interrupt)
        self.current_answer = ""

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.current_answer == str(self.target):
                    self.audio.play_sound("success")
                    # Dynamische Punkte: 100 Basis + Zeitbonus
                    remaining = max(0, self.end_time - time.time())
                    bonus = int(remaining * 5) # Bis zu 150 Punkte Bonus bei 30s
                    self.score += (100 + bonus)
                    
                    self.questions += 1
                    self._next_question()
                else:
                    self.audio.play_sound("error")
                    self.current_answer = ""
            elif event.key == pygame.K_BACKSPACE:
                self.current_answer = self.current_answer[:-1]
                self.audio.speak(self._("input_cleared") if not self.current_answer else self.current_answer[-1])
            elif event.key == pygame.K_ESCAPE:
                self.finish()
            else:
                char = event.unicode
                if char.isdigit() or char == "-":
                    self.current_answer += char
                    self.audio.speak(char)

    def draw(self, screen):
        # Hintergrund-Container
        pygame.draw.rect(screen, (40, 40, 60), (50, 100, 700, 400), border_radius=20)
        
        # Zeige Aufgabe
        font_large = pygame.font.SysFont("Arial", 90, bold=True)
        task_text = f"{self.a} {self.op_char} {self.b} ="
        task_surf = font_large.render(task_text, True, (255, 255, 255))
        screen.blit(task_surf, (400 - task_surf.get_width()//2, 180))
        
        # Zeige aktuelle Eingabe (mit blinkendem Cursor)
        cursor = "_" if int(time.time() * 2) % 2 == 0 else " "
        input_surf = font_large.render(self.current_answer + cursor, True, (255, 215, 0))
        screen.blit(input_surf, (400 - input_surf.get_width()//2, 280))
        
        # Zeige Zeitbalken
        remaining = max(0, self.end_time - time.time())
        width = int((remaining / self.time_limit) * 600)
        
        # Schatten für Balken
        pygame.draw.rect(screen, (20, 20, 30), (100, 420, 600, 25), border_radius=12)
        # Balkenfarbe wechselt zu Rot wenn Zeit knapp wird
        if remaining > 20: color = (50, 200, 50)
        elif remaining > 10: color = (200, 200, 50)
        else: color = (255, 50, 50)
        
        pygame.draw.rect(screen, color, (100, 420, width, 25), border_radius=12)
        # Leuchteffekt am Ende des Balkens
        if width > 0:
            pygame.draw.circle(screen, (255, 255, 255), (100 + width, 432), 8)
        
        # Punktestand und Statistik
        info_font = pygame.font.SysFont("Arial", 30)
        score_surf = info_font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        screen.blit(score_surf, (100, 120))
        
        q_surf = info_font.render(f"Gelöst: {self.questions}", True, (200, 200, 255))
        screen.blit(q_surf, (700 - q_surf.get_width(), 120))
