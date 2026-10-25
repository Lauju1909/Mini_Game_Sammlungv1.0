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
    SOUND_ALIASES = {
        "hit": "bump",
        "menu_move": "select",
        "radar": "blip",
        "swipe": "knifeSlice",
        "win": "success",
        "explosion": "error_008",
    }

    FALLBACK_TONES = {
        "hit": (280, 90),
        "menu_move": (520, 45),
        "radar": (880, 70),
        "swipe": (640, 60),
        "win": (784, 220),
        "explosion": (110, 320),
        "blip": (750, 60),
        "select": (500, 45),
        "confirm": (660, 110),
        "success": (880, 180),
        "error": (190, 220),
        "warn": (330, 150),
        "bump": (160, 90),
        "click": (950, 25),
    }

    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.prism = None
        self.prism_ctx = None
        self.prism_backend = None
        self.prism_active = False
        self.prism_backend_name = "None"
        self._speech_end_time = 0.0
        
        # Audio Queue und Threading
        self.speech_queue = queue.Queue()
        self.stop_worker = False
        self.last_speech_time = 0
        self.current_priority = 0
        self.sound_cache = {}
        self.tone_cache = {}
        self.interrupt_event = threading.Event()
        
        # Prism initialisieren (Ersatz fuer Tolk.dll und nvdaControllerClient64.dll)
        try:
            dll_path = resource_path("prism.dll")
            if os.path.exists(dll_path):
                self.prism = ctypes.cdll.LoadLibrary(dll_path)
                
                # Prototypen fuer prism.dll definieren
                self.prism.prism_init.argtypes = [ctypes.c_void_p]
                self.prism.prism_init.restype = ctypes.c_void_p
                
                self.prism.prism_shutdown.argtypes = [ctypes.c_void_p]
                self.prism.prism_shutdown.restype = None
                
                self.prism.prism_registry_create_best.argtypes = [ctypes.c_void_p]
                self.prism.prism_registry_create_best.restype = ctypes.c_void_p
                
                self.prism.prism_backend_name.argtypes = [ctypes.c_void_p]
                self.prism.prism_backend_name.restype = ctypes.c_char_p
                
                self.prism.prism_backend_speak.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]
                self.prism.prism_backend_speak.restype = ctypes.c_int
                
                self.prism.prism_backend_output.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_bool]
                self.prism.prism_backend_output.restype = ctypes.c_int
                
                self.prism.prism_backend_stop.argtypes = [ctypes.c_void_p]
                self.prism.prism_backend_stop.restype = ctypes.c_int
                
                self.prism.prism_backend_set_volume.argtypes = [ctypes.c_void_p, ctypes.c_float]
                self.prism.prism_backend_set_volume.restype = ctypes.c_int
                
                self.prism.prism_backend_set_rate.argtypes = [ctypes.c_void_p, ctypes.c_float]
                self.prism.prism_backend_set_rate.restype = ctypes.c_int
                
                self.prism.prism_backend_free.argtypes = [ctypes.c_void_p]
                self.prism.prism_backend_free.restype = None
                
                self.prism_ctx = self.prism.prism_init(None)
                if self.prism_ctx:
                    self.prism_backend = self.prism.prism_registry_create_best(self.prism_ctx)
                    if self.prism_backend:
                        self.prism_active = True
                        raw_name = self.prism.prism_backend_name(self.prism_backend)
                        self.prism_backend_name = raw_name.decode('utf-8', errors='ignore') if raw_name else "Unknown"
                        print(f"Prism initialisiert mit Backend: {self.prism_backend_name}")
                    else:
                        print("Prism: Kein verfuegbares Backend im System gefunden.")
                else:
                    print("Prism: prism_init() fehlgeschlagen.")
            else:
                print("prism.dll nicht gefunden.")
        except Exception as e:
            print(f"Prism Init Fehler: {e}")

        # SAPI Fallback initialisieren
        self.sapi = None
        self._pending_speech_volume = None
        self._pending_speech_rate = None

        # Pygame Mixer initialisieren
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
        except Exception as e:
            print(f"Mixer Init Fehler: {e}")

        self.music_volume = self.settings.get("volume_music", 50)
        self.sfx_volume = self.settings.get("volume_sfx", 100)
        self.set_volumes(self.sfx_volume, self.music_volume)

        # Worker Thread starten
        self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.worker_thread.start()

    @property
    def tolk(self):
        """Rueckwaertskompatibilitaet fuer Altsysteme/Tests."""
        return None

    @property
    def tolk_active(self):
        """Rueckwaertskompatibilitaet: signalisiert aktive Screenreader-Ausgabe."""
        return self.prism_active

    def _speech_worker(self):
        """Hintergrund-Thread zur Verarbeitung der Sprachausgabe."""
        thread_sapi = None
        if not self.prism_active and HAS_WIN32COM:
            try:
                import ctypes
                ctypes.windll.ole32.CoInitialize(None)
                thread_sapi = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception as e:
                print(f"SAPI Init Fehler im Worker: {e}")

        while not self.stop_worker:
            # Apply pending speech settings
            if self.prism_active and self.prism and self.prism_backend:
                if self._pending_speech_volume is not None:
                    try:
                        vol_float = max(0.0, min(1.0, self._pending_speech_volume / 100.0))
                        self.prism.prism_backend_set_volume(self.prism_backend, vol_float)
                    except Exception:
                        pass
                    self._pending_speech_volume = None
                if self._pending_speech_rate is not None:
                    try:
                        rate_float = max(0.2, min(3.0, (self._pending_speech_rate + 10) / 10.0))
                        self.prism.prism_backend_set_rate(self.prism_backend, rate_float)
                    except Exception:
                        pass
                    self._pending_speech_rate = None
            elif thread_sapi:
                if self._pending_speech_volume is not None:
                    try:
                        thread_sapi.Volume = self._pending_speech_volume
                        self._pending_speech_volume = None
                    except:
                        pass
                if self._pending_speech_rate is not None:
                    try:
                        thread_sapi.Rate = self._pending_speech_rate
                        self._pending_speech_rate = None
                    except:
                        pass
            
            try:
                # Warte auf neue Nachrichten in der Queue
                text, interrupt, priority = self.speech_queue.get(timeout=0.1)
                text_str = str(text) if text is not None else ""
                
                # Geschaetzte Sprechdauer: ~60ms pro Wort + 250ms Grundzeit
                word_count = len(text_str.split())
                est_duration = max(0.3, 0.25 + word_count * 0.065)
                
                if self.prism_active and self.prism and self.prism_backend:
                    try:
                        if interrupt:
                            try:
                                self.prism.prism_backend_stop(self.prism_backend)
                            except Exception:
                                pass
                        else:
                            # Warten, bis vorherige Sprachausgabe abgelaufen ist, falls kein Interrupt
                            wait_start = time.monotonic()
                            while (time.monotonic() < self._speech_end_time) and not self.interrupt_event.is_set():
                                if self.stop_worker or (time.monotonic() - wait_start > 5.0):
                                    break
                                time.sleep(0.01)
                        
                        self.interrupt_event.clear()
                        utf8_bytes = text_str.encode('utf-8', errors='replace')
                        res = self.prism.prism_backend_output(self.prism_backend, utf8_bytes, interrupt)
                        if res != 0:
                            self.prism.prism_backend_speak(self.prism_backend, utf8_bytes, interrupt)
                        
                        self._speech_end_time = time.monotonic() + est_duration
                        self.current_priority = priority
                        time.sleep(0.04)
                    except Exception as e:
                        print(f"Prism Worker Fehler: {e}")
                elif thread_sapi:
                    try:
                        if interrupt:
                            # SVSFPurgeBeforeSpeak (2) + Async (1) = 3
                            thread_sapi.Speak("", 3)
                        
                        self.current_priority = priority
                        # Flags: Async (1)
                        thread_sapi.Speak(text_str, 1)
                        
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
        """Gibt zurueck ob gerade gesprochen wird oder noch Text in der Queue ist."""
        if not self.speech_queue.empty():
            return True
        if self.prism_active and time.monotonic() < self._speech_end_time:
            return True
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
        
        now = time.monotonic()
        
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

    def _resolve_volume(self, volume=None):
        """Normalisiert Lautstärke-Werte (0.0-1.0 oder 0-100) relativ zu sfx_volume."""
        base_vol = max(0.0, min(1.0, self.sfx_volume / 100.0))
        if volume is None:
            return base_vol
        if isinstance(volume, float) and 0.0 <= volume <= 1.0:
            return max(0.0, min(1.0, base_vol * volume))
        return max(0.0, min(1.0, base_vol * (float(volume) / 100.0)))

    def _load_sound_cached(self, sound_name):
        """Lädt eine Sound-Datei aus dem Cache oder von der Festplatte (inkl. Alias-Auflösung)."""
        resolved_name = self.SOUND_ALIASES.get(sound_name, sound_name)
        if resolved_name in self.sound_cache:
            return self.sound_cache[resolved_name]

        formats = ["ogg", "mp3", "wav"]
        for name_candidate in (sound_name, resolved_name):
            for fmt in formats:
                path = resource_path(os.path.join("assets", f"{name_candidate}.{fmt}"))
                if os.path.exists(path):
                    try:
                        sound = pygame.mixer.Sound(path)
                        self.sound_cache[resolved_name] = sound
                        self.sound_cache[sound_name] = sound
                        return sound
                    except Exception as e:
                        print(f"Fehler beim Laden von {name_candidate}.{fmt}: {e}")
        return None

    def play_sound(self, sound_name, volume=None, pan=0.0):
        """Spielt einen Sound ab (unterstützt optionale Lautstärke und Stereo-Panning)."""
        if pan != 0.0:
            return self.play_panned_sound(sound_name, pan=pan, volume=volume)

        sound = self._load_sound_cached(sound_name)
        vol = self._resolve_volume(volume)
        if sound is not None:
            try:
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.set_volume(vol)
                    channel.play(sound)
                    return channel
                else:
                    sound.set_volume(vol)
                    sound.play()
                    return None
            except Exception as e:
                print(f"Fehler beim Abspielen von {sound_name}: {e}")

        # Synthetischer Fallback-Ton, falls Sound-Datei nicht existiert
        freq, dur = self.FALLBACK_TONES.get(sound_name, (520, 80))
        return self.play_tone(freq, duration_ms=dur, volume=vol * 100.0, pan=pan)

    def play_panned_sound(self, sound_name, pan, volume=None):
        """Spielt einen Sound mit Stereo-Panning (-1.0 links bis 1.0 rechts)."""
        pan = max(-1.0, min(1.0, float(pan)))
        sound = self._load_sound_cached(sound_name)
        vol = self._resolve_volume(volume)
        if sound is not None:
            try:
                channel = pygame.mixer.find_channel(True)
                if channel:
                    left = max(0.0, min(1.0, (1.0 - pan) * 0.5 if pan > 0 else 1.0))
                    right = max(0.0, min(1.0, (1.0 + pan) * 0.5 if pan < 0 else 1.0))
                    channel.set_volume(left * vol, right * vol)
                    channel.play(sound)
                    return channel
            except Exception as e:
                print(f"Panning Fehler: {e}")

        freq, dur = self.FALLBACK_TONES.get(sound_name, (520, 80))
        return self.play_tone(freq, duration_ms=dur, volume=vol * 100.0, pan=pan)

    def play_looping_sound(self, sound_name, volume=None):
        """Startet einen Sound in einer Endlosschleife und gibt den Kanal zurück."""
        sound = self._load_sound_cached(sound_name)
        vol = self._resolve_volume(volume)
        if sound is not None:
            try:
                channel = pygame.mixer.find_channel(True)
                if channel:
                    channel.set_volume(vol)
                    channel.play(sound, loops=-1)
                    return channel
            except Exception as e:
                print(f"Looping Fehler: {e}")
        return None

    def play_tone(self, frequency, duration_ms=500, volume=None, pan=0.0):
        """Erzeugt einen Sinuston mit der angegebenen Frequenz."""
        try:
            frequency = max(40, min(10000, int(frequency)))
            duration_ms = max(10, int(duration_ms))
            pan = max(-1.0, min(1.0, float(pan)))
            vol = self._resolve_volume(volume)

            cache_key = (frequency, duration_ms)
            sound = self.tone_cache.get(cache_key)
            if sound is None:
                mixer_init = pygame.mixer.get_init()
                sample_rate = mixer_init[0] if mixer_init else 44100
                channels = mixer_init[2] if mixer_init else 2
                n_samples = max(1, int(sample_rate * (duration_ms / 1000.0)))
                fade_samples = min(int(sample_rate * 0.005), max(1, n_samples // 4))

                # Sinuswelle generieren (16-bit signed) mit sanftem Fade-In/Out gegen Knacken
                buffer = bytearray()
                amplitude = 28000
                two_pi_f = 2.0 * math.pi * frequency / sample_rate

                for i in range(n_samples):
                    env = 1.0
                    if i < fade_samples:
                        env = i / fade_samples
                    elif i > n_samples - fade_samples:
                        env = (n_samples - i) / fade_samples
                    value = int(amplitude * env * math.sin(two_pi_f * i))
                    sample_bytes = value.to_bytes(2, byteorder='little', signed=True)
                    if channels == 2:
                        buffer.extend(sample_bytes)
                        buffer.extend(sample_bytes)
                    else:
                        buffer.extend(sample_bytes)

                sound = pygame.mixer.Sound(buffer=buffer)
                if len(self.tone_cache) < 256:
                    self.tone_cache[cache_key] = sound

            channel = pygame.mixer.find_channel(True)
            if channel:
                if pan == 0.0:
                    channel.set_volume(vol)
                else:
                    left = max(0.0, min(1.0, 1.0 - max(0.0, pan)))
                    right = max(0.0, min(1.0, 1.0 + min(0.0, pan)))
                    channel.set_volume(left * vol, right * vol)
                channel.play(sound)
                return channel
            else:
                sound.set_volume(vol)
                sound.play()
        except Exception as e:
            print(f"Tone Generation Fehler: {e}")
        return None

    def create_tone_loop(self, frequency, volume=None):
        """Erzeugt einen looping Sinuston."""
        try:
            frequency = max(40, min(10000, int(frequency)))
            mixer_init = pygame.mixer.get_init()
            sample_rate = mixer_init[0] if mixer_init else 44100
            channels = mixer_init[2] if mixer_init else 2
            # Ganze Perioden verwenden, damit der Loop nahtlos ist
            cycles = max(1, int(round(frequency * 0.1)))
            n_samples = max(1, int(round(sample_rate * cycles / frequency)))
            
            buffer = bytearray()
            vol = self._resolve_volume(volume)
            amplitude = 26000
            two_pi_f = 2.0 * math.pi * frequency / sample_rate
            
            for i in range(n_samples):
                value = int(amplitude * math.sin(two_pi_f * i))
                sample_bytes = value.to_bytes(2, byteorder='little', signed=True)
                if channels == 2:
                    buffer.extend(sample_bytes)
                    buffer.extend(sample_bytes)
                else:
                    buffer.extend(sample_bytes)
            
            sound = pygame.mixer.Sound(buffer=buffer)
            channel = pygame.mixer.find_channel(True)
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
        self._pending_speech_volume = max(0, min(100, volume))
        print(f"Sprachlautstärke auf {volume}% gesetzt.")

    def set_speech_rate(self, rate):
        """Setzt die Sprechgeschwindigkeit (30-100)."""
        sapi_rate = int((rate - 50) / 5)
        self._pending_speech_rate = max(-10, min(10, sapi_rate))
        print(f"Sprechgeschwindigkeit auf {rate}% gesetzt.")

    def cleanup(self):
        self.stop_worker = True
        if self.prism_active and self.prism:
            try:
                if self.prism_backend:
                    self.prism.prism_backend_stop(self.prism_backend)
                    self.prism.prism_backend_free(self.prism_backend)
                    self.prism_backend = None
                if self.prism_ctx:
                    self.prism.prism_shutdown(self.prism_ctx)
                    self.prism_ctx = None
            except Exception as e:
                print(f"Fehler bei Prism Cleanup: {e}")
            self.prism_active = False
        pygame.mixer.quit()
