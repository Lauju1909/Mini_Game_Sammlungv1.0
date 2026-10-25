import math
import random
import pygame
import time
from games.base_game import BaseGame

class AudioFishing(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_fishing"
        self.instructions = self._("game_audio_fishing_instructions")
        
        self.round = 1
        self.max_rounds = 5
        self.score = 0
        
        self.state = "waiting_for_start" # waiting_for_start, casting, waiting_for_bite, biting
        self.fish_timer = 0
        self.bite_time = 0
        self.bite_duration = 0
        self.last_splash = 0

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_round(self):
        self.audio.speak(self._("round_number", idx=self.round), interrupt=True)
        self.state = "casting"
        self.audio.speak(self._("press_space_to_cast"), interrupt=False)

    def _cast_line(self):
        self.audio.play_sound("confirm") # Simulate casting sound
        self.state = "waiting_for_bite"
        # Fish will bite randomly between 2 to 6 seconds
        self.fish_timer = time.monotonic() + random.uniform(2.0, 6.0)

    def _trigger_bite(self):
        self.state = "biting"
        self.bite_time = time.monotonic()
        # The player has a small window to react (0.5 to 1.2 seconds depending on round)
        self.bite_duration = max(0.5, 1.2 - (self.round * 0.1))
        self.audio.play_sound("blip") # The bite sound!

    def update(self):
        if not self.active:
            return
            
        current_time = time.monotonic()
        
        if self.state == "waiting_for_bite":
            # Ambient water sounds
            if current_time - self.last_splash > random.uniform(1.0, 2.5):
                self.last_splash = current_time
                self.audio.play_sound("bump") # Ambient substitute
                
            if current_time >= self.fish_timer:
                self._trigger_bite()
                
        elif self.state == "biting":
            # Rapid beeping to indicate struggle
            if current_time - self.last_splash > 0.15:
                self.last_splash = current_time
                self.audio.play_sound("blip")
                
            if current_time - self.bite_time > self.bite_duration:
                # Fish escaped
                self.audio.play_sound("error")
                self.audio.speak(self._("fish_escaped"), interrupt=True)
                self._end_round(False)

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_round()
            elif self.state == "casting":
                if event.key == pygame.K_SPACE:
                    self._cast_line()
            elif self.state == "waiting_for_bite":
                if event.key == pygame.K_SPACE:
                    # Pulled too early!
                    self.audio.play_sound("error")
                    self.audio.speak(self._("too_early"), interrupt=True)
                    self._end_round(False)
            elif self.state == "biting":
                if event.key == pygame.K_SPACE:
                    # Caught the fish!
                    reaction_time = time.monotonic() - self.bite_time
                    points = int(max(10, 1000 - (reaction_time * 1000)))
                    self.score += points
                    self.audio.play_sound("confirm")
                    self.audio.speak(self._("fish_caught", points=points), interrupt=True)
                    self._end_round(True)

    def _end_round(self, success):
        self.round += 1
        self.state = "waiting_for_start"
        if self.round > self.max_rounds:
            self.audio.speak(self._("final_score", score=self.score), interrupt=False)
            self.finish()
        else:
            self.audio.speak(self._("press_enter_to_continue"), interrupt=False)

    def draw(self, screen):
        # See / Angel-Visualisierung
        pygame.draw.rect(screen, (10, 30, 55), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (0, 180, 220), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-ANGELN - RUNDE {self.round} / {self.max_rounds}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        # Wasseroberfläche
        pygame.draw.line(screen, (0, 150, 255), (100, 330), (700, 330), 3)
        for x in range(120, 680, 40):
            wave_y = 330 + int(math.sin(time.monotonic() * 3 + x * 0.05) * 5)
            pygame.draw.circle(screen, (80, 200, 255), (x, wave_y), 3)
            
        # Pose / Schwimmer
        bobber_y = 330
        if self.state == "biting":
            bobber_y += int(math.sin(time.monotonic() * 20) * 12) + 6
            glow = (255, 60, 60)
        else:
            glow = (255, 200, 0)
            
        if self.state in ["waiting_for_bite", "biting"]:
            # Angelschnur
            pygame.draw.line(screen, (220, 220, 220), (200, 240), (400, bobber_y), 2)
            # Schwimmer
            pygame.draw.circle(screen, glow, (400, bobber_y), 14)
            pygame.draw.circle(screen, (255, 255, 255), (400, bobber_y - 6), 6)
            
        status_map = {
            "waiting_for_start": "Drücke EINGABE zum Starten",
            "casting": "Drücke LEERTASTE zum Auswerfen",
            "waiting_for_bite": "Warte auf Anbiss... Lausche auf das Signal!",
            "biting": "FISCH BEISST AN! JETZT LEERTASTE DRÜCKEN!"
        }
        st_color = (255, 80, 80) if self.state == "biting" else (200, 240, 255)
        st_surf = font.render(status_map.get(self.state, ""), True, st_color)
        screen.blit(st_surf, (400 - st_surf.get_width() // 2, 440))

