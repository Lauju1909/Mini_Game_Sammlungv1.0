import random
import pygame
from games.base_game import BaseGame

class SoundQuiz(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "sound_quiz"
        self.instructions = self._("game_sound_quiz_instructions")
        self.questions = [
            {"sound": "click", "options": [self._("sq_mouse"), self._("sq_car"), self._("sq_piano")], "correct": 0},
            {"sound": "confirm", "options": [self._("sq_bell"), self._("sq_bird"), self._("sq_thunder")], "correct": 0},
            {"sound": "error", "options": [self._("sq_dog"), self._("sq_alarm"), self._("sq_water")], "correct": 1}
        ]
        self.idx = 0
        self._ask()

    def _ask(self):
        q = self.questions[self.idx]
        self.audio.play_sound(q["sound"])
        self.audio.speak(self._("sound_quiz_question", opt1=q['options'][0], opt2=q['options'][1], opt3=q['options'][2]))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            q = self.questions[self.idx]
            if event.key == pygame.K_1: self._check(0)
            elif event.key == pygame.K_2: self._check(1)
            elif event.key == pygame.K_3: self._check(2)
            elif event.key == pygame.K_ESCAPE: self.finish()

    def _check(self, choice):
        if choice == self.questions[self.idx]["correct"]:
            self.audio.play_sound("success")
            self.score += 100
        else:
            self.audio.play_sound("error")
        
        self.idx += 1
        if self.idx >= len(self.questions): self.finish()
        else: self._ask()
