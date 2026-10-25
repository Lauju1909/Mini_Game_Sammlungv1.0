import random
import pygame
import time
from games.base_game import BaseGame

class AudioJuggler(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_juggler"
        self.instructions = self._("game_audio_juggler_instructions")
        
        self.score = 0
        self.lives = 3
        self.state = "waiting_for_start" # waiting_for_start, playing
        
        # Balls falling. Format: {"pos": "left"/"center"/"right", "time_to_hit": float}
        self.balls = []
        self.speed_multiplier = 1.0
        self.spawn_timer = 0.0

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_game(self):
        self.state = "playing"
        self.audio.speak(self._("start_go"), interrupt=True)
        self.spawn_timer = time.monotonic() + 1.0

    def _spawn_ball(self):
        pos = random.choice(["left", "center", "right"])
        fall_time = 2.0 / self.speed_multiplier
        self.balls.append({"pos": pos, "time_to_hit": time.monotonic() + fall_time})
        
        # Play the throw sound with panning
        pan = -0.8 if pos == "left" else (0.8 if pos == "right" else 0.0)
        self.audio.play_sound("hit", pan=pan)

    def update(self):
        if not self.active or self.state != "playing":
            return
            
        current_time = time.monotonic()
        
        # Spawn new balls
        if current_time >= self.spawn_timer:
            self._spawn_ball()
            # Next spawn time gets slightly faster
            self.speed_multiplier += 0.02
            interval = max(0.6, 2.0 / self.speed_multiplier)
            self.spawn_timer = current_time + interval
            
        # Check missed balls
        for ball in self.balls[:]:
            # Give a small 0.2s grace period after exact hit time
            if current_time > ball["time_to_hit"] + 0.2:
                self.balls.remove(ball)
                self.lives -= 1
                self.audio.play_sound("error")
                
                if self.lives > 0:
                    self.audio.speak(self._("ball_dropped", lives=self.lives), interrupt=True)
                else:
                    self.state = "game_over"
                    self.audio.speak(self._("juggler_gameover"), interrupt=True)
                    self.audio.speak(self._("final_score", score=self.score), interrupt=False)
                    self.finish()

    def handle_input(self, event):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
                
            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_game()
            elif self.state == "playing":
                pos_hit = None
                if event.key == pygame.K_LEFT:
                    pos_hit = "left"
                elif event.key == pygame.K_UP:
                    pos_hit = "center"
                elif event.key == pygame.K_RIGHT:
                    pos_hit = "right"
                    
                if pos_hit:
                    self._try_catch(pos_hit)

    def _try_catch(self, pos):
        current_time = time.monotonic()
        # Find the oldest ball in this position
        target_ball = None
        for ball in self.balls:
            if ball["pos"] == pos:
                if target_ball is None or ball["time_to_hit"] < target_ball["time_to_hit"]:
                    target_ball = ball
                    
        if target_ball:
            time_diff = abs(current_time - target_ball["time_to_hit"])
            if time_diff <= 0.4: # Catch window
                self.balls.remove(target_ball)
                self.score += int(10 * self.speed_multiplier)
                
                pan = -0.8 if pos == "left" else (0.8 if pos == "right" else 0.0)
                self.audio.play_sound("confirm", pan=pan)
                return
                
        # If we reach here, missed catch
        self.audio.play_sound("bump") # Empty hand sound

    def draw(self, screen):
        # Jongleur-Visualisierung
        pygame.draw.rect(screen, (25, 20, 40), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (180, 100, 255), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render("AUDIO-JONGLEUR", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        info = small_font.render(f"Punkte: {self.score}   |   Leben: {self.lives} / 3", True, (255, 215, 0))
        screen.blit(info, (400 - info.get_width() // 2, 195))
        
        # 3 Bahnen: Links (220), Mitte (400), Rechts (580)
        lanes = {"left": 220, "center": 400, "right": 580}
        for name, lx in lanes.items():
            pygame.draw.line(screen, (60, 50, 90), (lx, 220), (lx, 420), 2)
            # Fang-Zone am unteren Ende
            pygame.draw.circle(screen, (100, 70, 160), (lx, 420), 24, width=2)
            lbl = small_font.render(name.upper()[:1], True, (150, 130, 200))
            screen.blit(lbl, (lx - lbl.get_width() // 2, 430))
            
        # Fallende Bälle
        now = time.monotonic()
        for b in self.balls:
            lx = lanes.get(b["pos"], 400)
            time_left = b["time_to_hit"] - now
            # y geht von 220 bis 420
            progress = max(0.0, min(1.0, 1.0 - (time_left / 2.0)))
            by = int(220 + progress * 200)
            bcol = (255, 220, 50) if progress < 0.8 else (50, 255, 120)
            pygame.draw.circle(screen, bcol, (lx, by), 16)
            pygame.draw.circle(screen, (255, 255, 255), (lx - 4, by - 4), 5)
            
        hint = small_font.render("Pfeil LINKS / OBEN / RECHTS zum Fangen im richtigen Takt", True, (180, 180, 210))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

