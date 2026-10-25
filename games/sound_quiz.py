import pygame
from games.base_game import BaseGame

class SoundQuiz(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "sound_quiz"
        self.instructions = self._("game_sound_quiz_instructions")
        self.questions = [
            {"sound": "click", "options": [self._("sq_mouse"), self._("sq_car"), self._("sq_piano")], "correct": 0},
            {"sound": "confirm", "options": [self._("sq_bell"), self._("sq_bird"), self._("sq_thunder")], "correct": 0},
            {"sound": "error", "options": [self._("sq_dog"), self._("sq_alarm"), self._("sq_water")], "correct": 1}
        ]
        self.idx = 0
        
    def start(self):
        super().start()
        self._ask()

    def _ask(self):
        q = self.questions[self.idx]
        self.audio.play_sound(q["sound"])
        self.audio.speak(self._("sound_quiz_question", opt1=q['options'][0], opt2=q['options'][1], opt3=q['options'][2]))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            self.questions[self.idx]
            if event.key == pygame.K_1: self._check(0)
            elif event.key == pygame.K_2: self._check(1)
            elif event.key == pygame.K_3: self._check(2)
            elif event.key == pygame.K_ESCAPE: self.finish()

    def _check(self, choice):
        if choice == self.questions[self.idx]["correct"]:
            self.audio.play_sound("success")
            self.score += 100
        else:
            self.audio.play_sound("error")
        
        self.idx += 1
        if self.idx >= len(self.questions): self.finish()
        else: self._ask()

    def draw(self, screen):
        # Sound-Quiz-Bühne
        pygame.draw.rect(screen, (20, 20, 45), (60, 140, 680, 360), border_radius=20)
        pygame.draw.rect(screen, (140, 100, 255), (60, 140, 680, 360), width=2, border_radius=20)
        
        font = pygame.font.SysFont("Arial", 28, bold=True)
        small_font = pygame.font.SysFont("Arial", 22)
        
        title = font.render(f"SOUND-QUIZ - RUNDE {self.idx + 1} / {len(self.questions)}", True, (255, 255, 255))
        screen.blit(title, (400 - title.get_width() // 2, 155))
        
        score_surf = small_font.render(f"Punkte: {self.score}", True, (255, 215, 0))
        screen.blit(score_surf, (400 - score_surf.get_width() // 2, 195))
        
        if self.idx < len(self.questions):
            q = self.questions[self.idx]
            q_txt = font.render("Welches Geräusch hast du gehört?", True, (230, 230, 255))
            screen.blit(q_txt, (400 - q_txt.get_width() // 2, 240))
            
            for i, opt in enumerate(q["options"]):
                oy = 300 + i * 45
                pygame.draw.rect(screen, (40, 40, 80), (160, oy, 480, 38), border_radius=8)
                opt_txt = small_font.render(f"Taste {i + 1}: {opt}", True, (255, 255, 255))
                screen.blit(opt_txt, (180, oy + 6))
                
        hint = small_font.render("Drücke Taste 1, 2 oder 3 auf deiner Tastatur", True, (180, 180, 220))
        screen.blit(hint, (400 - hint.get_width() // 2, 465))

