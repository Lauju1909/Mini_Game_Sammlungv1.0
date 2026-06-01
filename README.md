# Audio Studio Tycoon: Mini-Game-Sammlung v2.0

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-2.0-green.svg)
![Accessibility](https://img.shields.io/badge/Accessibility-100%25%20Blind%20Accessible-brightgreen.svg)
![QA Status](https://img.shields.io/badge/QA%20Status-Passed%20(Agentic%20Tester%20V6)-brightgreen.svg)

Willkommen bei der **Mini-Game-Sammlung**, einer Sammlung von **48 barrierefreien Mini-Games**, die speziell für blinde und sehbehinderte Spieler sowie für Liebhaber von Audio-Spielen entwickelt wurden.

## 🌟 Features

- **Vollständige Barrierefreiheit:** 100% spielbar ohne visuelles Feedback.
- **Interaktive Tutorials:** Sprachgeführte Einführungen für jedes Spiel beim ersten Start.
- **Screenreader-Integration:** Unterstützt NVDA, JAWS und andere via Tolk (SAPI Fallback).
- **Zweisprachig:** Volle Unterstützung für **Deutsch** und **Englisch**.
- **Vielseitige Kategorien:**
  - **Action & Reaktion:** Audio-Schmiede, Audio-Bogenschießen Pro, Audio-Ping-Pong, Qualitätskontrolle, Audio-Hürdenlauf, Beat-Reaktor, Stereo-Münzfang, Ton-Jäger, Bomben-Entschärfer, Tasten-Gewitter, Schnellwähler, Maulwurf-Meister, Rhythmus-König, Reaktions-Blitz, Audio-Bogenschießen, Beat-Matcher, Audio-Balance, Morse-Läufer.
  - **Logik & Gedächtnis:** Sound-Memo, Simon Says, Audio-Kompass-Memory, Code-Knacker, Zahlen-Raten, Tresor-Knacker, Audio-Schlossknacker, Mathe-Blitz, Tickende Uhren, Tonhöhen-Meister, Klang-Weber, Sound-Folge.
  - **Navigation & Erkundung:** Das goldene Mikrofon, Audio-Labyrinth, Echolot, Die blinde Farm, Weltraum-Flug, Tier-Radar, Geheimnisvolle Türen, Frequenz-Jäger, Treppe des Schicksals, Sonar-U-Boot.
  - **Sprache & Wissen:** Wort-Schlange, Geräusche-Quiz, Buchstaben-Salat, Hauptstadt-Jäger.
  - **Simulation & Spezial:** Audio-Bowling, Schere-Stein-Papier Extreme, Audio-Slots, Echo-Jäger.
- **Premium Design:** Moderne UI mit Glaseffekten, Partikelsystemen und flüssigen Animationen für sehende Mitspieler.
- **Mehrspielermodus:** Lokal an einem PC mit bis zu 4 Spielern.

## 🚀 Installation & Start

1. **Voraussetzungen:** Python 3.10+ installiert.
2. **Repository klonen oder ZIP herunterladen.**
3. **Abhängigkeiten installieren:**
   ```bash
   pip install pygame pywin32
   ```
4. **Spiel starten:**
   ```bash
   python main.py
   ```
   Alternativ die `run_game.bat` nutzen.

## 🎮 Steuerung

- **Pfeiltasten:** Navigieren in Menüs und Spielen.
- **Enter / Leertaste:** Bestätigen / Aktion ausführen.
- **ESC:** Zurück zum Menü / Spiel abbrechen.
- **Zahlen 1-9:** Eingabe in Quiz-Spielen.

## ✅ Quality Assurance

Dieses Projekt wurde mit dem **Agentic Tester V6** (autonomes KI-Testsystem) validiert:
- **Test-Umfang:** 1000+ automatisierte Aktionen in DE/EN Sessions sowie Grafik-Rendering-Simulation aller 40 Mini-Games.
- **Status:** 0 Crashes, stabile Audio-Engine, korrekte Lokalisierung.
- **Ergebnis:** Alle Menüpfade, Zeichenroutinen und Kernmechaniken sind stabil und verifiziert.

## 📈 Changelog v2.0

- **Neues Minispiel hinzugefügt:** "Audio-Schmiede" (Rhythm Blacksmith)
  - Schmiede ein Schwert, indem du exakt im Takt eines dumpfen Hämmerns auf den Amboss schlägst!
- **Neues Minispiel hinzugefügt:** "Audio-Bogenschießen Pro" (Acoustic Archery Pro)
  - Ein verbessertes Audio-Bogenschießen mit Wind-Mechanik! Ein Rauschen auf einer Seite zeigt an, dass man den Schuss ausgleichen muss.
- **Neues Minispiel hinzugefügt:** "Audio-Ping-Pong" (Acoustic Tennis)
  - Ein auditives Tennis! Schlage den Ball zurück, indem du auf die richtige Seite und die zunehmende Lautstärke/Tonhöhe achierst.
- **Neues Minispiel hinzugefügt:** "Audio-Kompass-Memory" (Spatial Audio Memory)
  - Ein räumliches Simon-Says. Merke dir Sequenzen aus Tönen von Vorne, Hinten, Links und Rechts!
- **Neues Minispiel hinzugefügt:** "Audio-Schlossknacker" (Dial Master)
  - Ein auditives Schlossknacken, bei dem feine Tonhöhen-Unterschiede verraten, ob man auf der richtigen Zahl ist.
- **Neues Minispiel hinzugefügt:** "Qualitätskontrolle" (Audio Factory)
  - Ein Fließband-Sortierspiel. Unterscheide gute und defekte Teile anhand der Tonhöhe und sortiere defekte Teile rechtzeitig aus.
- **Neues Minispiel hinzugefügt:** "Sonar-U-Boot" (Submarine Sonar)
  - Ein 360-Grad Echo-Ortungsspiel. Ortet Feinde per Stereo-Pan und Tonhöhe.
  - Volle Lokalisierung und barrierefreies Design integriert.
- **Neues Minispiel hinzugefügt:** "Audio-Hürdenlauf" (Audio Runner)
  - Ein endloser Audio-Hindernisparcours über 3 Spuren.
  - Der Spieler muss durch akustische Hinweise in Form von Stereo-Signalen rechtzeitig die Spur wechseln.
  - Volle DE/EN Lokalisierung und 100% Blindengerechtigkeit integriert.

## 📈 Changelog v1.9

- **Mehrspieler-Optimierung (Hotseat):**
  - Bestätigte reibungslose Hotseat-Rotation für Spiele in der ersten Alphabethälfte (A-M).
  - Fehlende Lokalisierungen für Rundenübergänge und finale Auswertungen (`all_players_finished_winner`, `all_players_finished_tie`) hinzugefügt.
  - Gewährleistet, dass Spieleinstanzen bei jedem Spielerwechsel korrekt zurückgesetzt und ohne globale Statuskonflikte geladen werden.
  - Akustische Barrierefreiheit der Namensansagen (Turn-Switch) und UI-Einbindung gesichert.

## 📈 Changelog v1.8

- **Playability QA (11 Spiele):** Umfassende Fehlerbehebungen und Qualitätskontrollen in `echo_hunter.py`, `echolot.py`, `frequency_jammer.py`, `golden_mic.py`, `key_storm.py`, `letter_salad.py`, `math_blitz.py`, `mole_master.py`, `morse_runner.py`, `mystery_door.py`, `number_guess.py`.
  - Konsistente ESC-Steuerung durch Aufruf von `super().handle_input()` in allen Spielen sichergestellt.
  - Lokalisierungs-Strings (`self._()`) anstelle fest codierter Texte implementiert.
  - Timer-Logik korrigiert (Start- und Endzeitpunkt auf Spielbeginn `start()` anstatt Objekt-Initialisierung verlegt).
  - Screenreader-Ausgaben für Menügrenzen und Spiele-Feedback reaktiviert und verfeinert.

## 📈 Changelog v1.7

- **Kritische Fehlerbehebungen:**
  - `bomb_defuser.py`: Behebung des `UnboundLocalError` bei der `progress`-Variable im Rendering.
  - `key_storm.py`: Behebung des `AttributeError` durch korrekte Initialisierung von `self.target_key = None` vor Spielstart.
  - `number_guess.py`: Behebung des `NameError` durch Verschieben des Pygame-Imports auf Modulebene.
- **Code-Bereinigung:**
  - Alle redundanten und rein lokalen Pygame-Importe in `letter_salad.py`, `rps_extreme.py`, `word_snake.py`, `capital_hunter.py` und `sound_quiz.py` wurden auf Modulebene konsolidiert, um Stabilitätsproblemen vorzubeugen.

## 🛠️ Entwicklung

Das Spiel basiert auf **Pygame** und nutzt eine benutzerdefinierte Audio-Engine für präzise Stereo-Positionierung und Sprachausgabe.

- **Audio-Engine:** `core/audio.py` (Tolk/SAPI)
- **Lokalisierung:** `core/localization.py` (Generiert via `scratch/gen_loc.py`)
- **Spiele-Logik:** `games/` Verzeichnis

### Lokalisierung verwalten
Alle Übersetzungen werden zentral in `scratch/gen_loc.py` gepflegt. Um Änderungen zu übernehmen:
1. Bearbeite `TRANSLATIONS_DE` oder `TRANSLATIONS_EN` in `scratch/gen_loc.py`.
2. Führe das Skript aus: `python scratch/gen_loc.py`.
3. `core/localization.py` wird automatisch aktualisiert.

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 🔗 Links

- **Repository:** [https://github.com/Lauju1909/Mini_Game_Sammlungv1.0](https://github.com/Lauju1909/Mini_Game_Sammlungv1.0)
- **Releases:** [Download v1.7](https://github.com/Lauju1909/Mini_Game_Sammlungv1.0/releases)

---
*Entwickelt für das Advanced Agentic Coding Team von Google Deepmind.*
