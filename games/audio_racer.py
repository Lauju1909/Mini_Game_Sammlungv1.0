import pygame
import random
import time
from games.base_game import BaseGame

class AudioRacer(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_racer"
        self.instructions = self._("game_audio_racer_instructions")
        
        self.score = 0
        self.lives = 3
        
        self.speed = 10.0
        self.rpm = 2000.0
        self.gear = 1
        self.lane = 0 # -1 (Links), 0 (Mitte), 1 (Rechts)
        
        self.obstacles = []
        self.spawn_timer = 2.0
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        self.last_tick = time.time()
        
        self.last_engine_beep = 0
        self.last_obs_beep = 0

    def start(self):
        super().start()
        self.start_timer = time.time() + 3.0

    def spawn_obstacle(self):
        # Spawn auf zufälliger Spur
        lane = random.choice([-1, 0, 1])
        self.obstacles.append({
            "distance": 100.0,
            "lane": lane
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
            return

        if self.state == "playing":
            # Auto beschleunigt langsam
            self.speed += 1.0 * dt
            # RPM steigt basierend auf Geschwindigkeit
            self.rpm += (self.speed * 15.0) * dt
            
            # Motor stottert, wenn zu hoch
            if self.rpm > 7500:
                self.rpm = 7500
                self.speed = max(10.0, self.speed - 5.0 * dt)
                if random.random() < 0.1:
                    self.audio.play_sound("bump") # Stottern
            
            # Strecke zurücklegen
            self.score += int(self.speed * dt)
            
            # Hindernisse spawnen
            self.spawn_timer -= (self.speed / 50.0) * dt
            if self.spawn_timer <= 0:
                self.spawn_obstacle()
                self.spawn_timer = max(0.5, 3.0 - (self.speed / 40.0))

            # Hindernisse bewegen
            for obs in self.obstacles[:]:
                obs["distance"] -= self.speed * 1.5 * dt
                
                if obs["distance"] <= 0:
                    if obs["lane"] == self.lane:
                        # Crash!
                        self.lives -= 1
                        self.audio.play_sound("error")
                        self.speed = max(10.0, self.speed - 30.0)
                        self.rpm = 2000.0
                        self.obstacles.remove(obs)
                        
                        if self.lives <= 0:
                            self.audio.speak(self._("racer_crash_gameover"), priority=2)
                            time.sleep(1)
                            self.finish()
                        else:
                            self.audio.speak(self._("lives_left", lives=self.lives), priority=1)
                    else:
                        # Ausgewichen
                        self.audio.play_sound("click")
                        self.obstacles.remove(obs)

            # Audio: Motorsound
            if now - self.last_engine_beep > 0.08:
                self.last_engine_beep = now
                freq = int(100 + (self.rpm / 6.0)) # 2000 RPM -> ~430 Hz, 7000 RPM -> ~1260 Hz
                # Motorgeräusch immer in der Mitte
                self.audio.play_tone(frequency=freq, duration_ms=60, volume=20, pan=0.0)

            # Audio: Gegenverkehr
            if self.obstacles and now - self.last_obs_beep > 0.15:
                self.last_obs_beep = now
                # Nächstes Hindernis vertonen
                closest = min(self.obstacles, key=lambda x: x["distance"])
                if closest["distance"] < 80.0:
                    pan = float(closest["lane"])
                    vol = int(max(10, 100 - closest["distance"]))
                    # Tiefer Ton für LKW/Gegenverkehr
                    self.audio.play_tone(frequency=250, duration_ms=100, volume=vol, pan=pan)

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
                # Spurwechsel
                if event.key == pygame.K_LEFT:
                    if self.lane > -1:
                        self.lane -= 1
                        self.audio.play_sound("swipe")
                        self.audio.play_tone(frequency=400, duration_ms=50, volume=40, pan=-1.0)
                elif event.key == pygame.K_RIGHT:
                    if self.lane < 1:
                        self.lane += 1
                        self.audio.play_sound("swipe")
                        self.audio.play_tone(frequency=400, duration_ms=50, volume=40, pan=1.0)
                        
                # Schalten
                elif event.key == pygame.K_UP:
                    if 6000 <= self.rpm <= 7200:
                        # Perfekt geschaltet
                        self.gear += 1
                        self.rpm = 3000.0
                        self.speed += 15.0
                        self.audio.play_sound("success")
                        self.score += 500
                    else:
                        # Schlecht geschaltet
                        self.rpm = 2500.0
                        self.speed = max(10.0, self.speed - 15.0)
                        self.audio.play_sound("bump")

    def draw(self, screen):
        screen.fill((30, 30, 30))
        
        # Straße
        pygame.draw.rect(screen, (50, 50, 50), (200, 0, 400, 600))
        pygame.draw.line(screen, (255, 255, 255), (333, 0), (333, 600), 2)
        pygame.draw.line(screen, (255, 255, 255), (466, 0), (466, 600), 2)
        
        # Spieler
        player_x = 400 + self.lane * 133
        pygame.draw.rect(screen, (0, 255, 0), (player_x - 20, 450, 40, 80))
        
        # Hindernisse
        for obs in self.obstacles:
            obs_x = 400 + obs["lane"] * 133
            obs_y = int(500 - (obs["distance"] / 100.0) * 500)
            pygame.draw.rect(screen, (255, 0, 0), (obs_x - 20, obs_y, 40, 80))
            
        font = pygame.font.SysFont("Arial", 28)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        speed_surf = font.render(f"Tempo: {int(self.speed)} km/h", True, (100, 255, 255))
        rpm_surf = font.render(f"RPM: {int(self.rpm)}", True, (255, 255, 100))
        gear_surf = font.render(f"Gang: {self.gear}", True, (255, 200, 200))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
        screen.blit(speed_surf, (20, 60))
        screen.blit(rpm_surf, (20, 100))
        screen.blit(gear_surf, (20, 140))
