import random
import pygame
import time
from games.base_game import BaseGame

class AudioMath(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_math"
        self.instructions = self._("game_audio_math_instructions")
        
        self.score = 0
        self.state = "waiting_for_start"
        self.lives = 3
        
        self.num1 = 0
        self.num2 = 0
        self.operation = "+"
        self.correct_answer = 0
        self.user_input = ""
        
        self.time_limit = 10.0
        self.question_timer = 0.0

    def start(self):
        super().start()
        self.audio.speak(self.instructions, interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_game(self):
        self.state = "playing"
        self.score = 0
        self.lives = 3
        self.time_limit = 10.0
        self.audio.speak(self._("start_go"), interrupt=True)
        self._next_question()

    def _next_question(self):
        self.user_input = ""
        # Increase difficulty with score
        if self.score < 5:
            self.num1 = random.randint(1, 10)
            self.num2 = random.randint(1, 10)
            self.operation = "+"
            self.correct_answer = self.num1 + self.num2
        elif self.score < 10:
            self.operation = random.choice(["+", "-"])
            if self.operation == "+":
                self.num1 = random.randint(5, 20)
                self.num2 = random.randint(5, 20)
                self.correct_answer = self.num1 + self.num2
            else:
                self.num1 = random.randint(10, 20)
                self.num2 = random.randint(1, 9)
                self.correct_answer = self.num1 - self.num2
        else:
            self.operation = random.choice(["+", "-", "*"])
            if self.operation == "+":
                self.num1 = random.randint(10, 50)
                self.num2 = random.randint(10, 50)
                self.correct_answer = self.num1 + self.num2
            elif self.operation == "-":
                self.num1 = random.randint(20, 50)
                self.num2 = random.randint(5, 19)
                self.correct_answer = self.num1 - self.num2
            else:
                self.num1 = random.randint(2, 9)
                self.num2 = random.randint(2, 9)
                self.correct_answer = self.num1 * self.num2
                
        op_spoken = self._("math_plus") if self.operation == "+" else self._("math_minus") if self.operation == "-" else self._("math_times")
        question_text = f"{self.num1} {op_spoken} {self.num2}"
        self.audio.speak(question_text, interrupt=True)
        
        self.question_timer = time.monotonic() + self.time_limit
        # Decrease time limit slightly
        self.time_limit = max(3.0, self.time_limit * 0.95)

    def update(self):
        if not self.active or self.state != "playing":
            return
            
        current_time = time.monotonic()
        
        if current_time >= self.question_timer:
            self.lives -= 1
            self.audio.play_sound("error")
            if self.lives > 0:
                self.audio.speak(self._("math_time_up", lives=self.lives), interrupt=True)
                self._next_question()
            else:
                self.state = "game_over"
                self.audio.speak(self._("math_gameover"), interrupt=True)
                self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                self.finish()

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_game()
            elif self.state == "playing":
                if event.key == pygame.K_RETURN:
                    self._check_answer()
                elif event.key == pygame.K_BACKSPACE:
                    if len(self.user_input) > 0:
                        self.user_input = self.user_input[:-1]
                        self.audio.play_sound("menu_move")
                elif event.unicode.isdigit() or (event.unicode == "-" and len(self.user_input) == 0):
                    self.user_input += event.unicode
                    # Speak the typed digit
                    self.audio.speak(event.unicode, interrupt=True)

    def _check_answer(self):
        if not self.user_input:
            return
            
        try:
            answer = int(self.user_input)
        except ValueError:
            return
            
        if answer == self.correct_answer:
            self.score += 1
            self.audio.play_sound("success")
            self._next_question()
        else:
            self.lives -= 1
            self.audio.play_sound("error")
            if self.lives > 0:
                self.audio.speak(self._("math_wrong", lives=self.lives), interrupt=True)
                self._next_question()
            else:
                self.state = "game_over"
                self.audio.speak(self._("math_gameover"), interrupt=True)
                self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                self.finish()
