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
        
        # Tolk initialisieren
        self.interrupt_event = threading.Event()
        try:
            dll_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Tolk.dll")
            if os.path.exists(dll_path):
                self.tolk = ctypes.windll.LoadLibrary(dll_path)
                
                # Prototypen definieren
                self.tolk.Tolk_Load.restype = None
                self.tolk.Tolk_IsLoaded.restype = ctypes.c_bool
                self.tolk.Tolk_TrySAPI.restype = ctypes.c_bool
                self.tolk.Tolk_Output.argtypes = [ctypes.c_wchar_p, ctypes.c_bool]
                self.tolk.Tolk_Output.restype = ctypes.c_bool
                self.tolk.Tolk_IsSpeaking.restype = ctypes.c_bool
                self.tolk.Tolk_Silence.restype = ctypes.c_bool
                
                self.tolk.Tolk_Load()
                self.tolk_active = self.tolk.Tolk_IsLoaded()
                if self.tolk_active:
                    self.tolk.Tolk_TrySAPI(True)
            else:
                print("Tolk.dll nicht gefunden.")
        except Exception as e:
            print(f"Tolk Init Fehler: {e}")

        # SAPI Fallback initialisieren
        self.sapi = None
        if not self.tolk_active and HAS_WIN32COM:
            try:
                self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                print("SAPI Fallback aktiviert.")
            except Exception as e:
                print(f"SAPI Init Fehler: {e}")

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
        while not self.stop_worker:
            try:
                # Warte auf neue Nachrichten in der Queue
                text, interrupt = self.speech_queue.get(timeout=0.1)
                
                if interrupt:
                    if self.tolk_active and self.tolk:
                        self.tolk.Tolk_Silence()
                    elif self.sapi:
                        self.sapi.Speak("", 3) # SVSFPurgeBeforeSpeak + Async

                if self.tolk_active and self.tolk:
                    try:
                        # Warten, bis vorherige Sprachausgabe fertig ist, falls kein Interrupt
                        if not interrupt:
                            while self.tolk.Tolk_IsSpeaking() and not self.interrupt_event.is_set():
                                if self.stop_worker: break
                                time.sleep(0.01)
                        
                        self.interrupt_event.clear()
                        self.tolk.Tolk_Output(text, interrupt)
                        
                        # Kurze Pause nach dem Starten, damit Tolk_IsSpeaking Zeit hat, auf True zu springen
                        # Und damit aufeinanderfolgende Ansagen sich nicht überschneiden
                        time.sleep(0.15)
                    except Exception as e:
                        print(f"Tolk Worker Fehler: {e}")
                elif self.sapi:
                    try:
                        if interrupt:
                            # SVSFPurgeBeforeSpeak (2) + Async (1) = 3
                            self.sapi.Speak("", 3)
                        
                        # Flags: Async (1)
                        self.sapi.Speak(text, 1)
                        
                        if not interrupt:
                            # Warte bis SAPI fertig ist (maximal 10 Sekunden pro Ansage)
                            # Wir können SAPI nicht so einfach unterbrechen während WaitUntilDone,
                            # aber wir können das Intervall verkürzen oder Async nutzen.
                            # Da SAPI Async spricht (Flag 1), ist WaitUntilDone eigentlich nur für non-interruptive.
                            elapsed = 0
                            while elapsed < 10000 and not self.interrupt_event.is_set():
                                if self.sapi.WaitUntilDone(100): # 100ms warten
                                    break
                                elapsed += 100
                                if self.stop_worker: break
                        
                        self.interrupt_event.clear()
                    except Exception as e:
                        print(f"SAPI Speak Fehler: {e}")
                
                self.speech_queue.task_done()
            except queue.Empty:
                continue

    def speak(self, text, interrupt=True):
        """Fügt Text zur Sprach-Queue hinzu oder unterbricht sofort."""
        print(f"[TTS]: {text}")
        
        if interrupt:
            self.interrupt_event.set()
            # Leere die aktuelle Queue für sofortige Unterbrechung
            while not self.speech_queue.empty():
                try:
                    self.speech_queue.get_nowait()
                    self.speech_queue.task_done()
                except queue.Empty:
                    break
        
        # Zur Queue hinzufügen
        self.speech_queue.put((text, interrupt))

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
                    return
                except Exception as e:
                    print(f"Panning Fehler: {e}")
        print(f"Sound nicht gefunden: {sound_name}")

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
        """Setzt die Sprachlautstärke (wird aktuell primär über den Screenreader gesteuert)."""
        print(f"Sprachlautstärke auf {volume}% gesetzt.")
        # Zukünftige Implementierung für SAPI-Direktsteuerung hier möglich

    def set_speech_rate(self, rate):
        """Setzt die Sprechgeschwindigkeit (wird aktuell primär über den Screenreader gesteuert)."""
        print(f"Sprechgeschwindigkeit auf {rate}% gesetzt.")
        # Zukünftige Implementierung für SAPI-Direktsteuerung hier möglich

    def cleanup(self):
        self.stop_worker = True
        if self.tolk_active and self.tolk:
            self.tolk.Tolk_Unload()
        pygame.mixer.quit()
