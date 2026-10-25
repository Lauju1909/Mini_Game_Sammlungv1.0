import random
import pygame
import time
from games.base_game import BaseGame

class AudioBirdwatcher(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_birdwatcher"
        self.instructions = self._("game_audio_birdwatcher_instructions")
        
        self.score = 0
        self.round = 1
        self.max_rounds = 5
        self.state = "waiting_for_start" # waiting_for_start, calling, listening
        self.current_bird = None
        
        # 4 Vogelarten mit akustischen Mustern
        self.birds = [
            {"id": "cuckoo", "name_key": "bird_cuckoo", "key": 1},
            {"id": "owl", "name_key": "bird_owl", "key": 2},
            {"id": "woodpecker", "name_key": "bird_woodpecker", "key": 3},
            {"id": "nightingale", "name_key": "bird_nightingale", "key": 4},
        ]

    def start(self):
        super().start()
        self.audio.speak(self._("press_enter_to_start"), interrupt=False)

    def _play_birdcall(self, bird_id, pan=0.0):
        if bird_id == "cuckoo":
            # Kuckuck: Kuck (540 Hz), Kuck (420 Hz)
            self.audio.play_tone(540, duration_ms=220, pan=pan)
            pygame.time.delay(120)
            self.audio.play_tone(420, duration_ms=300, pan=pan)
        elif bird_id == "owl":
            # Eule: Tiefes Uh-Huu
            self.audio.play_tone(180, duration_ms=350, pan=pan)
            pygame.time.delay(80)
            self.audio.play_tone(160, duration_ms=450, pan=pan)
        elif bird_id == "woodpecker":
            # Specht: Schnelles Klopfen
            for _ in range(5):
                self.audio.play_tone(700, duration_ms=25, pan=pan)
                pygame.time.delay(40)
        elif bird_id == "nightingale":
            # Nachtigall: Helle Trillertöne
            for freq in [880, 988, 1046, 1174, 1046]:
                self.audio.play_tone(freq, duration_ms=70, pan=pan)
                pygame.time.delay(30)

    def _next_bird(self):
        self.state = "calling"
        self.current_bird = random.choice(self.birds)
        pan = random.choice([-0.8, -0.4, 0.4, 0.8])
        self.audio.speak(self._("round_number", idx=self.round), interrupt=True)
        # Kurze Pause vor dem Ruf
        pygame.time.delay(600)
        self._play_birdcall(self.current_bird["id"], pan=pan)
        self.state = "listening"

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
                    self._next_bird()
            elif self.state == "listening":
                choice = None
                if event.key in [pygame.K_1, pygame.K_KP1]: choice = 1
                elif event.key in [pygame.K_2, pygame.K_KP2]: choice = 2
                elif event.key in [pygame.K_3, pygame.K_KP3]: choice = 3
                elif event.key in [pygame.K_4, pygame.K_KP4]: choice = 4
                elif event.key == pygame.K_SPACE:
                    # Wiederholen
                    self._play_birdcall(self.current_bird["id"])
                    
                if choice is not None:
                    self._check_choice(choice)

    def _check_choice(self, choice):
        if choice == self.current_bird["key"]:
            self.score += 200
            self.audio.play_sound("success")
            self.audio.speak(self._("bird_correct", name=self._(self.current_bird["name_key"])), interrupt=True)
        else:
            self.audio.play_sound("error")
            self.audio.speak(self._("bird_wrong", name=self._(self.current_bird["name_key"])), interrupt=True)
            
        if self.round < self.max_rounds:
            self.round += 1
            pygame.time.delay(500)
            self._next_bird()
        else:
            self.finish()

    def draw(self, screen):
        # Vogel-Beobachtungsstand
        pygame.draw.rect(screen, (20, 35, 25), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (100, 220, 120), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 20)
        
        title = font.render(f"AUDIO-VOGELSTIMMEN - RUNDE {self.round} / {self.max_rounds}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        # 4 Vogelkarten
        options = [
            ("1: Kuckuck (Zweitongesang)", (160, 250)),
            ("2: Waldohreule (Tiefes Uhu)", (440, 250)),
            ("3: Buntspecht (Klopfen)", (160, 330)),
            ("4: Nachtigall (Heller Triller)", (440, 330)),
        ]
        
        for text, (ox, oy) in options:
            pygame.draw.rect(screen, (40, 60, 45), (ox, oy, 250, 50), border_radius=8)
            t_surf = small_font.render(text, True, (230, 255, 230))
            screen.blit(t_surf, (ox + 10, oy + 14))
            
        hint = small_font.render("Tasten 1-4 = Vogel wählen  |  LEERTASTE = Ruf wiederholen", True, (180, 220, 190))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))
