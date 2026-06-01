import pygame
import random
import time
from games.base_game import BaseGame

class AudioFactory(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_factory"
        self.instructions = self._("game_audio_factory_instructions")
        
        self.lives = 3
        self.score = 0
        self.items = []
        
        self.last_spawn_time = 0
        self.spawn_interval = 3.0
        self.base_speed = 0.4 # pan units per second (takes ~5s from -1 to 1)
        
        self.last_beep_time = 0
        self.beep_interval = 0.2
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0

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
            # Schwierigkeit anpassen
            speed_multiplier = min(3.0, 1.0 + (self.score / 500.0))
            current_spawn_interval = max(0.8, self.spawn_interval / speed_multiplier)
            
            # Spawnen
            if now - self.last_spawn_time > current_spawn_interval:
                self.last_spawn_time = now
                self.spawn_item(speed_multiplier)

            # Bewegen und Aussortieren
            dt = 0.016 # Approximierte Frame-Zeit
            for item in self.items[:]:
                item["pan"] += item["speed"] * dt
                
                # Wenn es das Ende erreicht
                if item["pan"] > 1.2:
                    if item["type"] == "broken":
                        # Defektes Teil durchgelassen -> Fehler
                        self.lives -= 1
                        self.audio.play_sound("error")
                        self.audio.speak(self._("factory_missed_broken", lives=self.lives), priority=2)
                        if self.lives <= 0:
                            self.finish()
                    else:
                        # Gutes Teil ist erfolgreich durch
                        self.score += 20
                        # Nur ein weicher Ton, um nicht zu übertönen
                        self.audio.play_sound("click_001")
                    
                    if item in self.items:
                        self.items.remove(item)

            # Beepen
            if now - self.last_beep_time > self.beep_interval:
                self.last_beep_time = now
                for item in self.items:
                    # Gutes Teil = hoher Ton (600Hz), Defektes Teil = tiefer brummiger Ton (250Hz)
                    freq = 600 if item["type"] == "good" else 250
                    self.audio.play_tone(frequency=freq, duration_ms=80, volume=70, pan=max(-1.0, min(1.0, item["pan"])))

    def spawn_item(self, speed_multiplier):
        # 30% Chance auf defektes Teil
        item_type = "broken" if random.random() < 0.3 else "good"
        speed = self.base_speed * speed_multiplier
        self.items.append({
            "pan": -1.2,
            "type": item_type,
            "speed": speed
        })

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "playing" and event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                self.grab_item()

    def grab_item(self):
        # Finde ein Item im Greifbereich (-0.2 bis 0.2)
        grabbed = None
        for item in self.items:
            if -0.25 <= item["pan"] <= 0.25:
                grabbed = item
                break
        
        if grabbed:
            self.items.remove(grabbed)
            if grabbed["type"] == "broken":
                # Korrekt aussortiert
                self.score += 100
                self.audio.play_sound("success")
                self.audio.speak(self._("factory_sorted"), priority=0)
            else:
                # Gutes Teil fälschlicherweise aussortiert
                self.lives -= 1
                self.audio.play_sound("bump")
                self.audio.speak(self._("factory_wrong_sort", lives=self.lives), priority=2)
                if self.lives <= 0:
                    self.finish()
        else:
            # Ins Leere gegriffen
            self.audio.play_sound("click")

    def draw(self, screen):
        screen.fill((30, 30, 30))
        
        # Fließband
        pygame.draw.rect(screen, (80, 80, 80), (50, 250, 700, 100))
        
        # Greifbereich in der Mitte
        pygame.draw.rect(screen, (255, 255, 0), (350, 240, 100, 120), 3)
        
        # Items
        for item in self.items:
            # pan geht von -1.2 bis 1.2
            # mappen auf 50 bis 750
            x = 400 + (item["pan"] * 350)
            color = (0, 255, 0) if item["type"] == "good" else (255, 0, 0)
            pygame.draw.circle(screen, color, (int(x), 300), 30)

        # UI
        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
