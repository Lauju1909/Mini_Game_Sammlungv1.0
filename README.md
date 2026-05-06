# Audio Studio Tycoon: Game Pack v1.4

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.4-green.svg)
![Accessibility](https://img.shields.io/badge/Accessibility-100%25%20Blind%20Accessible-brightgreen.svg)

Willkommen beim **Audio Studio Tycoon: Game Pack**, einer Sammlung von über 30 barrierefreien Mini-Games, die speziell für blinde und sehbehinderte Spieler sowie für Liebhaber von Audio-Spielen entwickelt wurden.

## 🌟 Features

- **Vollständige Barrierefreiheit:** 100% spielbar ohne visuelles Feedback.
- **Screenreader-Integration:** Unterstützt NVDA, JAWS und andere via Tolk (SAPI Fallback).
- **Zweisprachig:** Volle Unterstützung für **Deutsch** und **Englisch**.
- **Vielseitige Kategorien:**
  - **Action & Reaktion:** Beat-Reaktor, Stereo-Münzfang, Bomben-Entschärfer.
  - **Logik & Gedächtnis:** Sound-Memo, Simon Says, Code-Knacker.
  - **Navigation & Erkundung:** Audio-Labyrinth, Echolot, Die blinde Farm.
  - **Sprache & Wissen:** Wort-Schlange, Geräusche-Quiz, Hauptstadt-Jäger.
  - **Simulation & Spaß:** Audio-Bowling, Schere-Stein-Papier, Audio-Slots.
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

## 🛠️ Entwicklung

Das Spiel basiert auf **Pygame** und nutzt eine benutzerdefinierte Audio-Engine für präzise Stereo-Positionierung und Sprachausgabe.

- **Audio-Engine:** `core/audio.py` (Tolk/SAPI)
- **Lokalisierung:** `core/localization.py`
- **Spiele-Logik:** `games/` Verzeichnis

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---
*Entwickelt für das Advanced Agentic Coding Team von Google Deepmind.*
