import math
import pygame
import os
import sys
import ctypes
import queue
import threading
import time

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

class AudioManager:
    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.tolk = None
        self.tolk_active = False
        
        # Audio Queue und Threading
        self.speech_queue = queue.Queue()
        self.stop_worker = False
        self.last_speech_time = 0
        self.current_priority = 0
        
        # Tolk initialisieren
        self.interrupt_event = threading.Event()
        try:
            dll_path = resource_path("Tolk.dll")
            if os.path.exists(dll_path):
                self.tolk = ctypes.windll.LoadLibrary(dll_path)
                
                # Prototypen explizit definieren
                self.tolk.Tolk_Load.restype = ctypes.c_bool
                self.tolk.Tolk_IsLoaded.restype = ctypes.c_bool
                self.tolk.Tolk_Unload.restype = None
                
                if hasattr(self.tolk, 'Tolk_TrySAPI'):
                    self.tolk.Tolk_TrySAPI.argtypes = [ctypes.c_bool]
                    self.tolk.Tolk_TrySAPI.restype = ctypes.c_bool
                
                self.tolk.Tolk_Output.argtypes = [ctypes.c_wchar_p, ctypes.c_bool]
                self.tolk.Tolk_Output.restype = ctypes.c_bool
                self.tolk.Tolk_IsSpeaking.restype = ctypes.c_bool
                
                if hasattr(self.tolk, 'Tolk_Silence'):
                    self.tolk.Tolk_Silence.restype = ctypes.c_bool
                
                # Initialisieren
                if self.tolk.Tolk_Load():
                    self.tolk_active = self.tolk.Tolk_IsLoaded()
                    if self.tolk_active:
                        if hasattr(self.tolk, 'Tolk_TrySAPI'):
                            self.tolk.Tolk_TrySAPI(True)
                else:
                    print("Tolk_Load() fehlgeschlagen.")
            else:
                print("Tolk.dll nicht gefunden.")
        except Exception as e:
            print(f"Tolk Init Fehler: {e}")

        # SAPI Fallback initialisieren
        self.sapi = None
        self.sapi = None

        # Pygame Mixer initialisieren
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        except Exception as e:
            print(f"Mixer Init Fehler: {e}")

        self.music_volume = self.settings.get("volume_music", 50)
        self.sfx_volume = self.settings.get("volume_sfx", 100)
        self.set_volumes(self.sfx_volume, self.music_volume)

        # Worker Thread starten
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    def _speech_worker(self):
        """Hintergrund-Thread zur Verarbeitung der Sprachausgabe."""
        thread_sapi = None
        if not self.tolk_active and HAS_WIN32COM:
            try:
                import ctypes
                ctypes.windll.ole32.CoInitialize(None)
                thread_sapi = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception as e:
                print(f"SAPI Init Fehler im Worker: {e}")

        while not self.stop_worker:
            try:
                # Warte auf neue Nachrichten in der Queue
                text, interrupt, priority = self.speech_queue.get(timeout=0.1)
                
                if self.tolk_active and self.tolk:
                    try:
                        if interrupt:
                            if hasattr(self.tolk, 'Tolk_Silence'):
                                self.tolk.Tolk_Silence()
                        else:
                            # Warten, bis vorherige Sprachausgabe fertig ist, falls kein Interrupt
                            wait_start = time.time()
                            while self.tolk.Tolk_IsSpeaking() and not self.interrupt_event.is_set():
                                if self.stop_worker or (time.time() - wait_start > 5.0):
                                    break
                                time.sleep(0.01)
                        
                        self.interrupt_event.clear()
                        self.tolk.Tolk_Output(text, interrupt)
                        self.current_priority = priority
                        
                        # Kurze Pause nach dem Starten
                        time.sleep(0.05)
                    except Exception as e:
                        print(f"Tolk Worker Fehler: {e}")
                elif thread_sapi:
                    try:
                        if interrupt:
                            # SVSFPurgeBeforeSpeak (2) + Async (1) = 3
                            thread_sapi.Speak("", 3)
                        
                        self.current_priority = priority
                        # Flags: Async (1)
                        thread_sapi.Speak(text, 1)
                        
                        if not interrupt:
                            # Warte bis SAPI fertig ist
                            elapsed = 0
                            while elapsed < 10000 and not self.interrupt_event.is_set():
                                if thread_sapi.WaitUntilDone(100):
                                    break
                                elapsed += 100
                                if self.stop_worker: break
                        
                        self.interrupt_event.clear()
                    except Exception as e:
                        print(f"SAPI Speak Fehler: {e}")
                
                self.speech_queue.task_done()
            except Exception as e:
                # queue.Empty ist okay bei timeout=0.1
                if "Empty" not in str(type(e)):
                    print(f"Audio Worker Fehler: {e}")
                
    def _clear_queue(self):
        """Leert die aktuelle Sprach-Warteschlange."""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break

    def is_speaking(self):
        """Gibt zurück ob gerade gesprochen wird oder noch Text in der Queue ist."""
        if not self.speech_queue.empty():
            return True
        if self.tolk_active and self.tolk:
            try:
                return self.tolk.Tolk_IsSpeaking()
            except:
                pass
        return False

    def speak(self, text, interrupt=True, priority=1):
        """
        Fügt Text zur Sprach-Queue hinzu oder unterbricht sofort.
        Prioritäten: 
        0 = Info (UI Details, kann immer unterbrochen werden)
        1 = Standard (Menüpunkte, Ergebnisse)
        2 = Wichtig (Systemmeldungen, Spielstart, Spielerwechsel)
        """
        if not text or not str(text).strip(): return
        
        now = time.time()
        
        # Debounce: Wenn der exakt gleiche Text innerhalb von 300ms nochmal kommt, ignorieren
        if hasattr(self, '_last_text') and self._last_text == text and (now - self.last_speech_time < 0.3):
            return
            
        actual_interrupt = interrupt
        
        # Prioritäten-Logik
        if interrupt:
            # 1. Wenn eine Nachricht mit niedrigerer Prio eine mit höherer unterbrechen will -> Warteschlange
            if priority < self.current_priority:
                actual_interrupt = False
            
            # 2. Stomping-Schutz bei gleicher oder niedrigerer Priorität
            elif priority <= self.current_priority:
                # Wenn die letzte Ansage erst vor kurzem (< 200ms) gestartet wurde, 
                # stellen wir uns lieber an, statt das erste Wort zu "stompem".
                if now - self.last_speech_time < 0.2:
                    actual_interrupt = False
            
            # Wenn wir unterbrechen (oder es vorhatten), leeren wir die Queue für veraltete Nachrichten
            # außer wir haben gerade entschieden, uns DOCH nur hinten anzustellen.
            if actual_interrupt:
                self.interrupt_event.set()
                self._clear_queue()
        
        self._last_text = text
        self.last_speech_time = now
        self.speech_queue.put((text, actual_interrupt, priority))

    def play_sound(self, sound_name):
        formats = ["ogg", "mp3", "wav"]
        for fmt in formats:
            path = resource_path(os.path.join("assets", f"{sound_name}.{fmt}"))
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.sfx_volume / 100.0)
                    sound.play()
                    return
                except Exception as e:
                    print(f"Fehler beim Abspielen von {sound_name}.{fmt}: {e}")
        print(f"Sound nicht gefunden: {sound_name}")

    def play_panned_sound(self, sound_name, pan):
        """Spielt einen Sound mit Stereo-Panning (-1.0 links bis 1.0 rechts)."""
        formats = ["ogg", "mp3", "wav"]
        for fmt in formats:
            path = resource_path(os.path.join("assets", f"{sound_name}.{fmt}"))
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    channel = pygame.mixer.find_channel()
                    if channel:
                        # Berechne Lautstärke für links und rechts
                        left = max(0.0, min(1.0, (1.0 - pan)))
                        right = max(0.0, min(1.0, (1.0 + pan)))
                        channel.set_volume(left * (self.sfx_volume/100.0), right * (self.sfx_volume/100.0))
                        channel.play(sound)
                        return channel
                except Exception as e:
                    print(f"Panning Fehler: {e}")
        print(f"Sound nicht gefunden: {sound_name}")
        return None

    def play_looping_sound(self, sound_name, volume=None):
        """Startet einen Sound in einer Endlosschleife und gibt den Kanal zurück."""
        formats = ["ogg", "mp3", "wav"]
        for fmt in formats:
            path = resource_path(os.path.join("assets", f"{sound_name}.{fmt}"))
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    channel = pygame.mixer.find_channel()
                    if channel:
                        vol = (volume if volume is not None else self.sfx_volume) / 100.0
                        channel.set_volume(vol)
                        channel.play(sound, loops=-1)
                        return channel
                except Exception as e:
                    print(f"Looping Fehler: {e}")
        return None

    def play_tone(self, frequency, duration_ms=500, volume=None, pan=0.0):
        """Erzeugt einen Sinuston mit der angegebenen Frequenz."""
        try:
            sample_rate = 44100
            n_samples = int(sample_rate * (duration_ms / 1000.0))
            
            # Sinuswelle generieren (16-bit signed)
            buffer = bytearray()
            vol = (volume if volume is not None else self.sfx_volume) / 100.0
            amplitude = 32767 * vol
            
            for i in range(n_samples):
                # f(t) = A * sin(2 * pi * freq * t)
                t = i / sample_rate
                value = int(amplitude * math.sin(2 * math.pi * frequency * t))
                # 16-bit Little Endian
                buffer.extend(value.to_bytes(2, byteorder='little', signed=True))
            
            sound = pygame.mixer.Sound(buffer=buffer)
            
            if pan == 0.0:
                sound.set_volume(vol)
                sound.play()
            else:
                channel = pygame.mixer.find_channel()
                if channel:
                    left = max(0.0, min(1.0, (1.0 - pan)))
                    right = max(0.0, min(1.0, (1.0 + pan)))
                    channel.set_volume(left * vol, right * vol)
                    channel.play(sound)
                    return channel
        except Exception as e:
            print(f"Tone Generation Fehler: {e}")
        return None

    def create_tone_loop(self, frequency, volume=None):
        """Erzeugt einen looping Sinuston."""
        try:
            sample_rate = 44100
            # Eine Periode oder eine kurze Schleife, die nahtlos ist
            # Wir nehmen eine feste Länge von 0.1s für den Loop-Puffer
            duration = 0.1 
            n_samples = int(sample_rate * duration)
            
            buffer = bytearray()
            vol = (volume if volume is not None else self.sfx_volume) / 100.0
            amplitude = 32767 * vol
            
            for i in range(n_samples):
                t = i / sample_rate
                value = int(amplitude * math.sin(2 * math.pi * frequency * t))
                buffer.extend(value.to_bytes(2, byteorder='little', signed=True))
            
            sound = pygame.mixer.Sound(buffer=buffer)
            channel = pygame.mixer.find_channel()
            if channel:
                channel.set_volume(vol)
                channel.play(sound, loops=-1)
                return channel
        except Exception as e:
            print(f"Tone Loop Fehler: {e}")
        return None

    def stop_sound(self, channel):
        """Stoppt den Sound auf dem angegebenen Kanal."""
        if channel:
            try:
                channel.stop()
            except:
                pass

    def fadeout_sound(self, channel, time_ms):
        """Blendet den Sound auf dem angegebenen Kanal über time_ms Millisekunden aus."""
        if channel:
            try:
                channel.fadeout(time_ms)
            except:
                pass

    def set_channel_volume(self, channel, volume_left, volume_right=None):
        """Setzt die Lautstärke eines Kanals (0.0 bis 1.0)."""
        if channel:
            try:
                if volume_right is None:
                    channel.set_volume(volume_left * (self.sfx_volume / 100.0))
                else:
                    channel.set_volume(volume_left * (self.sfx_volume / 100.0), volume_right * (self.sfx_volume / 100.0))
            except:
                pass

    def set_volumes(self, sfx_vol, music_vol):
        """Aktualisiert die Lautstärken für SFX und Musik."""
        self.sfx_volume = sfx_vol
        self.music_volume = music_vol
        # Musik-Lautstärke im Pygame-Mixer setzen
        try:
            pygame.mixer.music.set_volume(self.music_volume / 100.0)
        except Exception as e:
            print(f"Fehler beim Setzen der Musik-Lautstärke: {e}")

    def set_speech_volume(self, volume):
        """Setzt die Sprachlautstärke (0-100)."""
        print(f"Sprachlautstärke auf {volume}% gesetzt.")
        if self.sapi:
            try:
                # SAPI Volume ist 0-100
                self.sapi.Volume = max(0, min(100, volume))
            except:
                pass

    def set_speech_rate(self, rate):
        """Setzt die Sprechgeschwindigkeit (30-100)."""
        print(f"Sprechgeschwindigkeit auf {rate}% gesetzt.")
        if self.sapi:
            try:
                # SAPI Rate ist -10 bis 10. 50% entspricht etwa 0.
                sapi_rate = int((rate - 50) / 5)
                self.sapi.Rate = max(-10, min(10, sapi_rate))
            except:
                pass

    def cleanup(self):
        self.stop_worker = True
        if self.tolk_active and self.tolk:
            self.tolk.Tolk_Unload()
        pygame.mixer.quit()
