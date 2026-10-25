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
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _next_round(self):
        self.sequence = [random.randint(0, 9) for _ in range(3 + self.round)]
        self.current_pos = 0
        self.audio.speak(f"Runde {self.round}. Tippe: " + ", ".join(map(str, self.sequence)))
        self.start_time = time.monotonic()
        self.waiting_for_start = False

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.finish()
            return
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
                        duration = time.monotonic() - self.start_time
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

    def draw(self, screen):
        # Schnellwahl-Telefon
        pygame.draw.rect(screen, (20, 25, 35), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (240, 180, 40), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        big_font = pygame.font.SysFont("Arial", 36, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"SCHNELLWAHL - RUNDE {self.round} / {self.max_rounds}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        if self.waiting_for_start:
            start_msg = font.render("Drücke EINGABE zum Starten der Runde", True, (100, 255, 150))
            screen.blit(start_msg, (400 - start_msg.get_width() // 2, 300))
        else:
            # Zeige die Ziffernfolge
            digits_str = " - ".join(str(d) for d in self.sequence)
            seq_surf = big_font.render(digits_str, True, (255, 255, 255))
            screen.blit(seq_surf, (400 - seq_surf.get_width() // 2, 260))
            
            # Bereits eingegebene Ziffern hervorheben
            entered = "".join(str(self.sequence[i]) for i in range(self.current_pos))
            entered_surf = font.render(f"Eingegeben: {entered}_", True, (100, 255, 120))
            screen.blit(entered_surf, (400 - entered_surf.get_width() // 2, 330))
            
            # Zeitleiste
            elapsed = time.monotonic() - self.start_time
            time_txt = small_font.render(f"Zeit: {elapsed:.2f} s", True, (200, 200, 220))
            screen.blit(time_txt, (400 - time_txt.get_width() // 2, 390))
            
        hint = small_font.render("Tippe die Ziffern (0-9) so schnell wie möglich ein", True, (190, 190, 210))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

