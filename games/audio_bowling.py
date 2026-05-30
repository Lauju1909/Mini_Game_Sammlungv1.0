import random
import pygame
import time
from games.base_game import BaseGame

class AudioBowling(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_bowling"
        self.instructions = self._("game_audio_bowling_instructions")
        self.swing = 0
        self.dir = 1

    def update(self):
        self.swing += self.dir * 0.05
        if self.swing >= 1.0 or self.swing <= 0:
            self.dir *= -1
            if self.swing >= 1.0:
                self.audio.play_sound("bump")
            else:
                self.audio.play_sound("click_002")
                
        now = pygame.time.get_ticks()
        if not hasattr(self, 'last_tick'): self.last_tick = 0
        interval = max(50, 300 - int(self.swing * 250))
        if now - self.last_tick > interval:
            self.audio.play_sound("click")
            self.last_tick = now

    def handle_input(self, event):
        super().handle_input(event)
        if self.is_tutorial: return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Höherer Swing-Wert = besserer Wurf
                pins = int(self.swing * 10)
                self.score = pins * 50
                self.audio.play_sound("confirm")
                self.audio.speak(self._("bowl_pins", pins=pins))
                self.finish()

    def draw(self, screen):
        font_medium = pygame.font.SysFont("Arial", 32)
        
        # Bowlingbahn (Lane)
        pygame.draw.rect(screen, (80, 40, 20), (250, 50, 300, 500))
        pygame.draw.rect(screen, (120, 70, 40), (250, 50, 300, 500), width=5)
        
        # Pins
        pin_positions = [
            (400, 100),
            (370, 80), (430, 80),
            (340, 60), (400, 60), (460, 60),
            (310, 40), (370, 40), (430, 40), (490, 40)
        ]
        for pos in pin_positions:
            pygame.draw.circle(screen, (240, 240, 240), pos, 12)
            pygame.draw.circle(screen, (200, 0, 0), pos, 12, width=2)
            
        # Power Meter (Links)
        pygame.draw.rect(screen, (40, 40, 40), (100, 150, 40, 300))
        fill_height = int(self.swing * 300)
        color = (255, int(255 * (1 - self.swing)), 0) # Von Rot zu Gelb
        pygame.draw.rect(screen, color, (100, 450 - fill_height, 40, fill_height))
        
        label = font_medium.render("POWER", True, (255, 255, 255))
        # Rotiere Label? Nein, einfach drunter
        screen.blit(label, (80, 460))
        
        hint = font_medium.render("Drücke LEERTASTE!", True, (255, 215, 0))
        screen.blit(hint, (400 - hint.get_width()//2, 520))
