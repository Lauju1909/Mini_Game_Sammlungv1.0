import pygame
import random
import time
from games.base_game import BaseGame

class AudioMinesweeper(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_minesweeper"
        self.instructions = self._("game_audio_minesweeper_instructions")
        
        self.score = 0
        self.pos = 0
        self.mine_pos = 0
        self.on_mine_timer = 2.0
        self.last_click = 0
        
        self.state = "starting"
        self.start_timer = time.monotonic() + 2.0
        self.last_tick = time.monotonic()

    def start(self):
        super().start()
        self.spawn_mine()

    def spawn_mine(self):
        self.mine_pos = self.pos
        while abs(self.mine_pos - self.pos) < 3:
            self.mine_pos = random.randint(0, 20)
        # Weniger Zeit bei höherem Score
        self.on_mine_timer = max(0.5, 2.0 - (self.score * 0.1))

    def game_over(self):
        self.audio.play_sound("error")
        self.audio.speak(self._("minesweeper_boom"), priority=2)
        self.sleep(1.5)
        self.finish()

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.monotonic()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.audio.speak(self._("start_go"), priority=2)
            return

        if self.state == "playing":
            dist = abs(self.mine_pos - self.pos)
            
            if dist == 0:
                self.on_mine_timer -= dt
                if self.on_mine_timer <= 0:
                    self.game_over()
                elif now - self.last_click > 0.05:
                    self.last_click = now
                    # Extrem schnelles, helles Klicken als Warnung
                    self.audio.play_tone(frequency=1200, duration_ms=20, volume=80, pan=0.0)
            else:
                interval = max(0.1, dist * 0.15)
                if now - self.last_click > interval:
                    self.last_click = now
                    # Klicken: Panning zeigt Richtung der Mine
                    pan = 1.0 if self.mine_pos > self.pos else -1.0
                    self.audio.play_tone(frequency=400, duration_ms=30, volume=50, pan=pan)

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
                    if self.pos > 0:
                        self.pos -= 1
                        self.audio.play_sound("swipe")
                        self.last_click = 0 # Sofortiges Feedback
                elif event.key == pygame.K_RIGHT:
                    if self.pos < 20:
                        self.pos += 1
                        self.audio.play_sound("swipe")
                        self.last_click = 0 # Sofortiges Feedback
                elif event.key == pygame.K_SPACE:
                    dist = abs(self.mine_pos - self.pos)
                    if dist == 0:
                        self.score += 1
                        self.audio.play_sound("success")
                        self.audio.speak(str(self.score), priority=1)
                        self.spawn_mine()
                    else:
                        self.game_over()

    def draw(self, screen):
        screen.fill((20, 30, 20))
        
        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Entschärft: {self.score}", True, (255, 255, 255))
        pos_surf = font.render(f"Position: {self.pos}", True, (150, 255, 150))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(pos_surf, (20, 60))
        
        # Grid visualisieren
        for i in range(21):
            color = (100, 100, 100)
            if i == self.pos:
                color = (0, 255, 0)
            if i == self.mine_pos and self.state == "playing" and abs(self.mine_pos - self.pos) == 0:
                color = (255, 0, 0) # Zeige Mine nur wenn Spieler drauf steht
                
            pygame.draw.rect(screen, color, (50 + i * 30, 300, 20, 20))
