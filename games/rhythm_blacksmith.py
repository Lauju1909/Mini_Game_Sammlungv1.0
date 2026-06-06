import pygame
import time
from games.base_game import BaseGame

class RhythmBlacksmith(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "rhythm_blacksmith"
        self.instructions = self._("game_rhythm_blacksmith_instructions")
        
        self.progress = 0
        self.score = 0
        
        self.beat_interval = 0.8 # 75 BPM
        self.last_beat_time = 0
        self.start_timer = time.time() + 2.0
        self.state = "starting"
        
        self.swords_forged = 0
        self.target_swords = 3

    def start(self):
        super().start()
        self.start_timer = time.time() + 3.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.audio.speak(self._("start_go"), priority=2)
                self.last_beat_time = now + 0.5
            return

        if self.state == "playing":
            # Metronom / Tiefes Hämmern
            if now >= self.last_beat_time:
                self.audio.play_tone(frequency=120, duration_ms=100, volume=70, pan=0.0)
                self.last_beat_time += self.beat_interval

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "playing" and event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                now = time.time()
                
                # Berechne die Distanz zum nächsten oder letzten Beat
                diff_last = now - self.last_beat_time
                diff_next = (self.last_beat_time + self.beat_interval) - now
                
                # Der Spieler kann den Beat leicht verspätet oder früh treffen
                diff = min(abs(diff_last), abs(diff_next))
                
                if diff <= 0.18: # 180ms Toleranz (großzügig)
                    # Perfekter Treffer
                    self.progress += 10
                    self.score += int(100 * (1.0 - (diff / 0.18))) # Je genauer, desto mehr Punkte
                    
                    # Tonhöhe steigt mit Fortschritt
                    freq = 400 + (self.progress * 4)
                    self.audio.play_tone(frequency=freq, duration_ms=80, volume=100, pan=0.0)
                    
                    if self.progress >= 100:
                        # Schwert fertig!
                        self.audio.play_sound("success")
                        self.swords_forged += 1
                        self.progress = 0
                        
                        if self.swords_forged >= self.target_swords:
                            self.audio.speak(self._("blacksmith_all_done"), priority=1)
                            self.sleep(1.0)
                            self.finish()
                        else:
                            self.audio.speak(self._("blacksmith_sword_done", count=self.swords_forged), priority=1)
                            # Schneller werden
                            self.beat_interval *= 0.85
                            
                else:
                    # Takt verfehlt
                    self.audio.play_sound("bump")
                    self.progress = max(0, self.progress - 5)
                    self.score = max(0, self.score - 20)

    def draw(self, screen):
        screen.fill((40, 20, 20))
        
        # Amboss
        pygame.draw.rect(screen, (80, 80, 90), (300, 400, 200, 100))
        pygame.draw.rect(screen, (60, 60, 70), (320, 500, 160, 100))
        
        # Schwert (Glühend)
        if self.state == "playing":
            glow = int(min(255, self.progress * 2.5))
            pygame.draw.rect(screen, (255, glow, 0), (250, 380, 300, 20))
            
            # Funken-Effekt bei Treffer (simuliert durch kurze Farbänderung)
            # Wir machen es hier statisch für den Screenreader, visueller Effekt ist zweitrangig.

        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        progress_surf = font.render(f"Schmiede-Fortschritt: {self.progress}%", True, (255, 200, 100))
        swords_surf = font.render(f"Schwerter: {self.swords_forged}/{self.target_swords}", True, (100, 255, 100))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(swords_surf, (600, 20))
        screen.blit(progress_surf, (400 - progress_surf.get_width()//2, 100))
