import pygame
import random
import time
from games.base_game import BaseGame

class AudioDefense(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_defense"
        self.instructions = self._("game_audio_defense_instructions")
        
        self.score = 0
        self.lives = 3
        
        self.enemies = []
        self.base_speed = 15.0
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        
        self.last_tick = time.time()
        self.state = "starting"
        self.start_timer = time.time() + 2.0

    def start(self):
        super().start()
        self.start_timer = time.time() + 3.0

    def spawn_enemy(self):
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]
        d = random.choice(directions)
        
        # Sicherstellen, dass nicht zwei Gegner fast gleichzeitig kommen
        self.enemies.append({
            "direction": d,
            "distance": 100.0,
            "last_beep": 0
        })

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.audio.speak(self._("start_go"), priority=2)
                self.spawn_enemy()
            return

        if self.state == "playing":
            # Spawn new enemies
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_enemy()
                self.spawn_interval = max(0.8, self.spawn_interval * 0.95)
                self.spawn_timer = self.spawn_interval

            # Update enemies
            for e in self.enemies[:]:
                e["distance"] -= self.base_speed * dt
                
                # Check if hit player
                if e["distance"] <= 0:
                    self.take_damage()
                    self.enemies.remove(e)
                    continue
                
                # Play audio
                beep_interval = max(0.1, (e["distance"] / 100.0) * 0.5)
                if now - e["last_beep"] > beep_interval:
                    e["last_beep"] = now
                    
                    vol = int(max(10, 100 - e["distance"]))
                    pan = 0.0
                    freq = 500
                    
                    if e["direction"] == "LEFT":
                        pan = -1.0
                    elif e["direction"] == "RIGHT":
                        pan = 1.0
                    elif e["direction"] == "UP":
                        freq = 800
                    elif e["direction"] == "DOWN":
                        freq = 300
                        
                    self.audio.play_tone(frequency=freq, duration_ms=50, volume=vol, pan=pan)

    def take_damage(self):
        self.lives -= 1
        self.audio.play_sound("error")
        if self.lives <= 0:
            self.finish()
        else:
            self.audio.speak(self._("lives_left", lives=self.lives), priority=2)
            # Gegner etwas zurücksetzen für kurze Verschnaufpause
            for e in self.enemies:
                e["distance"] += 20.0

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
                direction_map = {
                    pygame.K_UP: "UP",
                    pygame.K_DOWN: "DOWN",
                    pygame.K_LEFT: "LEFT",
                    pygame.K_RIGHT: "RIGHT"
                }
                
                if event.key in direction_map:
                    target_dir = direction_map[event.key]
                    
                    # Finde den nächsten Gegner in dieser Richtung
                    target_enemy = None
                    min_dist = 999.0
                    for e in self.enemies:
                        if e["direction"] == target_dir and e["distance"] < min_dist:
                            min_dist = e["distance"]
                            target_enemy = e
                            
                    if target_enemy:
                        if target_enemy["distance"] <= 25.0:
                            # Perfekter Treffer
                            self.audio.play_sound("success")
                            self.score += int(30 - target_enemy["distance"]) * 10
                            self.enemies.remove(target_enemy)
                            self.base_speed += 0.5
                        else:
                            # Zu früh gedrückt! (Panik)
                            self.take_damage()
                            self.enemies.remove(target_enemy) # Gegner trotzdem weg, sonst wird man doppelt bestraft
                    else:
                        # Falsche Richtung gedrückt (kein Gegner da)
                        self.take_damage()

    def draw(self, screen):
        screen.fill((10, 20, 10))
        
        # Spieler in der Mitte
        center = (400, 300)
        pygame.draw.circle(screen, (0, 255, 0), center, 25)
        pygame.draw.circle(screen, (255, 0, 0), center, 50, width=1) # Hit-Zone
        
        # Gegner zeichnen
        for e in self.enemies:
            d = e["distance"]
            if e["direction"] == "UP":
                pos = (400, int(300 - d * 2.5))
            elif e["direction"] == "DOWN":
                pos = (400, int(300 + d * 2.5))
            elif e["direction"] == "LEFT":
                pos = (int(400 - d * 2.5), 300)
            elif e["direction"] == "RIGHT":
                pos = (int(400 + d * 2.5), 300)
                
            size = int(max(5, 20 - (d / 100.0) * 15))
            pygame.draw.circle(screen, (255, 100, 100), pos, size)

        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
