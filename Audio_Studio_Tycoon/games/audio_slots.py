import random
import pygame
import time
from games.base_game import BaseGame

class AudioSlots(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_slots"
        self.instructions = self._("game_audio_slots_instructions")
        self.symbols = ["confirm", "select", "success", "cash", "blip", "warn"]
        self.reels = ["confirm", "confirm", "confirm"]
        self.is_spinning = False
        self.spin_timer = 0
        self.spins_left = 10 # 10 Versuche pro Spiel
        self.total_score = 0

    def start(self):
        super().start()
        self.audio.speak(self._("game_audio_slots_desc"), interrupt=True)

    def update(self):
        if self.is_spinning:
            if time.time() > self.spin_timer:
                self.is_spinning = False
                self._resolve_spin()

    def handle_input(self, event):
        if self.is_spinning: return
        
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.spins_left > 0:
                    self._spin()
                else:
                    self.finish()
            elif event.key == pygame.K_ESCAPE:
                self.finish()

    def _spin(self):
        self.is_spinning = True
        self.spins_left -= 1
        self.audio.play_sound("drumroll")
        self.audio.speak(self._("slots_spinning"), interrupt=True)
        self.spin_timer = time.time() + 2.0 # 2 Sekunden Spannung
        
        # Vorab Ergebnis bestimmen
        self.reels = [random.choice(self.symbols) for _ in range(3)]

    def _resolve_spin(self):
        r1, r2, r3 = self.reels
        
        # Sounds abspielen
        for sym in self.reels:
            self.audio.play_sound(sym)
            time.sleep(0.3)
            
        res_text = self._("slots_result", r1=r1, r2=r2, r3=r3)
        self.audio.speak(res_text, interrupt=False)
        
        # Gewinnberechnung
        spin_score = 0
        if r1 == r2 == r3:
            # Jackpot!
            spin_score = 500
            self.audio.speak(self._("jackpot"), interrupt=False)
            self.audio.play_sound("success")
        elif r1 == r2 or r2 == r3 or r1 == r3:
            # Kleiner Gewinn
            spin_score = 100
            self.audio.speak(self._("win_small"), interrupt=False)
            self.audio.play_sound("confirm")
        
        self.score += spin_score
        
        if self.spins_left <= 0:
            self.audio.speak(self._("game_over"), interrupt=False)
            # Kurz warten bevor beendet wird
            self.finish()

    def draw(self, screen):
        # Visuelle Darstellung der Slots
        font_large = pygame.font.SysFont("Arial", 48, bold=True)
        font_main = pygame.font.SysFont("Arial", 32)
        
        # Titel
        title_surf = font_large.render(self._("game_audio_slots"), True, (255, 215, 0))
        screen.blit(title_surf, (400 - title_surf.get_width()//2, 50))
        
        # Walzen zeichnen
        for i in range(3):
            x = 200 + i * 150
            y = 200
            rect = pygame.Rect(x, y, 100, 150)
            pygame.draw.rect(screen, (30, 30, 50), rect, border_radius=10)
            pygame.draw.rect(screen, (100, 100, 150), rect, width=3, border_radius=10)
            
            if not self.is_spinning:
                sym_text = self.reels[i].capitalize()
                sym_surf = font_main.render(sym_text[:3].upper(), True, (255, 255, 255))
                screen.blit(sym_surf, (x + 50 - sym_surf.get_width()//2, y + 75 - sym_surf.get_height()//2))
            else:
                # Animiertes Drehen (Zufälliger Text)
                temp_sym = random.choice(self.symbols).upper()[:3]
                sym_surf = font_main.render(temp_sym, True, (150, 150, 150))
                screen.blit(sym_surf, (x + 50 - sym_surf.get_width()//2, y + 75 - sym_surf.get_height()//2))

        # Spins übrig und Score
        spins_text = f"Spins: {self.spins_left}"
        spins_surf = font_main.render(spins_text, True, (255, 255, 255))
        screen.blit(spins_surf, (100, 450))
        
        score_text = f"{self._('points')}: {self.score}"
        score_surf = font_main.render(score_text, True, (255, 255, 255))
        screen.blit(score_surf, (700 - score_surf.get_width(), 450))
