import pygame
import random
import time
from games.base_game import BaseGame

class AudioBoss(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_boss"
        self.instructions = self._("game_audio_boss_instructions")
        
        self.boss_hp = 100
        self.player_hp = 3
        self.score = 0
        
        self.state = "starting"
        self.start_timer = time.time() + 3.0
        
        self.current_attack = None
        self.attack_timer = 0
        self.next_attack_time = time.time() + 4.0
        self.last_tick = time.time()
        self.last_beep = 0
        
        # Attack specific
        self.proj_dist = 0
        self.proj_side = 0
        self.proj_speed = 40.0
        
        self.melee_dir = ""
        self.shield_charge = 0

    def start(self):
        super().start()
        self.audio.speak(self._("boss_intro"), priority=2)
        self.start_timer = time.time() + 4.0

    def start_random_attack(self):
        attacks = ["projectile", "melee", "aoe"]
        chosen = random.choice(attacks)
        
        if chosen == "projectile":
            self.current_attack = "projectile"
            self.proj_dist = 100.0
            self.proj_side = random.choice([-1.0, 1.0])
            self.proj_speed = 35.0 + (100 - self.boss_hp) * 0.2 # Wird schneller
            
        elif chosen == "melee":
            self.current_attack = "melee_telegraph"
            self.melee_dir = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            self.attack_timer = time.time() + max(0.6, 1.2 - (100 - self.boss_hp)*0.005)
            
        elif chosen == "aoe":
            self.current_attack = "aoe"
            self.attack_timer = time.time() + 3.0
            self.shield_charge = 0

    def end_attack(self):
        self.current_attack = None
        self.next_attack_time = time.time() + 1.5

    def take_damage(self):
        self.player_hp -= 1
        self.audio.play_sound("error")
        if self.player_hp <= 0:
            self.audio.speak(self._("boss_defeat"), priority=2)
            self.sleep(1)
            self.finish()
        else:
            self.audio.speak(self._("boss_hit", hp=self.player_hp), priority=1)

    def damage_boss(self, amount):
        self.boss_hp -= amount
        self.score += amount * 10
        self.audio.play_sound("confirm")
        
        if self.boss_hp <= 0:
            self.boss_hp = 0
            self.audio.speak(self._("boss_victory"), priority=2)
            self.score += self.player_hp * 500
            self.sleep(2)
            self.finish()
        else:
            if self.boss_hp in [75, 50, 25]:
                self.audio.speak(f"{self.boss_hp}%", priority=1)

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
                self.next_attack_time = now + 1.0
            return

        if self.state == "playing":
            if self.current_attack is None:
                if now > self.next_attack_time:
                    self.start_random_attack()
            
            elif self.current_attack == "projectile":
                self.proj_dist -= self.proj_speed * dt
                if self.proj_dist <= 0:
                    self.take_damage()
                    self.end_attack()
                else:
                    beep_interval = max(0.08, (self.proj_dist / 100.0) * 0.3)
                    if now - self.last_beep > beep_interval:
                        self.last_beep = now
                        freq = int(800 - (self.proj_dist * 4))
                        vol = int(max(10, 100 - self.proj_dist))
                        self.audio.play_tone(frequency=freq, duration_ms=40, volume=vol, pan=self.proj_side)
            
            elif self.current_attack == "melee_telegraph":
                if now - self.last_beep > 0.15:
                    self.last_beep = now
                    freq = 500
                    pan = 0.0
                    if self.melee_dir == "LEFT": pan = -1.0
                    elif self.melee_dir == "RIGHT": pan = 1.0
                    elif self.melee_dir == "UP": freq = 800
                    elif self.melee_dir == "DOWN": freq = 300
                    self.audio.play_tone(frequency=freq, duration_ms=100, volume=60, pan=pan)
                    
                if now > self.attack_timer:
                    self.current_attack = "melee_strike"
                    self.attack_timer = now + 0.6
                    self.audio.play_sound("bump") # Wusch-Geräusch als Angriff
            
            elif self.current_attack == "melee_strike":
                if now > self.attack_timer:
                    self.take_damage()
                    self.end_attack()
                    
            elif self.current_attack == "aoe":
                if now > self.attack_timer:
                    if self.shield_charge >= 12:
                        self.damage_boss(20) # AoE abwehren macht viel Schaden
                    else:
                        self.take_damage()
                    self.end_attack()
                else:
                    if now - self.last_beep > 0.1:
                        self.last_beep = now
                        progress = 1.0 - ((self.attack_timer - now) / 3.0)
                        freq = 200 + progress * 600
                        self.audio.play_tone(frequency=int(freq), duration_ms=80, volume=80)

    def handle_input(self, event):
        if not self.active: return
        if self.is_tutorial:
            self.handle_tutorial_input(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.finish()
                return
            
            if self.state == "playing":
                if self.current_attack == "projectile":
                    if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        pressed_side = -1.0 if event.key == pygame.K_LEFT else 1.0
                        if pressed_side == self.proj_side and self.proj_dist <= 30.0:
                            self.damage_boss(15)
                        else:
                            self.take_damage()
                        self.end_attack()
                
                elif self.current_attack == "melee_strike":
                    direction_map = {
                        pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
                        pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"
                    }
                    if event.key in direction_map:
                        if direction_map[event.key] == self.melee_dir:
                            self.damage_boss(10)
                        else:
                            self.take_damage()
                        self.end_attack()
                        
                elif self.current_attack == "aoe":
                    if event.key == pygame.K_SPACE:
                        self.shield_charge += 1
                        self.audio.play_tone(frequency=400 + self.shield_charge * 20, duration_ms=50)

    def draw(self, screen):
        screen.fill((20, 0, 0))
        
        # Boss HP
        pygame.draw.rect(screen, (100, 0, 0), (100, 50, 600, 40))
        pygame.draw.rect(screen, (255, 0, 0), (100, 50, self.boss_hp * 6, 40))
        
        font = pygame.font.SysFont("Arial", 32)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.player_hp}", True, (100, 255, 100))
        
        screen.blit(score_surf, (20, 150))
        screen.blit(lives_surf, (20, 200))
        
        state_surf = font.render(f"Angriff: {self.current_attack}", True, (200, 200, 200))
        screen.blit(state_surf, (20, 250))
