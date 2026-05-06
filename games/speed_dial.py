import random
import pygame
import time
from games.base_game import BaseGame

class SpeedDial(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "speed_dial"
        self.instructions = self._("game_speed_dial_instructions")
        
        self.sequence = []
        self.current_pos = 0
        self.start_time = 0
        self.round = 1
        self.max_rounds = 5
        self.total_time = 0
        self.waiting_for_start = True

    def start(self):
        super().start()
        self.audio.speak(self._("instructions"), interrupt=False)
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _next_round(self):
        self.sequence = [random.randint(0, 9) for _ in range(3 + self.round)]
        self.current_pos = 0
        self.audio.speak(f"Runde {self.round}. Tippe: " + ", ".join(map(str, self.sequence)))
        self.start_time = time.time()
        self.waiting_for_start = False

    def handle_input(self, event):
        if self.waiting_for_start:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._next_round()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            # Prüfe Zahlentasten (Hauptreihe und Numpad)
            val = None
            if pygame.K_0 <= event.key <= pygame.K_9:
                val = event.key - pygame.K_0
            elif pygame.K_KP0 <= event.key <= pygame.K_KP9:
                val = event.key - pygame.K_KP0
            
            if val is not None:
                if val == self.sequence[self.current_pos]:
                    self.audio.play_sound("click")
                    self.current_pos += 1
                    if self.current_pos >= len(self.sequence):
                        duration = time.time() - self.start_time
                        self.total_time += duration
                        self.audio.play_sound("confirm")
                        self.audio.speak(f"Fertig! {duration:.1f} Sekunden.")
                        self.round += 1
                        if self.round > self.max_rounds:
                            # Score berechnen (großzügigerer Faktor)
                            self.score = int(max(100, 15000 - self.total_time * 100))
                            self.audio.speak(self._("final_score", score=self.score))
                            self.finish()
                        else:
                            self._next_round()
                else:
                    self.audio.play_sound("error")
                    self.audio.speak(self._("wrong"))
                    # Strafe: 1 Sekunde Zeitaufschlag
                    self.start_time -= 1
