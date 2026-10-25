import pygame
import time
from games.base_game import BaseGame

class AudioLockpicker(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_lockpicker"
        self.instructions = self._("game_audio_lockpicker_instructions")
        
        self.score = 0
        self.state = "waiting_for_start"
        self.lives = 3
        
        self.pins_total = 3
        self.pins_set = 0
        
        self.pin_progress = 0.0 # 0.0 to 1.0
        self.is_lifting = False
        self.lift_speed = 0.5 # per second
        self.sweet_spot = 0.7 # Where it clicks
        self.click_played = False
        self.last_update = time.monotonic()

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_game(self):
        self.state = "playing"
        self.score = 0
        self.lives = 3
        self.pins_set = 0
        self.audio.speak(self._("start_go"), interrupt=True)
        self._reset_pin()

    def _reset_pin(self):
        self.pin_progress = 0.0
        self.is_lifting = False
        self.click_played = False
        self.last_update = time.monotonic()
        # Randomize sweet spot for each pin
        import random
        self.sweet_spot = random.uniform(0.4, 0.9)
        self.lift_speed = random.uniform(0.4, 0.8) + (self.pins_set * 0.1)

    def update(self):
        if not self.active or self.state != "playing":
            return
            
        current_time = time.monotonic()
        dt = current_time - self.last_update
        self.last_update = current_time
        
        if self.is_lifting:
            self.pin_progress += self.lift_speed * dt
            
            # Sound feedback for lifting
            # Since we can't easily change pitch dynamically without a library,
            # we can play a short ticking sound rapidly
            if int(self.pin_progress * 100) % 5 == 0:
                # Play a tick
                # We could use panning or a simple sound
                pass # Or just play one continuous sound if we had it. Let's stick to clicks.
            
            # Play the sweet spot click
            if self.pin_progress >= self.sweet_spot and not self.click_played:
                self.audio.play_sound("metalClick")
                self.click_played = True
                
            # If lifted too far
            if self.pin_progress >= 1.0:
                self._fail_pin()

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
                if event.key == pygame.K_UP:
                    if not self.is_lifting:
                        self.is_lifting = True
                        self.audio.play_sound("scroll_001") # Start lift sound
                elif event.key == pygame.K_SPACE:
                    if self.is_lifting:
                        self._try_set()
                        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                if self.is_lifting:
                    # Dropped the pin
                    self._fail_pin()

    def _try_set(self):
        # Check if within sweet spot (e.g. +/- 0.1)
        if abs(self.pin_progress - self.sweet_spot) <= 0.1:
            self.pins_set += 1
            self.score += 100
            self.audio.play_sound("success")
            
            if self.pins_set >= self.pins_total:
                self._win_game()
            else:
                self.audio.speak(self._("pin_set", num=self.pins_set), interrupt=True)
                self._reset_pin()
        else:
            self._fail_pin()

    def _fail_pin(self):
        self.lives -= 1
        self.audio.play_sound("error")
        if self.lives > 0:
            self.audio.speak(self._("pin_failed", lives=self.lives), interrupt=True)
            self._reset_pin()
        else:
            self.state = "game_over"
            self.audio.speak(self._("lockpicker_gameover"), interrupt=True)
            self.audio.speak(self._("final_score", score=self.score), interrupt=False)
            self.finish()

    def _win_game(self):
        self.state = "game_over"
        self.audio.play_sound("success")
        self.audio.speak(self._("lock_opened"), interrupt=True)
        self.audio.speak(self._("final_score", score=self.score), interrupt=False)
        self.finish()

    def draw(self, screen):
        # Schloss-Visualisierung
        pygame.draw.rect(screen, (20, 25, 30), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (220, 180, 60), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-SCHLOSSKNACKER - STIFT {self.pins_set + 1} / {self.pins_total}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        info = small_font.render(f"Punkte: {self.score}   |   Fehlversuche übrig: {self.lives}", True, (255, 215, 0))
        screen.blit(info, (400 - info.get_width() // 2, 195))
        
        # Zylinder / Stifte
        for i in range(self.pins_total):
            px = 280 + i * 120
            py = 320
            # Schacht
            pygame.draw.rect(screen, (40, 45, 55), (px - 20, 240, 40, 140), border_radius=4)
            # Gesetzter Stift vs aktiver
            if i < self.pins_set:
                col = (50, 220, 80)
                pin_h = 40
            elif i == self.pins_set:
                col = (255, 200, 50) if self.click_played else (100, 180, 255)
                pin_h = int(240 + (1.0 - self.pin_progress) * 90) - 240 + 20
            else:
                col = (90, 90, 90)
                pin_h = 100
            pygame.draw.rect(screen, col, (px - 16, 380 - pin_h, 32, pin_h), border_radius=4)
            
        hint = small_font.render("Pfeil OBEN gedrückt halten (Anheben), bei Klick LEERTASTE!", True, (200, 200, 220))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

