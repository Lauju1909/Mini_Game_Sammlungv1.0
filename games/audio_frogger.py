import pygame
import random
import time
from games.base_game import BaseGame

class AudioFrogger(BaseGame):
    def __init__(self, audio, highscore, settings, player):
        super().__init__(audio, highscore, settings, player)
        self.game_id = "audio_frogger"
        self.instructions = self._("game_audio_frogger_instructions")
        
        self.score = 0
        self.lives = 3
        self.level = 1
        
        self.road_index = 0
        self.roads = []
        self.generate_roads()
        
        self.state = "starting"
        self.start_timer = time.time() + 2.0
        self.last_tick = time.time()
        self.last_car_beep = 0

    def generate_roads(self):
        self.roads = []
        for i in range(10):
            direction = random.choice([-1, 1])
            speed = 30 + i * 4 + (self.level * 5)
            
            # Anzahl der Autos steigt mit Level und Straße
            if i < 2: num_cars = 1
            elif i < 7: num_cars = 2
            else: num_cars = min(3, 1 + self.level)
            
            cars = []
            spacing = 200.0 / num_cars
            for c in range(num_cars):
                cars.append(-100.0 + c * spacing)
                
            self.roads.append({
                "dir": direction,
                "speed": speed,
                "cars": cars
            })

    def start(self):
        super().start()
        self.audio.speak(self._("start_go"), priority=2)
        self.start_timer = time.time() + 2.0

    def update(self):
        if not self.active: return
        if self.is_tutorial: return

        now = time.time()
        dt = now - self.last_tick
        self.last_tick = now

        if self.state == "starting":
            if now > self.start_timer:
                self.state = "playing"
            return

        if self.state == "playing":
            # Autos bewegen
            for road in self.roads:
                for i in range(len(road["cars"])):
                    road["cars"][i] += road["dir"] * road["speed"] * dt
                    
                    if road["dir"] == 1 and road["cars"][i] > 100:
                        road["cars"][i] -= 200
                    elif road["dir"] == -1 and road["cars"][i] < -100:
                        road["cars"][i] += 200

            # Audio für die aktuelle Straße (die vor dem Spieler)
            if now - self.last_car_beep > 0.08:
                self.last_car_beep = now
                current_road = self.roads[self.road_index]
                
                # Finde das Auto, das der Mitte (0) am nächsten ist
                closest_car = min(current_road["cars"], key=abs)
                
                pan = max(-1.0, min(1.0, closest_car / 100.0))
                
                # Doppler-Effekt
                is_approaching = (current_road["dir"] == 1 and closest_car < 0) or (current_road["dir"] == -1 and closest_car > 0)
                base_freq = 300 + (self.road_index * 20)
                freq = base_freq + 60 if is_approaching else base_freq - 60
                
                vol = int(max(10, 100 - abs(closest_car)))
                
                self.audio.play_tone(frequency=int(freq), duration_ms=50, volume=vol, pan=pan)

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
                if event.key == pygame.K_UP:
                    current_road = self.roads[self.road_index]
                    closest_car = min(current_road["cars"], key=abs)
                    
                    if abs(closest_car) < 25.0:
                        # Crash!
                        self.lives -= 1
                        self.audio.play_sound("error")
                        self.audio.play_sound("bump") # Matschiges Geräusch
                        self.road_index = 0
                        
                        if self.lives <= 0:
                            self.audio.speak(self._("frogger_gameover"), priority=2)
                            time.sleep(1.5)
                            self.finish()
                        else:
                            self.audio.speak(self._("lives_left", lives=self.lives), priority=1)
                    else:
                        # Sicher überquert
                        self.audio.play_sound("success")
                        self.road_index += 1
                        self.score += 10
                        
                        if self.road_index >= 10:
                            # Level geschafft!
                            self.audio.play_sound("confirm")
                            self.level += 1
                            self.score += 100
                            self.road_index = 0
                            self.generate_roads()
                            self.audio.speak(self._("frogger_level_up", level=self.level), priority=2)
                            self.state = "starting"
                            self.start_timer = time.time() + 2.0

    def draw(self, screen):
        screen.fill((30, 30, 30))
        
        font = pygame.font.SysFont("Arial", 28)
        score_surf = font.render(f"Punkte: {self.score}", True, (255, 255, 255))
        lives_surf = font.render(f"Leben: {self.lives}", True, (255, 100, 100))
        level_surf = font.render(f"Level: {self.level}", True, (100, 255, 100))
        road_surf = font.render(f"Straße: {self.road_index + 1} / 10", True, (200, 200, 255))
        
        screen.blit(score_surf, (20, 20))
        screen.blit(lives_surf, (650, 20))
        screen.blit(level_surf, (20, 60))
        screen.blit(road_surf, (20, 100))
        
        # Straßen visualisieren
        for i in range(10):
            y = 500 - (i * 40)
            color = (50, 50, 50)
            if i == self.road_index:
                color = (100, 100, 50) # Aktuelle Straße vor einem
            pygame.draw.rect(screen, color, (100, y, 600, 30))
            
            # Autos auf der Straße
            for car in self.roads[i]["cars"]:
                car_x = 400 + (car / 100.0) * 300
                pygame.draw.rect(screen, (255, 0, 0), (car_x - 10, y + 5, 20, 20))
        
        # Spieler visualisieren
        player_y = 500 - (self.road_index * 40) + 35 # Steht "vor" der aktuellen Straße
        pygame.draw.rect(screen, (0, 255, 0), (390, player_y, 20, 20))
