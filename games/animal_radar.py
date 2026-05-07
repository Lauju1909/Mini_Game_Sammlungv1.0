import pygame
import random
import math
from games.base_game import BaseGame

class AnimalRadar(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "animal_radar"
        self.instructions = self._("game_animal_radar_instructions")
        self.target_angle = random.uniform(0, 360)
        self.player_angle = 180
        self.animals = [
            {"id": "sq_bird", "sound": "pluck_001"},
            {"id": "sq_dog", "sound": "bong_001"},
            {"id": "sq_mouse", "sound": "tick_001"}
        ]
        self.target_animal = random.choice(self.animals)
        self.last_beep = 0
        self.beep_interval = 1000

    def start(self):
        super().start()
        self.audio.speak(self._("welcome") + " " + self._("game_animal_radar"), interrupt=False)
        self.audio.speak(self._("find_the_sound") + " " + self._(self.target_animal["id"]), interrupt=False)

    def handle_input(self, event):
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.player_angle = (self.player_angle - 10) % 360
                self.audio.play_sound("click")
            elif event.key == pygame.K_RIGHT:
                self.player_angle = (self.player_angle + 10) % 360
                self.audio.play_sound("click")
            elif event.key == pygame.K_RETURN:
                self.check_target()

    def check_target(self):
        diff = abs(self.player_angle - self.target_angle)
        if diff > 180:
            diff = 360 - diff
        
        if diff < 15:
            self.score = 100 - int(diff)
            self.audio.play_sound("success")
            self.audio.speak(self._("hit_perfect"))
            self.finish()
        else:
            self.audio.play_sound("error")
            self.audio.speak(self._("miss"))
            self.finish()

    def update(self):
        now = pygame.time.get_ticks()
        
        # Berechne Winkel-Differenz
        diff = self.target_angle - self.player_angle
        if diff > 180: diff -= 360
        if diff < -180: diff += 360
        
        # Je näher am Ziel, desto schneller der Beep
        abs_diff = abs(diff)
        self.beep_interval = max(100, min(1000, int(abs_diff * 5)))
        
        if now - self.last_beep > self.beep_interval:
            # Pan von -1.0 (links) bis 1.0 (rechts)
            pan = math.sin(math.radians(diff))
            
            # Lautstärke basierend auf Ausrichtung (optional)
            # Wir nutzen den Sound des Ziel-Tiers
            self.audio.play_panned_sound(self.target_animal["sound"], pan)
            self.last_beep = now

    def draw(self, screen):
        # Zeichne einen Kompass oder Radar
        center = (400, 300)
        pygame.draw.circle(screen, (0, 50, 0), center, 200)
        pygame.draw.circle(screen, (0, 255, 0), center, 200, 2)
        
        # Spieler-Blickrichtung
        p_rad = math.radians(self.player_angle - 90)
        p_end = (center[0] + math.cos(p_rad) * 180, center[1] + math.sin(p_rad) * 180)
        pygame.draw.line(screen, (255, 255, 255), center, p_end, 3)
        
        # Ziel (nur für Sehende, vielleicht etwas versteckt)
        t_rad = math.radians(self.target_angle - 90)
        t_pos = (center[0] + math.cos(t_rad) * 150, center[1] + math.sin(t_rad) * 150)
        pygame.draw.circle(screen, (255, 0, 0, 50), t_pos, 10)
