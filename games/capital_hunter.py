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
