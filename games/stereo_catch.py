import pygame
import time
from games.base_game import BaseGame

class StereoCatch(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "stereo_catch"
        self.instructions = self._("game_stereo_catch_instructions")
        self.pan = -1.0
        self.direction = 1
        self.speed = 0.025
        self.last_tick = time.monotonic()
        self.last_beep = 0

    def update(self):
        if self.is_tutorial:
            self.update_tutorial()
            return

        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now
        
        # FPS-unabhängige Bewegung
        self.pan += self.direction * self.speed * (dt / 0.016)
        if self.pan >= 1.0:
            self.pan = 1.0
            self.direction = -1
            self.audio.play_sound("bump")
        elif self.pan <= -1.0:
            self.pan = -1.0
            self.direction = 1
            self.audio.play_sound("bump")
        
        if now - self.last_beep > 0.15:
            self.audio.play_panned_sound("blip", self.pan)
            self.last_beep = now

    def update_tutorial(self):
        if self.tutorial_step == 1:
            self.audio.speak(self._("tut_sc_1"), priority=1)
            self.tutorial_step = 2
        elif self.tutorial_step == 2:
            if not self.audio.is_speaking():
                self.audio.speak(self._("tut_sc_2"), priority=1)
                self.tutorial_step = 3
        elif self.tutorial_step == 3:
            if not self.audio.is_speaking():
                self.audio.speak(self._("tut_sc_3"), priority=1)
                self.tutorial_step = 4
        elif self.tutorial_step == 4:
            # Bewege die Münze im Tutorial
            now = time.monotonic()
            dt = now - self.last_tick
            self.last_tick = now
            self.pan += self.direction * (self.speed * 0.5) * (dt / 0.016) # Langsamer im Tutorial
            if self.pan >= 1.0:
                self.pan = 1.0
                self.direction = -1
                self.audio.play_sound("bump")
            elif self.pan <= -1.0:
                self.pan = -1.0
                self.direction = 1
                self.audio.play_sound("bump")
            if now - self.last_beep > 0.2:
                self.audio.play_panned_sound("blip", self.pan)
                self.last_beep = now
        elif self.tutorial_step == 5:
            if not self.audio.is_speaking():
                self.finish_tutorial()

    def handle_input(self, event):
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                accuracy = abs(self.pan)
                if accuracy < 0.08:
                    self.score = 1500
                    self.audio.play_sound("success")
                    self.audio.speak(self._("hit_perfect"))
                elif accuracy < 0.2:
                    self.score = 800
                    self.audio.play_sound("confirm")
                    self.audio.speak(self._("hit_good"))
                elif accuracy < 0.4:
                    self.score = 300
                    self.audio.play_sound("select")
                    self.audio.speak(self._("hit_ok"))
                else:
                    self.score = 0
                    self.audio.play_sound("error")
                    self.audio.speak(self._("miss"))
                
                self.audio.speak(self._("final_score", score=self.score))
                self.finish()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def handle_tutorial_input(self, event):
        super().handle_tutorial_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if self.tutorial_step == 4:
                    accuracy = abs(self.pan)
                    if accuracy < 0.25: # Großzügig im Tutorial
                        self.audio.play_sound("success")
                        self.audio.speak(self._("good"), priority=2)
                        self.tutorial_step = 5
                    else:
                        self.audio.speak(self._("miss"), priority=2)

    def draw(self, screen):
        # Hintergrund-Elemente
        pygame.draw.rect(screen, (30, 30, 50), (50, 250, 700, 100), border_radius=20)
        
        # Schiene
        pygame.draw.rect(screen, (60, 60, 90), (100, 290, 600, 20), border_radius=10)
        
        # Mitte-Markierung
        pygame.draw.rect(screen, (100, 100, 255), (395, 270, 10, 60), border_radius=5)
        
        # Trefferzonen Visualisierung
        # Perfect Zone (Gold)
        pygame.draw.rect(screen, (255, 215, 0), (400 - 0.08 * 300, 285, 0.16 * 300, 30), 2, border_radius=5)
        
        # Der bewegliche Indikator
        pos_x = 400 + (self.pan * 300)
        pygame.draw.circle(screen, (255, 255, 0), (int(pos_x), 300), 18)
        pygame.draw.circle(screen, (255, 255, 255), (int(pos_x) - 5, 295), 6) # Glanz
        
        # Text-Informationen
        font = pygame.font.SysFont("Arial", 32, bold=True)
        label = font.render("MÜNZE FANGEN!", True, (255, 255, 255))
        screen.blit(label, (400 - label.get_width()//2, 180))
        
        # Info-Text
        info_font = pygame.font.SysFont("Arial", 20)
        info_text = "Drücke ENTER in der Mitte"
        info_surf = info_font.render(info_text, True, (180, 180, 200))
        screen.blit(info_surf, (400 - info_surf.get_width()//2, 380))
