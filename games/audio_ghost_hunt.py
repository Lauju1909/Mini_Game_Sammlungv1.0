import random
import pygame
import time
import math
from games.base_game import BaseGame

class AudioGhostHunt(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_ghost_hunt"
        self.instructions = self._("game_audio_ghost_hunt_instructions")
        
        self.score = 0
        self.ghosts_caught = 0
        self.target_ghosts = 4
        self.lives = 3
        
        self.state = "waiting_for_start" # waiting_for_start, hunting, caught_ghost
        self.player_angle = 0.0 # -1.0 to 1.0
        self.ghost_angle = 0.0 # -1.0 to 1.0
        self.ghost_speed = 0.2
        self.last_emf_tick = 0.0
        self.ghost_timer = 0.0
        self.round_start_time = 0.0

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _spawn_ghost(self):
        self.state = "hunting"
        self.player_angle = 0.0
        self.ghost_angle = random.choice([-0.7, -0.5, 0.5, 0.7])
        self.ghost_speed = random.choice([-0.15, 0.15]) * (1.0 + self.ghosts_caught * 0.2)
        self.round_start_time = time.monotonic()
        self.ghost_timer = time.monotonic() + 15.0 # 15s to catch each ghost
        self.audio.speak(self._("ghost_spotted", num=self.ghosts_caught + 1), interrupt=True)

    def update(self):
        if not self.active:
            return

        now = time.monotonic()

        if self.state == "hunting":
            # Geist bewegt sich langsam hin und her
            self.ghost_angle += self.ghost_speed * 0.016
            if self.ghost_angle > 0.9:
                self.ghost_angle = 0.9
                self.ghost_speed = -abs(self.ghost_speed)
            elif self.ghost_angle < -0.9:
                self.ghost_angle = -0.9
                self.ghost_speed = abs(self.ghost_speed)

            # EMF-Signal abhängig von der Winkeldifferenz
            angle_diff = abs(self.ghost_angle - self.player_angle)
            # Panning relativ zur Blickrichtung
            rel_pan = max(-1.0, min(1.0, self.ghost_angle - self.player_angle))
            
            interval = max(0.08, min(0.6, angle_diff * 0.5))
            if now - self.last_emf_tick > interval:
                self.last_emf_tick = now
                freq = int(700 - min(400, angle_diff * 350))
                vol = int(max(20, 100 - angle_diff * 60))
                self.audio.play_tone(frequency=freq, duration_ms=40, volume=vol, pan=rel_pan)
                
            # Zeit abgelaufen
            if now >= self.ghost_timer:
                self.lives -= 1
                self.audio.play_sound("error")
                if self.lives > 0:
                    self.audio.speak(self._("ghost_escaped", lives=self.lives), interrupt=True)
                    self._spawn_ghost()
                else:
                    self.finish()

    def handle_input(self, event):
        if not self.active:
            return

        super().handle_input(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return

            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._spawn_ghost()
            elif self.state == "hunting":
                if event.key == pygame.K_LEFT:
                    self.player_angle = max(-1.0, self.player_angle - 0.1)
                elif event.key == pygame.K_RIGHT:
                    self.player_angle = min(1.0, self.player_angle + 0.1)
                elif event.key == pygame.K_SPACE:
                    self._capture_ghost()

    def _capture_ghost(self):
        angle_diff = abs(self.ghost_angle - self.player_angle)
        if angle_diff <= 0.18:
            # Geist gefangen!
            self.ghosts_caught += 1
            points = int(max(50, 400 - angle_diff * 1000))
            self.score += points
            self.audio.play_sound("success")
            
            if self.ghosts_caught >= self.target_ghosts:
                self.audio.speak(self._("ghost_all_caught"), interrupt=True)
                self.finish()
            else:
                self.audio.speak(self._("ghost_captured", num=self.ghosts_caught), interrupt=True)
                self._spawn_ghost()
        else:
            # Daneben geschossen
            self.audio.play_sound("bump")
            self.audio.speak(self._("ghost_missed"), interrupt=True)

    def draw(self, screen):
        # Geisterjagd EMF-Radar
        pygame.draw.rect(screen, (15, 20, 35), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (100, 160, 255), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-GEISTERJAGD - GEISTER: {self.ghosts_caught} / {self.target_ghosts}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        info = small_font.render(f"Punkte: {self.score}   |   Leben: {self.lives}", True, (255, 215, 0))
        screen.blit(info, (400 - info.get_width() // 2, 195))
        
        # Halbkreis Radar / Scanner
        radar_center = (400, 400)
        for r in [60, 120, 180]:
            pygame.draw.arc(screen, (40, 70, 110), (radar_center[0] - r, radar_center[1] - r, r * 2, r * 2), math.pi, 2 * math.pi, 1)
            
        # Spieler-Peiler Strahl
        p_angle = math.pi + (self.player_angle + 1.0) * (math.pi / 2.0)
        px = radar_center[0] + int(math.cos(p_angle) * 170)
        py = radar_center[1] + int(math.sin(p_angle) * 170)
        pygame.draw.line(screen, (0, 220, 255), radar_center, (px, py), 3)
        
        # Geist Position (Wolkige Visualisierung)
        g_angle = math.pi + (self.ghost_angle + 1.0) * (math.pi / 2.0)
        gx = radar_center[0] + int(math.cos(g_angle) * 140)
        gy = radar_center[1] + int(math.sin(g_angle) * 140)
        pygame.draw.circle(screen, (180, 150, 255), (gx, gy), 18)
        pygame.draw.circle(screen, (255, 255, 255), (gx, gy), 8)
        
        hint = small_font.render("Pfeil LINKS / RECHTS = Gerät ausrichten  |  LEERTASTE = Fangstrahl abfeuern", True, (180, 210, 240))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))
