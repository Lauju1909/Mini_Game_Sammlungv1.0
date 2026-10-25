import math
import random
import pygame
import time
from games.base_game import BaseGame

class SpaceFlight(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "space_flight"
        self.instructions = self._("game_space_flight_instructions")
        self.next_asteroid = time.monotonic() + 2
        self.asteroids_passed = 0
        self.waiting_for_dodge = False

    def update(self):
        now = time.monotonic()
        if self.waiting_for_dodge:
            if now > self.hit_deadline:
                self._fail()
        elif now > self.next_asteroid:
            self.side = random.choice(["links", "rechts"])
            pan = -1.0 if self.side == "links" else 1.0
            self.audio.play_panned_sound("warn", pan)
            # Nutze lokalisierte Richtungsansage
            self.audio.speak(self._("key_left" if self.side == "links" else "key_right"))
            self.hit_deadline = now + 1.5
            self.next_asteroid = now + 3
            self.waiting_for_dodge = True

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            if not hasattr(self, 'waiting_for_dodge') or not self.waiting_for_dodge:
                return # Ignoriere Eingaben wenn kein Asteroid da ist
            
            if event.key == pygame.K_LEFT:
                if hasattr(self, 'side') and self.side == "rechts":
                    self._success()
                else: self._fail()
            elif event.key == pygame.K_RIGHT:
                if hasattr(self, 'side') and self.side == "links":
                    self._success()
                else: self._fail()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _success(self):
        self.waiting_for_dodge = False
        self.audio.play_sound("confirm")
        self.score += 50
        self.asteroids_passed += 1
        if self.asteroids_passed >= 5: self.finish()

    def _fail(self):
        self.audio.play_sound("error")
        self.audio.speak(self._("hit_obstacle"))
        self.finish()

    def draw(self, screen):
        # Raumschiff-Cockpit
        pygame.draw.rect(screen, (10, 10, 25), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (120, 180, 255), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"WELTRAUMFLUG - HINDERNISSE: {self.asteroids_passed} / 5", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        # Warp-Sterne
        now = time.monotonic()
        for i in range(12):
            star_x = int(400 + math.cos(i * 0.5 + now * 2) * (50 + i * 18))
            star_y = int(320 + math.sin(i * 0.5 + now * 2) * (30 + i * 12))
            pygame.draw.circle(screen, (200, 220, 255), (star_x, star_y), 2)
            
        # Raumschiff-Fadenkreuz
        pygame.draw.circle(screen, (100, 200, 255), (400, 330), 20, width=2)
        
        # Warnung vor Asteroid
        if self.waiting_for_dodge and hasattr(self, 'side'):
            ax = 220 if self.side == "links" else 580
            pygame.draw.circle(screen, (255, 80, 50), (ax, 330), 32)
            warn_txt = font.render("ACHTUNG! ASTEROID!", True, (255, 70, 70))
            screen.blit(warn_txt, (400 - warn_txt.get_width() // 2, 240))
            dodge_dir = "RECHTS" if self.side == "links" else "LINKS"
            sub_txt = small_font.render(f"Weiche nach {dodge_dir} aus! (Pfeil {dodge_dir})", True, (255, 220, 100))
            screen.blit(sub_txt, (400 - sub_txt.get_width() // 2, 400))
            
        hint = small_font.render("Pfeil LINKS / RECHTS zum Ausweichen in die freie Richtung", True, (180, 190, 220))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

