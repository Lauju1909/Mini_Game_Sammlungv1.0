# Audio Studio Tycoon: Mini-Game-Sammlung v1.6

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.6-green.svg)
![Accessibility](https://img.shields.io/badge/Accessibility-100%25%20Blind%20Accessible-brightgreen.svg)
![QA Status](https://img.shields.io/badge/QA%20Status-Passed%20(Agentic%20Tester%20V4)-brightgreen.svg)

Willkommen bei der **Mini-Game-Sammlung**, einer Sammlung von **40 barrierefreien Mini-Games**, die speziell für blinde und sehbehinderte Spieler sowie für Liebhaber von Audio-Spielen entwickelt wurden.

## 🌟 Features

- **Vollständige Barrierefreiheit:** 100% spielbar ohne visuelles Feedback.
- **Screenreader-Integration:** Unterstützt NVDA, JAWS und andere via Tolk (SAPI Fallback).
- **Zweisprachig:** Volle Unterstützung für **Deutsch** und **Englisch**.
- **Vielseitige Kategorien:**
  - **Action & Reaktion:** Beat-Reaktor, Stereo-Münzfang, Ton-Jäger, Bomben-Entschärfer, Tasten-Gewitter, Schnellwähler, Maulwurf-Meister, Rhythmus-König, Reaktions-Blitz, Audio-Bogenschießen, Beat-Matcher, Audio-Balance, Morse-Läufer.
  - **Logik & Gedächtnis:** Sound-Memo, Simon Says, Code-Knacker, Zahlen-Raten, Tresor-Knacker, Mathe-Blitz, Tickende Uhren, Tonhöhen-Meister, Klang-Weber, Sound-Folge.
  - **Navigation & Erkundung:** Das goldene Mikrofon, Audio-Labyrinth, Echolot, Die blinde Farm, Weltraum-Flug, Tier-Radar, Geheimnisvolle Türen, Frequenz-Jäger, Treppe des Schicksals.
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

Dieses Projekt wurde mit dem **Agentic Tester V4** (autonomes KI-Testsystem) validiert:
- **Test-Umfang:** 1000+ automatisierte Aktionen in DE/EN Sessions.
- **Status:** 0 Crashes, stabile Audio-Engine, korrekte Lokalisierung.
- **Ergebnis:** Alle Menüpfade und Kernmechaniken sind stabil.

## 🛠️ Entwicklung

Das Spiel basiert auf **Pygame** und nutzt eine benutzerdefinierte Audio-Engine für präzise Stereo-Positionierung und Sprachausgabe.

- **Audio-Engine:** `core/audio.py` (Tolk/SAPI)
- **Lokalisierung:** `core/localization.py`
- **Spiele-Logik:** `games/` Verzeichnis

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

## 🔗 Links

- **Repository:** [https://github.com/Lauju1909/Mini_Game_Sammlungv1.0](https://github.com/Lauju1909/Mini_Game_Sammlungv1.0)
- **Releases:** [Download v1.6](https://github.com/Lauju1909/Mini_Game_Sammlungv1.0/releases)

---
*Entwickelt für das Advanced Agentic Coding Team von Google Deepmind.*
