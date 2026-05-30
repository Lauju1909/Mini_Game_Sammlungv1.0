import pygame
import random
import math
from games.base_game import BaseGame

class BeatMatcher(BaseGame):
    def __init__(self, audio_manager, highscore_manager, settings_manager, player_name):
        super().__init__(audio_manager, highscore_manager, settings_manager, player_name)
        self.game_id = "beat_matcher"
        self.instructions = self._("game_beat_matcher_instructions")
        
        self.bpm = random.randint(80, 140)
        self.beat_interval = 60000 / self.bpm # ms
        self.last_beat_time = 0
        
        self.hits = 0
        self.max_hits = 16
        self.accuracy_sum = 0
        self.state = "playing"

    def start(self):
        super().start()
        self.audio.speak(self._("hit_the_beat"))
        self.last_beat_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_beat_time > self.beat_interval:
            self.audio.play_sound("tick_001")
            self.last_beat_time = now

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                now = pygame.time.get_ticks()
                diff = abs(now - self.last_beat_time)
                # If hit is closer to the NEXT beat
                if abs(now - (self.last_beat_time + self.beat_interval)) < diff:
                    diff = abs(now - (self.last_beat_time + self.beat_interval))
                
                accuracy = max(0, 100 - (diff / (self.beat_interval / 2) * 100))
                self.score += int(accuracy)
                self.accuracy_sum += accuracy
                self.hits += 1
                
                if accuracy > 80:
                    self.audio.play_sound("success")
                else:
                    self.audio.play_sound("click")
                    
                if self.hits >= self.max_hits:
                    self.finish()

    def draw(self, screen):
        screen.fill((20, 20, 30))
        font = pygame.font.SysFont("Outfit, Arial", 40)
        title = font.render(self._("game_beat_matcher"), True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width()//2, 50))
        
        # Beat visualization
        now = pygame.time.get_ticks()
        progress = (now - self.last_beat_time) / self.beat_interval
        
        # Expanding circle
        size = 50 + progress * 200
        alpha = int(255 * (1 - progress))
        s = pygame.Surface((600, 600), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 255, alpha), (300, 300), int(size), width=5)
        screen.blit(s, (100, 0))
        
        # Static target circle
        pygame.draw.circle(screen, (255, 255, 255), (400, 300), 50, width=2)
        
        # Stats
        hits_text = font.render(f"Hits: {self.hits} / {self.max_hits}", True, (150, 150, 150))
        screen.blit(hits_text, (400 - hits_text.get_width()//2, 500))
        
        if self.hits > 0:
            avg_acc = self.accuracy_sum / self.hits
            acc_text = font.render(f"Avg Accuracy: {avg_acc:.1f}%", True, (0, 255, 0))
            screen.blit(acc_text, (400 - acc_text.get_width()//2, 550))
