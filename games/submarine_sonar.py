import pygame
import random
import time
import math
from games.base_game import BaseGame

class SubmarineSonar(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "submarine_sonar"
        self.instructions = self._("game_submarine_sonar_instructions")
        
        self.player_angle = 0
        self.lives = 3
        self.score = 0
        
        self.enemies = [] # Liste von dicts: {"angle": int, "distance": int}
        
        self.last_ping_time = 0
        self.ping_interval = 1.2
        self.spawn_timer = time.time() + 2.0
        self.time_between_spawns = 5.0
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        
        self.torpedo_reload_time = 1.0
        self.last_fire_time = 0

    def start(self):
        super().start()
        self.start_timer = time.time() + 3.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.audio.speak(self._("start_go"), priority=2)
            return

        if self.state == "playing":
            # Feinde spawnen
            if now > self.spawn_timer:
                self.spawn_enemy()
                # Spawn-Zeit verringern für mehr Schwierigkeit
                self.time_between_spawns = max(2.0, self.time_between_spawns * 0.95)
                self.spawn_timer = now + self.time_between_spawns

            # Pings senden
            if now - self.last_ping_time > self.ping_interval:
                self.last_ping_time = now
                self.ping_enemies()

    def spawn_enemy(self):
        # Feind spawnt in einem Vielfachen von 15 Grad
        angle = random.randint(0, 23) * 15
        self.enemies.append({"angle": angle, "distance": 100})

    def ping_enemies(self):
        # Gehe Feinde durch und spiele Ping-Töne
        for enemy in self.enemies[:]:
            enemy["distance"] -= 5
            if enemy["distance"] <= 0:
                # Getroffen!
                self.enemies.remove(enemy)
                self.lives -= 1
                self.audio.play_sound("error")
                self.audio.speak(self._("submarine_hit", lives=self.lives), priority=2)
                if self.lives <= 0:
                    self.finish()
                continue

            # Berechne relativen Winkel
            rel_angle = (enemy["angle"] - self.player_angle) % 360
            
            # Pan (-1.0 links bis 1.0 rechts) basierend auf Sinus
            pan = math.sin(math.radians(rel_angle))
            
            # Tonhöhe basierend auf Vorne/Hinten (Kosinus)
            front = math.cos(math.radians(rel_angle)) >= -0.1 # Ein bisschen Toleranz
            freq = 600 if front else 300
            
            # Lautstärke basierend auf Entfernung
            vol_percent = max(10, 100 - enemy["distance"])
            
            # Spiele Ton
            self.audio.play_tone(frequency=freq, duration_ms=150, volume=vol_percent, pan=pan)
            # Kurze Pause zwischen mehreren Feinden
            self.sleep(0.05)

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "playing":
                if event.key == pygame.K_LEFT:
                    self.player_angle = (self.player_angle - 15) % 360
                    self.audio.play_panned_sound("click", -0.5)
                
                elif event.key == pygame.K_RIGHT:
                    self.player_angle = (self.player_angle + 15) % 360
                    self.audio.play_panned_sound("click", 0.5)
                    
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    now = time.time()
                    if now - self.last_fire_time > self.torpedo_reload_time:
                        self.fire_torpedo()
                        self.last_fire_time = now
                    else:
                        self.audio.play_sound("bump") # Nachladen

    def fire_torpedo(self):
        self.audio.play_sound("confirm") # Torpedo Abschuss Sound
        
        hit = False
        for enemy in self.enemies[:]:
            rel_angle = (enemy["angle"] - self.player_angle) % 360
            # Ein Treffer ist innerhalb von +/- 15 Grad (also 0, 15, 345)
            if rel_angle <= 15 or rel_angle >= 345:
                hit = True
                self.enemies.remove(enemy)
                points = 100
                self.score += points
                self.audio.play_sound("success")
                self.audio.speak(self._("submarine_destroyed"), priority=1)
                break
                
        if not hit:
            self.audio.play_sound("bump")
            self.audio.speak(self._("miss"), priority=1)

    def draw(self, screen):
        screen.fill((10, 20, 30))
        
        # Radar visuell
        center = (400, 300)
        pygame.draw.circle(screen, (0, 100, 0), center, 200, 2)
        pygame.draw.circle(screen, (0, 100, 0), center, 100, 1)
        
        # Eigene Ausrichtung
        end_pos = (
            center[0] + 200 * math.sin(math.radians(self.player_angle)),
            center[1] - 200 * math.cos(math.radians(self.player_angle))
        )
        pygame.draw.line(screen, (0, 255, 0), center, end_pos, 3)
        
        # Feinde
        for enemy in self.enemies:
            r = (enemy["distance"] / 100.0) * 200
            a = enemy["angle"]
            ex = center[0] + r * math.sin(math.radians(a))
            ey = center[1] - r * math.cos(math.radians(a))
            pygame.draw.circle(screen, (255, 0, 0), (int(ex), int(ey)), 8)

        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
