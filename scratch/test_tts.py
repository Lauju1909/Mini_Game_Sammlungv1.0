import sys
import os
import time

# Pfade hinzufügen
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, 'core'))

from core.settings_manager import SettingsManager
from core.audio import AudioManager

print("--- Sprachausgabe-Test ---")
# Korrekter settings_path
settings_path = os.path.join(PROJECT_ROOT, "data", "settings.json")
settings = SettingsManager(settings_path)
audio = AudioManager(settings)

print(f"Tolk geladen: {audio.tolk_active}")
if audio.tolk_active:
    print("-> NVDA, JAWS oder SAPI wird über Tolk angesteuert.")
else:
    print("-> SAPI Fallback wird verwendet.")
    print(f"SAPI initialisiert: {audio.sapi is not None}")

test_text = "Hallo! Die Sprachausgabe der Mini-Game-Sammlung wurde erfolgreich getestet und funktioniert ordnungsgemäß."
print(f"Spreche: '{test_text}'")

audio.speak(test_text, interrupt=True, priority=2)

# Da speak asynchron im Worker-Thread läuft, müssen wir kurz warten, bis die Ausgabe fertig ist.
time.sleep(5)

audio.cleanup()
print("Sprachausgabe-Test abgeschlossen.")
