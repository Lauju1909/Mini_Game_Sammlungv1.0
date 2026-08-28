import pygame
import random
import time
import math
from games.base_game import BaseGame

class AudioSpaceship(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_spaceship"
        self.instructions = self._("game_audio_spaceship_instructions")
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.enemies_defeated = 0
        
        self.player_angle = 0.0
        self.enemies = []
        
        self.state = "starting"
        self.start_timer = time.monotonic() + 2.0
        self.last_tick = time.monotonic()
        self.next_spawn = 0

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.start_timer = time.monotonic() + 2.0

    def spawn_enemy(self, now):
        t = "fighter" if random.random() > 0.4 else "bomber"
        speed = random.uniform(12.0, 18.0) + (self.level * 2) if t == "fighter" else random.uniform(5.0, 8.0) + self.level
        
        self.enemies.append({
            "type": t,
            "angle": random.uniform(0, 360),
            "distance": 100.0,
            "speed": speed,
            "last_buzz": 0,
            "buzz_delay": 0.1 if t == "fighter" else 0.4
        })
        
        spawn_interval = max(1.0, 4.0 - (self.level * 0.2))
        self.next_spawn = now + spawn_interval + random.uniform(-0.5, 0.5)

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.next_spawn = now + 1.0
            return

        if self.state == "playing":
            if now > self.next_spawn:
                self.spawn_enemy(now)
                
            for enemy in list(self.enemies):
                enemy["distance"] -= enemy["speed"] * dt
                
                # Feind hat uns erreicht
                if enemy["distance"] <= 0:
                    self.audio.play_sound("error")
                    self.audio.play_tone(frequency=100, duration_ms=500, volume=100) # Crash
                    self.lives -= 1
                    self.enemies.remove(enemy)
                    
                    if self.lives <= 0:
                        self.audio.speak(self._("spaceship_gameover"), priority=2)
                        self.sleep(2)
                        self.finish()
                        return
                    else:
                        self.audio.speak(self._("lives_left", lives=self.lives), priority=1)
                    continue

                # Audio-Feedback für Feinde
                if now - enemy["last_buzz"] > enemy["buzz_delay"]:
                    enemy["last_buzz"] = now
                    
                    rel_angle = (enemy["angle"] - self.player_angle) % 360
                    if rel_angle > 180: rel_angle -= 360
                    
                    pan = math.sin(math.radians(rel_angle))
                    front_back = math.cos(math.radians(rel_angle)) # 1.0 = Vorne, -1.0 = Hinten
                    
                    vol = int(max(10, 100 - enemy["distance"]))
                    
                    if enemy["type"] == "fighter":
                        freq = 800 + (front_back * 300) # Hell und schnell
                        self.audio.play_tone(frequency=int(freq), duration_ms=40, volume=vol, pan=pan)
                    else:
                        freq = 200 + (front_back * 50) # Tief und bedrohlich
                        self.audio.play_tone(frequency=int(freq), duration_ms=150, volume=vol, pan=pan)

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
                # Drehen
                if event.key == pygame.K_LEFT:
                    self.player_angle -= 15.0
                    self.audio.play_tone(frequency=400, duration_ms=20, volume=30)
                elif event.key == pygame.K_RIGHT:
                    self.player_angle += 15.0
                    self.audio.play_tone(frequency=400, duration_ms=20, volume=30)
                    
                # Schießen
                elif event.key in [pygame.K_SPACE, pygame.K_m]:
                    weapon = "laser" if event.key == pygame.K_SPACE else "missile"
                    
                    # Schuss-Sound
                    if weapon == "laser":
                        self.audio.play_tone(frequency=1200, duration_ms=50, volume=50) # Pew
                    else:
                        self.audio.play_tone(frequency=150, duration_ms=200, volume=70) # Whoosh
                        
                    hit = False
                    for enemy in list(self.enemies):
                        rel_angle = (enemy["angle"] - self.player_angle) % 360
                        if rel_angle > 180: rel_angle -= 360
                        
                        # Im Visier? (+/- 20 Grad Vorne)
                        if abs(rel_angle) <= 20:
                            if (weapon == "laser" and enemy["type"] == "fighter") or (weapon == "missile" and enemy["type"] == "bomber"):
                                # Treffer!
                                self.audio.play_sound("success" if weapon == "laser" else "confirm")
                                self.audio.play_sound("bump") # Explosion
                                self.enemies.remove(enemy)
                                self.score += 10 if weapon == "laser" else 20
                                self.enemies_defeated += 1
                                hit = True
                                
                                # Level Up
                                if self.enemies_defeated % 10 == 0:
                                    self.level += 1
                                    self.audio.speak(self._("spaceship_level_up", level=self.level), priority=2)
                                break
                                
                    if not hit:
                        self.audio.play_sound("swipe") # Daneben

    def draw(self, screen):
        screen.fill((10, 10, 30))
        
        font = pygame.font.SysFont("Arial", 28)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Schilde: {self.lives}", True, (255, 100, 100))
        level_surf = font.render(f"Welle: {self.level}", True, (100, 255, 100))
        angle_surf = font.render(f"Richtung: {int(self.player_angle % 360)}°", True, (200, 200, 255))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
        screen.blit(level_surf, (20, 60))
        screen.blit(angle_surf, (20, 100))
        
        # Radar visuell
        center_x, center_y = 400, 350
        pygame.draw.circle(screen, (0, 100, 0), (center_x, center_y), 200, 2)
        
        # Spieler-Richtung (Vorne ist UP, also -90 grad für pygame)
        p_rad = math.radians(self.player_angle - 90)
        end_x = center_x + math.cos(p_rad) * 200
        end_y = center_y + math.sin(p_rad) * 200
        pygame.draw.line(screen, (0, 255, 0), (center_x, center_y), (end_x, end_y), 3)
        pygame.draw.circle(screen, (0, 255, 0), (center_x, center_y), 10)
        
        # Feinde
        for enemy in self.enemies:
            # Winkel absolut auf dem Bildschirm
            e_rad = math.radians(enemy["angle"] - 90)
            dist_px = enemy["distance"] * 2
            ex = center_x + math.cos(e_rad) * dist_px
            ey = center_y + math.sin(e_rad) * dist_px
            
            color = (255, 100, 100) if enemy["type"] == "fighter" else (150, 0, 0)
            size = 5 if enemy["type"] == "fighter" else 15
            pygame.draw.circle(screen, color, (int(ex), int(ey)), size)
