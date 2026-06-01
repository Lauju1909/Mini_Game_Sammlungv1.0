import pygame
import random
import time
from games.base_game import BaseGame

class AudioRunner(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_runner"
        self.instructions = self._("game_audio_runner_instructions")
        
        self.player_lane = 0 # -1: Links, 0: Mitte, 1: Rechts
        self.lives = 3
        self.score = 0
        
        self.obstacle_active = False
        self.obstacle_lane = 0
        self.obstacle_start_time = 0
        self.obstacle_duration = 2.0 # Sekunden bis Einschlag
        
        self.last_beep_time = 0
        self.beep_interval = 0.4
        
        self.state = "starting" # starting, playing, game_over
        self.start_timer = time.time()

    def start(self):
        super().start()
        self.start_timer = time.time() + 2.5 # Warten auf Instructions

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.audio.speak(self._("start_go"), priority=2)
                self.spawn_obstacle(now)
            return

        if self.state == "playing":
            if self.obstacle_active:
                elapsed = now - self.obstacle_start_time
                progress = elapsed / self.obstacle_duration
                
                # Wenn der Countdown abgelaufen ist
                if elapsed >= self.obstacle_duration:
                    self.check_collision()
                    self.obstacle_active = False
                    
                    if self.lives > 0:
                        # Nächstes Hindernis nach kurzer Pause
                        self.start_timer = now + 0.5
                        self.state = "waiting_next"
                else:
                    # Spiele warnendes Beepen, das schneller wird
                    current_interval = max(0.05, self.beep_interval * (1.0 - progress))
                    if now - self.last_beep_time > current_interval:
                        pan = float(self.obstacle_lane)
                        # Tonhöhe steigt leicht an
                        freq = 400 + (progress * 400)
                        self.audio.play_tone(freq, duration_ms=50, volume=80, pan=pan)
                        self.last_beep_time = now

        elif self.state == "waiting_next":
            if now > self.start_timer:
                self.state = "playing"
                self.spawn_obstacle(now)

    def spawn_obstacle(self, now):
        self.obstacle_active = True
        self.obstacle_start_time = now
        # Hindernis spawnt bevorzugt auf der Lane des Spielers oder einer benachbarten
        self.obstacle_lane = random.choice([-1, 0, 1])
        
        # Mache das Spiel über die Zeit schneller
        speed_factor = max(0.6, 1.0 - (self.score / 500.0))
        self.obstacle_duration = 2.0 * speed_factor
        self.beep_interval = 0.4 * speed_factor
        
        self.last_beep_time = now

    def check_collision(self):
        if self.player_lane == self.obstacle_lane:
            # Crash
            self.lives -= 1
            self.audio.play_sound("error") # Crash sound
            self.audio.speak(self._("crash_lives", lives=self.lives), priority=2)
            
            if self.lives <= 0:
                self.finish()
        else:
            # Erfolgreich ausgewichen
            self.score += 10
            self.audio.play_sound("success") # Whoosh sound
            # Nur jede 50 Punkte ansagen, um nicht zu spammen
            if self.score > 0 and self.score % 50 == 0:
                self.audio.speak(f"{self.score}", interrupt=False, priority=0)

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state in ["playing", "waiting_next"]:
                if event.key == pygame.K_LEFT:
                    if self.player_lane > -1:
                        self.player_lane -= 1
                        self.audio.play_panned_sound("click", -1.0)
                    else:
                        self.audio.play_panned_sound("bump", -1.0)
                
                elif event.key == pygame.K_RIGHT:
                    if self.player_lane < 1:
                        self.player_lane += 1
                        self.audio.play_panned_sound("click", 1.0)
                    else:
                        self.audio.play_panned_sound("bump", 1.0)

    def draw(self, screen):
        # Visuelle Repräsentation für Sehende
        screen.fill((20, 20, 30))
        
        # Lanes zeichnen
        pygame.draw.line(screen, (100, 100, 100), (250, 100), (250, 500), 2)
        pygame.draw.line(screen, (100, 100, 100), (550, 100), (550, 500), 2)
        
        # Spieler
        player_x = 400 + self.player_lane * 150
        pygame.draw.rect(screen, (0, 255, 0), (player_x - 30, 400, 60, 60))
        
        # Hindernis
        if self.obstacle_active:
            elapsed = time.time() - self.obstacle_start_time
            progress = elapsed / self.obstacle_duration
            obs_y = 100 + progress * 300
            obs_x = 400 + self.obstacle_lane * 150
            
            # Farbe wird rötlicher, je näher es kommt
            color_val = int(255 * progress)
            pygame.draw.rect(screen, (255, 255 - color_val, 255 - color_val), (obs_x - 40, obs_y - 20, 80, 40))

        # UI
        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
