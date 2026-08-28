import pygame
import time
from games.base_game import BaseGame

class RhythmMaster(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "rhythm_master"
        self.instructions = self._("game_rhythm_master_instructions")
        self.bpm = 100
        self.beat_interval = 60 / self.bpm
        self.last_beat_time = 0
        self.next_beat_time = 0
        self.score = 0
        self.combo = 0
        self.game_duration = 30 # seconds
        self.start_time = 0
        self.beats_hit = 0
        self.total_beats = 0
        self.visual_beats = [] # For drawing

    def start(self):
        super().start()
        self.start_time = time.monotonic()
        self.next_beat_time = self.start_time + 1.0
        self.audio.speak(self._("ready"), interrupt=False)

    def update(self):
        if not self.active: return
        
        current_time = time.monotonic()
        if current_time - self.start_time > self.game_duration:
            self.finish()
            return

        # Check for missed beat
        if current_time > self.next_beat_time + 0.2:
            self.audio.play_sound("error")
            self.combo = 0
            self.next_beat_time += self.beat_interval
            self.total_beats += 1
            # Speed up slightly
            self.bpm = min(180, self.bpm + 2)
            self.beat_interval = 60 / self.bpm

        # Play beat sound
        if current_time >= self.next_beat_time - 0.05 and current_time < self.next_beat_time:
            # We use a small window to trigger the sound exactly on beat
            # but we don't want to trigger it multiple times
            pass 

        # Auto-beat sound (metronome)
        if current_time >= self.next_beat_time:
            self.audio.play_sound("click")
            # Add to visual beats
            self.visual_beats.append({"time": current_time, "alpha": 255})
            
    def handle_input(self, event):
        if not self.active: return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                current_time = time.monotonic()
                diff = abs(current_time - self.next_beat_time)
                
                if diff < 0.1: # Perfect
                    self.score += 50 + (self.combo * 5)
                    self.combo += 1
                    self.audio.play_sound("confirm")
                    self.audio.speak(self._("hit_perfect"), interrupt=True)
                    self._on_hit()
                elif diff < 0.2: # Good
                    self.score += 20
                    self.combo += 1
                    self.audio.play_sound("select")
                    self.audio.speak(self._("hit_good"), interrupt=True)
                    self._on_hit()
                else: # Miss
                    self.score = max(0, self.score - 10)
                    self.combo = 0
                    self.audio.play_sound("bump")
                    self.audio.speak(self._("miss"), interrupt=True)

    def _on_hit(self):
        self.beats_hit += 1
        self.total_beats += 1
        # Set next beat
        self.next_beat_time += self.beat_interval
        # Gradually increase speed
        self.bpm = min(200, self.bpm + 1)
        self.beat_interval = 60 / self.bpm

    def draw(self, screen):
        center = (400, 300)
        # Draw a rhythmic ring
        current_time = time.monotonic()
        pulse = (current_time % self.beat_interval) / self.beat_interval
        
        # Outer ring shrinking to center
        ring_radius = int(200 * (1.0 - pulse))
        pygame.draw.circle(screen, (255, 215, 0), center, max(1, ring_radius), width=5)
        
        # Center target
        target_color = (0, 255, 127) if pulse < 0.1 or pulse > 0.9 else (100, 100, 100)
        pygame.draw.circle(screen, target_color, center, 40)
        
        # Draw hit feedback
        for beat in self.visual_beats[:]:
            elapsed = current_time - beat["time"]
            if elapsed > 0.5:
                self.visual_beats.remove(beat)
                continue
            
            radius = 40 + int(elapsed * 400)
            alpha = int(255 * (1.0 - elapsed * 2))
            s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, alpha), (radius, radius), radius, width=2)
            screen.blit(s, (center[0]-radius, center[1]-radius))

        # Stats
        font = pygame.font.SysFont("Arial", 36, bold=True)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        combo_surf = font.render(f"Combo: x{self.combo}", True, (255, 215, 0))
        screen.blit(score_surf, (40, 40))
        screen.blit(combo_surf, (40, 90))
        
        # BPM
        bpm_surf = font.render(f"BPM: {int(self.bpm)}", True, (150, 150, 255))
        screen.blit(bpm_surf, (650, 40))
