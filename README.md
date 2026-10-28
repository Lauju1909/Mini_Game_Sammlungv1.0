# Audio Studio Tycoon: Mini-Game-Sammlung v1.3.0

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: v1.3.0](https://img.shields.io/badge/Version-v1.3.0-green.svg)](version.json)
[![Accessibility: 100% Blind Accessible](https://img.shields.io/badge/Accessibility-100%25%20Blind%20Accessible-brightgreen.svg)]()
[![Games: 75 Mini-Games](https://img.shields.io/badge/Games-75%20Mini--Games-orange.svg)]()

Willkommen bei der **Mini-Game-Sammlung**, einer massiven Sammlung von **75 barrierefreien Audio-Minispielen**, die speziell für blinde und sehbehinderte Spieler sowie für Liebhaber von Audio-Spielen entwickelt wurden.

---

## 🌟 Features

- **Vollständige Barrierefreiheit:** 100% spielbar ohne visuelles Feedback über Gehör und Akustik.
- **75 abwechslungsreiche Minispiele in 5 Kategorien:**
  - **Action & Reaktion (30 Spiele):** z. B. Audio-Elfmeter, DJ-Turntable, Beat-Reaktor, Stereo-Münzfang, Ton-Jäger, Bomben-Entschärfer, Tasten-Gewitter, Schnellwähler, Maulwurf-Meister, Rhythmus-König, Reaktions-Blitz, Audio-Bogenschießen Pro, Rhythmus-Schmiede, Audio-Verteidigung, Audio-Bosskampf, Audio-Rennfahrer, Audio-Frosch, Audio-Mückenjagd, Audio-Kellner, Audio-Dart, Audio-Raumschiff, Beat-Matcher, Audio-Ping-Pong, Audio-Balance, Audio-Hürdenlauf, Fabrik-Prüfung, Audio-Jongleur, Audio-Scharfschütze, Morse-Läufer.
  - **Logik & Gedächtnis (17 Spiele):** z. B. Audio-Alchemie, Klang-Memory, Simon Says, Raum-Gedächtnis, Code-Knacker, Zahlen-Raten, Tresor-Knacker, Drehscheiben-Meister, Mathe-Blitz, Tickende Uhren, Tonhöhen-Meister, Klang-Weber, Audio-Tonfolge, Minenräumer, Schiffe-Versenken, Audio-Türsteher, Audio-Morsen.
  - **Navigation & Erkundung (12 Spiele):** z. B. Audio-Geisterjagd, Das goldene Mikrofon, Audio-Labyrinth, Echolot, Die blinde Farm, Weltraum-Flug, Tier-Radar, Geheimnisvolle Türen, Frequenz-Jäger, Treppe des Schicksals, U-Boot-Sonar, Audio-Weichensteller.
  - **Sprache & Wissen (10 Spiele):** z. B. Vogelstimmen-Erkennung, Wort-Schlange, Geräusche-Quiz, Buchstaben-Salat, Hauptstadt-Jäger, Audio-Kopfrechnen, Schlossknacker, Audio-Fechter, Audio-Holzfäller, Audio-Senso.
  - **Simulation & Spaß (6 Spiele):** z. B. Audio-Barista, Audio-Angeln, Audio-Bowling, Schere-Stein-Papier Extreme, Spielautomat, Echo-Jäger.
- **Universeller Tutorial-Modus:** Alle 75 Spiele verfügen über sprachgeführte Einführungen bei der ersten Runde (überspringbar mit ESC oder Enter).
- **Lückenlose Visualisierungen (`draw`):** Jedes einzelne Spiel besitzt eine moderne grafische Darstellung für sehende Mitspieler und Zuschauer.
- **Sanftes Menü-Scrolling & Playlist-Queue:** Automatische Bildlaufleiste für lange Spiellisten und visuelle `[✓]` Kennzeichnung für vorgemerkte Playlists.
- **Zufallsspiel-Modus:** Ein Klick im Hauptmenü wählt ein Überraschungsspiel aus allen 75 Titeln.
- **Screenreader-Integration:** Unterstützt NVDA, JAWS, OneCore und SAPI via modernem Prism-Audiosystem (prism.dll).
- **Vollständig zweisprachig:** Volle Lokalisierung für **Deutsch** und **Englisch**.
- **Mehrspielermodus:** Lokal an einem PC mit bis zu 4 Spielern und Session-Ranglisten.

---

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

---

## 🎮 Steuerung

- **Pfeiltasten:** Navigieren in Menüs und Steuern in Spielen (Links, Rechts, Oben, Unten).
- **Enter / Leertaste:** Bestätigen / Aktion ausführen.
- **ESC:** Zurück zum Menü / Spiel abbrechen.
- **Zahlen 1-9:** Eingabe in Quiz- und Rechenspielen.
- **F8 / Strg + L (Ctrl + L):** **Sprache blitzschnell umschalten** (Deutsch <-> English) mit sofortiger Sprachausgabe und Menü-Aktualisierung.

### 🌐 Schnelle Sprachumschaltung & Hotkey (Language Switching)
In der **Mini-Game-Sammlung** kannst du die Sprache des Spiels jederzeit blitzschnell wechseln:
- **Tastenkombination / Hotkey:** Drücke **`F8`** oder **`Strg + L`** (bzw. **`Ctrl + L`**), um das Spiel sofort an jeder beliebigen Stelle (im Hauptmenü, in Kategorien, in der Spieleliste oder während des Spielens) zwischen **Deutsch** und **Englisch** umzuschalten.
- **Akustische Ansage:** Der Screenreader meldet sofort *"Sprache auf Deutsch gestellt."* bzw. *"Language set to English."* und liest das aktuelle Menü direkt in der neuen Sprache vor.
- **Menü-Steuerung:** Alternativ lässt sich die Sprache über das Menü unter **Einstellungen (`Settings`) -> Sprache (`Language`)** mit Enter oder Pfeiltasten umschalten.
- **Dauerhafte Speicherung:** Die gewählte Sprache wird automatisch in `data/settings.json` gespeichert und bleibt beim nächsten Spielstart erhalten.

#### 🌐 English: Quick Language Switch
- Press **`F8`** or **`Ctrl + L`** anytime to instantly toggle between **English** and **German**.
- The screenreader announces the change immediately and refreshes all active menu items.
- Your language preference is automatically saved to `data/settings.json`.

---

## ✅ Quality Assurance & Verifikation

- **Test-Suite:** `python tools/deep_test_all_75.py`
- **Ergebnis:** Alle 75 Spiele initialisieren fehlerfrei, durchlaufen Tutorials, Game-Loops, Eingaben und Grafikausgaben ohne Exceptions.

---

## 📄 Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
