import pygame
import time
import random
import math
from games.base_game import BaseGame

class BeatReaktor(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "beat_reaktor"
        self.instructions = self._("game_beat_reaktor_instructions")
        self.next_hit = time.time() + random.uniform(2, 5)
        self.waiting_for_hit = True
        self.hits = 0

    def update(self):
        if self.is_tutorial:
            self.update_tutorial()
            return

        if self.waiting_for_hit and time.time() >= self.next_hit:
            self.audio.play_sound("confirm")
            self.waiting_for_hit = False
            self.hit_time = time.time()

    def update_tutorial(self):
        if self.tutorial_step == 1:
            # Willkommenstext wurde schon von BaseGame.start_tutorial gesprochen
            self.audio.speak(self._("tut_br_1"), priority=1)
            self.tutorial_step = 2
        elif self.tutorial_step == 2:
            if not self.audio.is_speaking():
                self.audio.speak(self._("tut_br_2"), priority=1)
                self.tutorial_step = 3
        elif self.tutorial_step == 3:
            if not self.audio.is_speaking():
                self.audio.speak(self._("tut_br_3"), priority=1)
                self.tutorial_step = 4
                self.next_hit = time.time() + 2.0
                self.waiting_for_hit = True
        elif self.tutorial_step == 4:
            # Warte auf den Beat im Tutorial
            if self.waiting_for_hit and time.time() >= self.next_hit:
                self.audio.play_sound("confirm")
                self.waiting_for_hit = False
                self.hit_time = time.time()
        elif self.tutorial_step == 5:
            if not self.audio.is_speaking():
                self.finish_tutorial()

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if not self.waiting_for_hit:
                    reaction = time.time() - self.hit_time
                    if reaction < 0.6:
                        points = int((0.6 - reaction) * 2000)
                        self.score += points
                        self.audio.play_sound("success")
                        if reaction < 0.15:
                            self.audio.speak(self._("hit_perfect"))
                        else:
                            self.audio.speak(self._("hit"))
                        
                        self.hits += 1
                        if self.hits >= 5: 
                            self.audio.speak(self._("final_score", score=self.score))
                            self.finish()
                        else:
                            self.next_hit = time.time() + random.uniform(1.5, 3.5)
                            self.waiting_for_hit = True
                    else:
                        self.audio.speak(self._("too_late"))
                        self.next_hit = time.time() + random.uniform(1, 2)
                        self.waiting_for_hit = True
                else:
                    self.audio.speak(self._("too_early"))
                    self.score = max(0, self.score - 100)
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def handle_tutorial_input(self, event):
        super().handle_tutorial_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if self.tutorial_step == 4:
                    if not self.waiting_for_hit:
                        reaction = time.time() - self.hit_time
                        if reaction < 0.8: # Großzügiger im Tutorial
                            self.audio.play_sound("success")
                            self.audio.speak(self._("tut_br_hit"), priority=2)
                            self.tutorial_step = 5
                        else:
                            self.audio.speak(self._("tut_br_miss"), priority=2)
                            self.next_hit = time.time() + 2.0
                            self.waiting_for_hit = True
                    else:
                        self.audio.speak(self._("too_early"), priority=2)

    def draw(self, screen):
        # Hintergrund
        pygame.draw.rect(screen, (20, 20, 40), (100, 150, 600, 300), border_radius=25)
        
        # Titel
        font = pygame.font.SysFont("Arial", 40, bold=True)
        title = font.render("BEAT-REAKTOR", True, (255, 255, 255))
        # Leuchteffekt für Titel
        glow = int(math.sin(time.time() * 3) * 50) + 205
        title = font.render("BEAT-REAKTOR", True, (glow, glow, 255))
        screen.blit(title, (400 - title.get_width()//2, 80))
        
        # Visualisierung des Beats
        center = (400, 300)
        if not self.waiting_for_hit:
            # Der Moment des Treffers! Großes leuchtendes Becken
            elapsed = time.time() - self.hit_time
            size = int(100 + (1.0 - elapsed/0.6) * 50) if elapsed < 0.6 else 100
            color = (255, 255, 0) if elapsed < 0.6 else (100, 100, 0)
            pygame.draw.circle(screen, color, center, size)
            pygame.draw.circle(screen, (255, 255, 255), center, size - 10, 5)
        else:
            # Warten...
            pygame.draw.circle(screen, (50, 50, 70), center, 80)
            # Pulsierender Ring
            pulse = int(math.sin(time.time() * 5) * 10) + 10
            pygame.draw.circle(screen, (80, 80, 100), center, 80 + pulse, 2)

        # Fortschritt
        font_small = pygame.font.SysFont("Arial", 24)
        progress = f"Treffer: {self.hits} / 5"
        prog_surf = font_small.render(progress, True, (200, 200, 200))
        screen.blit(prog_surf, (400 - prog_surf.get_width()//2, 410))
        
        # Aktueller Score
        score_surf = font_small.render(f"Punkte: {self.score}", True, (255, 255, 255))
        screen.blit(score_surf, (100, 100))
