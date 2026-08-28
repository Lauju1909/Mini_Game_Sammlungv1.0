import pygame
import random
import time
from games.base_game import BaseGame

class AudioArcheryPro(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_archery_pro"
        self.instructions = self._("game_audio_archery_pro_instructions")
        
        self.score = 0
        self.round = 1
        self.max_rounds = 5
        self.pan = -1.0
        self.speed = 0.02
        self.direction = 1
        
        # Wind: offset von -0.4 bis 0.4. Positiv = drückt nach rechts
        self.wind_offset = 0.0 
        
        self.state = "starting"
        self.last_tick = time.monotonic()
        self.last_beep = 0
        self.last_wind_beep = 0
        self.start_timer = time.monotonic() + 2.0
        
        self.arrow_pos = 0.0

    def start(self):
        super().start()
        self.start_timer = time.monotonic() + 3.0

    def next_arrow(self):
        self.state = "aiming"
        self.pan = -1.0 if random.random() > 0.5 else 1.0
        self.direction = 1 if self.pan < 0 else -1
        
        # Speed wird mit den Runden schneller
        self.speed = 0.4 + (self.round * 0.1) # pro Sekunde
        
        # Wind ab Runde 2
        if self.round >= 2:
            self.wind_offset = random.uniform(-0.4, 0.4)
        else:
            self.wind_offset = 0.0
            
        self.last_tick = time.monotonic()
        self.audio.play_sound("click")

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.audio.speak(self._("start_go"), priority=2)
                self.next_arrow()
            return

        if self.state == "aiming":
            self.pan += self.direction * self.speed * dt
            if self.pan > 1.2 or self.pan < -1.2:
                self.direction *= -1

            # Ziel-Ping
            if now - self.last_beep > 0.15:
                self.audio.play_panned_sound("click", max(-1.0, min(1.0, self.pan)))
                self.last_beep = now
                
            # Wind-Sound (tiefes Rauschen/Brummen)
            if self.wind_offset != 0 and (now - self.last_wind_beep > 0.2):
                wind_pan = 1.0 if self.wind_offset > 0 else -1.0
                wind_vol = int(abs(self.wind_offset) * 150) # 0 bis 60
                self.audio.play_tone(frequency=150, duration_ms=180, volume=wind_vol, pan=wind_pan)
                self.last_wind_beep = now

        if self.state == "result":
            if now > self.start_timer: # start_timer wird für Pause missbraucht
                if self.round >= self.max_rounds:
                    self.finish()
                else:
                    self.round += 1
                    self.next_arrow()

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "aiming" and event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                self.shoot()

    def shoot(self):
        self.arrow_pos = self.pan
        
        # Effektive Position = wo das Ziel war + wie sehr der Wind den Pfeil verschiebt
        # Wenn Wind +0.3 (nach rechts), und Ziel auf -0.3 (links), fliegt Pfeil genau in die Mitte!
        effective_hit = self.pan + self.wind_offset
        diff = abs(effective_hit)
        
        if diff < 0.1:
            round_points = 200
            self.result_text = self._("hit_perfect")
            self.audio.play_sound("success")
        elif diff < 0.25:
            round_points = 100
            self.result_text = self._("hit_good")
            self.audio.play_sound("confirm")
        elif diff < 0.4:
            round_points = 50
            self.result_text = self._("hit_ok")
            self.audio.play_sound("click_001")
        else:
            round_points = 0
            self.result_text = self._("miss")
            self.audio.play_sound("error")
            
        self.score += round_points
        self.state = "result"
        self.start_timer = time.monotonic() + 2.5
        
        # Sag das Resultat
        self.audio.speak(f"{self.result_text}. {round_points} {self._('points')}.", priority=1)

    def draw(self, screen):
        screen.fill((20, 30, 40))
        
        center = (400, 300)
        colors = [(255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 215, 0)]
        for i, color in enumerate(colors):
            radius = 200 - i * 40
            pygame.draw.circle(screen, color, center, radius)
            pygame.draw.circle(screen, (100, 100, 100), center, radius, width=1)
            
        if self.state == "aiming":
            x = 400 + self.pan * 350
            pygame.draw.circle(screen, (0, 255, 0), (int(x), 300), 15)
            
            # Wind Anzeige
            if self.wind_offset != 0:
                wx = 400 + (1.0 if self.wind_offset > 0 else -1.0) * 350
                pygame.draw.circle(screen, (100, 100, 255), (int(wx), 100), 20)
                font_w = pygame.font.SysFont("Arial", 20)
                w_surf = font_w.render(f"Wind: {abs(self.wind_offset):.2f}", True, (255,255,255))
                screen.blit(w_surf, (wx - 40, 130))
        
        if self.state == "result":
            # Wo der Pfeil landete (ohne Wind)
            x_aim = 400 + self.arrow_pos * 350
            # Wo der Pfeil WIRKLICH landete (mit Wind)
            x_hit = 400 + (self.arrow_pos + self.wind_offset) * 350
            
            pygame.draw.line(screen, (200, 200, 200), (int(x_aim), 100), (int(x_aim), 500), 2)
            pygame.draw.line(screen, (255, 255, 0), (int(x_hit), 100), (int(x_hit), 500), 5)
            pygame.draw.circle(screen, (255, 0, 0), (int(x_hit), 300), 10)
            
            font = pygame.font.SysFont("Arial", 48, bold=True)
            text_surf = font.render(self.result_text, True, (255, 255, 255))
            screen.blit(text_surf, (400 - text_surf.get_width()//2, 520))

        font_small = pygame.font.SysFont("Arial", 24)
        status = font_small.render(f"Pfeil: {self.round}/{self.max_rounds} | Score: {self.score}", True, (255, 255, 255))
        screen.blit(status, (40, 40))
