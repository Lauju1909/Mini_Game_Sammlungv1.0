import random
import pygame
import time
from games.base_game import BaseGame

class AudioAlchemy(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_alchemy"
        self.instructions = self._("game_audio_alchemy_instructions")
        
        self.score = 0
        self.round = 1
        self.max_rounds = 4
        self.lives = 3
        
        self.target_drops = {"red": 2, "blue": 2}
        self.player_drops = {"red": 0, "blue": 0}
        self.state = "waiting_for_start" # waiting_for_start, brewing, round_eval

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _start_recipe(self):
        self.state = "brewing"
        self.player_drops = {"red": 0, "blue": 0}
        
        if self.round == 1:
            self.target_drops = {"red": random.randint(1, 3), "blue": random.randint(1, 2)}
        elif self.round == 2:
            self.target_drops = {"red": random.randint(2, 4), "blue": random.randint(2, 3)}
        else:
            self.target_drops = {"red": random.randint(2, 5), "blue": random.randint(3, 5)}
            
        recipe_text = self._("alchemy_recipe", r=self.target_drops["red"], b=self.target_drops["blue"])
        self.audio.speak(recipe_text, interrupt=True)

    def handle_input(self, event):
        if not self.active:
            return

        super().handle_input(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return

            if self.state == "waiting_for_start":
                if event.key == pygame.K_RETURN:
                    self._start_recipe()
            elif self.state == "brewing":
                if event.key == pygame.K_1:
                    # Rote Essenz
                    self.player_drops["red"] += 1
                    self.audio.play_tone(frequency=320, duration_ms=90, volume=80, pan=-0.5)
                elif event.key == pygame.K_2:
                    # Blaue Essenz
                    self.player_drops["blue"] += 1
                    self.audio.play_tone(frequency=680, duration_ms=90, volume=80, pan=0.5)
                elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    # Umrühren und Trank prüfen
                    self._stir_cauldron()

    def _stir_cauldron(self):
        self.audio.play_sound("confirm")
        r_ok = self.player_drops["red"] == self.target_drops["red"]
        b_ok = self.player_drops["blue"] == self.target_drops["blue"]
        
        if r_ok and b_ok:
            self.score += 250 * self.round
            self.audio.play_sound("success")
            if self.round < self.max_rounds:
                self.round += 1
                self.audio.speak(self._("alchemy_success"), interrupt=True)
                self._start_recipe()
            else:
                self.audio.speak(self._("alchemy_master"), interrupt=True)
                self.finish()
        else:
            self.lives -= 1
            self.audio.play_sound("error")
            if self.lives > 0:
                self.audio.speak(self._("alchemy_failed", lives=self.lives), interrupt=True)
                self._start_recipe()
            else:
                self.finish()

    def draw(self, screen):
        # Alchemie-Kessel
        pygame.draw.rect(screen, (30, 20, 35), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (200, 80, 255), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-ALCHEMIE - REZEPT {self.round} / {self.max_rounds}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        info = small_font.render(f"Punkte: {self.score}   |   Leben: {self.lives}", True, (255, 215, 0))
        screen.blit(info, (400 - info.get_width() // 2, 195))
        
        # Rezept-Anzeige
        req_text = font.render(f"Ziel: {self.target_drops['red']}x Rot (Taste 1)  +  {self.target_drops['blue']}x Blau (Taste 2)", True, (230, 220, 255))
        screen.blit(req_text, (400 - req_text.get_width() // 2, 240))
        
        # Kessel
        cauldron_rect = pygame.Rect(320, 290, 160, 130)
        pygame.draw.arc(screen, (160, 160, 180), cauldron_rect, 0, 3.1415, 5)
        pygame.draw.ellipse(screen, (120, 60, 160), (320, 290, 160, 40))
        
        # Gegebene Tropfen
        drops_cur = font.render(f"Im Kessel: {self.player_drops['red']} Rot   |   {self.player_drops['blue']} Blau", True, (255, 215, 0))
        screen.blit(drops_cur, (400 - drops_cur.get_width() // 2, 380))
        
        hint = small_font.render("Taste 1 = Rot  |  Taste 2 = Blau  |  LEERTASTE = Trank brauen!", True, (210, 190, 230))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))
