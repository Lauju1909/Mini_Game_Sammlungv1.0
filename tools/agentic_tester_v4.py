import sys
import os
import time
import json
import random
import traceback
from collections import deque

# Pfad-Management
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

try:
    from core.localization import get_text as _
    import core.localization as localization
    from main import MiniGameCollection as GameCollection
except ImportError as e:
    print(f"KRITISCHER FEHLER: Projektmodule konnten nicht geladen werden ({e}).")
    print(f"Root-Pfad: {ROOT_DIR}")
    sys.exit(1)

class BaseEnvironment:
    """Basis-Schnittstelle für ein zu testendes Projekt."""
    def get_state(self):
        raise NotImplementedError()
    
    def perform_action(self, action):
        raise NotImplementedError()
    
    def is_alive(self):
        raise NotImplementedError()

class MiniGameEnv(BaseEnvironment):
    """Adapter für die Mini-Game-Sammlung."""
    def __init__(self, lang="de"):
        localization.set_language(lang)
        self.game = GameCollection()
        self.last_tts = []
        self.last_logs = []
        
        # Mock Audio - We use the REAL AudioManager logic but mock the output level
        self.game.audio.tolk_active = True
        class MockTolk:
            def __init__(self, tts_list):
                self.tts_list = tts_list
                self.speaking = False
            def Tolk_Output(self, text, interrupt):
                self.tts_list.append({
                    "text": text,
                    "time": time.time(),
                    "interrupt": interrupt
                })
                print(f"[AGENT SENSOR] OUTPUT: {text} (Interrupt: {interrupt})")
                return True
            def Tolk_IsSpeaking(self):
                return False
            def Tolk_Silence(self):
                return True
            def Tolk_Unload(self):
                return True
            def Tolk_IsLoaded(self):
                return True
        
        self.game.audio.tolk = MockTolk(self.last_tts)
        self.game.audio.play_sound = lambda x, **kwargs: None
        self.game.audio.play_tone = lambda frequency, duration_ms=500, volume=None, pan=0.0, **kwargs: None

    def get_state(self):
        """Extrahiert den aktuellen Zustand des Spiels."""
        # Zustand besteht aus: Aktuellem Menü-Titel, Optionen und letztem TTS
        current_menu_title = "Unknown"
        if hasattr(self.game.menu, 'menu_stack') and self.game.menu.menu_stack:
            current_menu_title = self.game.menu.menu_stack[-1][1]
            
        options = []
        if self.game.menu.current_menu:
            options = [item.get("id", item.get("label", "???")) for item in self.game.menu.current_menu]
            
        # Wenn ein Spiel läuft, ist der Zustand das Spiel selbst
        game_active = self.game.current_game is not None
        game_id = self.game.current_game.game_id if game_active else "Menu"
        
        return {
            "game_id": game_id,
            "menu_title": current_menu_title,
            "options": options,
            "last_tts": self.last_tts[-1]["text"] if self.last_tts else ""
        }

    def perform_action(self, key_name):
        """Simuliert einen Tastendruck."""
        import pygame
        key_map = {
            "UP": pygame.K_UP, "DOWN": pygame.K_DOWN, "RETURN": pygame.K_RETURN, "ESCAPE": pygame.K_ESCAPE,
            "SPACE": pygame.K_SPACE, "LEFT": pygame.K_LEFT, "RIGHT": pygame.K_RIGHT,
            "1": pygame.K_1, "2": pygame.K_2, "3": pygame.K_3, "4": pygame.K_4, "5": pygame.K_5
        }
        
        code = key_map.get(key_name.upper())
        if code:
            # Wir rufen die Event-Logik direkt auf
            class FakeEvent:
                def __init__(self, key): 
                    self.key = key
                    self.type = pygame.KEYDOWN
                    self.unicode = chr(key) if key < 256 else ""
            
            event = FakeEvent(code)
            self.game.handle_input(event)
            
            # Einen Frame simulieren
            if self.game.current_game:
                self.game.current_game.update()
        else:
            print(f"[AGENT ERROR] Unbekannte Taste: {key_name}")

    def is_alive(self):
        return self.game.running

class AgentBrain:
    """Die 'KI' des Testers. Merkt sich Pfade und entscheidet autonom."""
    def __init__(self, memory_file="agent_memory.json"):
        self.memory_file = memory_file
        self.graph = {} # State-Hash -> {actions: {key: next_state_hash}, visit_count: N}
        self.load_memory()
        self.path_history = []

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.graph = json.load(f)
            except: self.graph = {}

    def save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=2, ensure_ascii=False)

    def get_state_hash(self, state):
        # Einfacher Hash aus ID und Optionen
        return f"{state['game_id']}|{state['menu_title']}|{','.join(state['options'])}"

    def choose_action(self, state):
        s_hash = self.get_state_hash(state)
        if s_hash not in self.graph:
            self.graph[s_hash] = {"actions": {}, "visit_count": 0, "tts_history": []}
        
        node = self.graph[s_hash]
        node["visit_count"] += 1
        if state["last_tts"] not in node["tts_history"]:
            node["tts_history"].append(state["last_tts"])

        # Mögliche Aktionen
        possible_keys = ["UP", "DOWN", "RETURN", "ESCAPE", "SPACE", "LEFT", "RIGHT", "1", "2", "3", "4", "5"]
        
        # In Spielen öfter Action-Keys probieren
        if state["game_id"] != "Menu":
            # Curiosity Bonus für untried keys im Spiel
            untried = [k for k in possible_keys if k not in node["actions"]]
            if untried:
                return random.choice(untried)
            return random.choice(["SPACE", "LEFT", "RIGHT", "UP", "DOWN", "ESCAPE"])
        
        # Im Menü: Gezielte Exploration
        untried = [k for k in possible_keys if k not in node["actions"]]
        if untried and random.random() < 0.8:
            return random.choice(untried)
        
        # Sonst: Wähle die Aktion, die am seltensten zu bekannten Zuständen führte (Exploration)
        action = random.choice(possible_keys)
        
        # Suizid-Prävention: Nicht RETURN drücken, wenn wir auf "Beenden" stehen
        if action == "RETURN":
            quitting_terms = ["beenden", "quit", "exit", "schließen", "beendet"]
            last_tts_lower = state["last_tts"].lower()
            if any(term in last_tts_lower for term in quitting_terms):
                print(f"[AGENT] Suizid verhindert! Wechsle von RETURN zu DOWN.")
                return "DOWN"
        
        return action

    def record_transition(self, state_before, action, state_after):
        h_before = self.get_state_hash(state_before)
        h_after = self.get_state_hash(state_after)
        self.graph[h_before]["actions"][action] = h_after

class AgenticTesterV4:
    """Der Haupt-Controller für den autonomen Test."""
    def __init__(self, env):
        self.env = env
        self.brain = AgentBrain()
        self.errors = []
        self.start_time = time.time()

    def run(self, max_steps=500, session_name="Unnamed"):
        print("\n" + "="*50)
        print(f"AGENTIC TESTER V4 - SESSION: {session_name}")
        print("="*50)
        
        step = 0
        consecutive_stagnation = 0
        last_state_hash = ""
        
        try:
            while step < max_steps and self.env.is_alive():
                state_before = self.env.get_state()
                current_hash = self.brain.get_state_hash(state_before)
                
                # Stagnations-Erkennung (Agent drückt nur UP/DOWN im Kreis)
                if current_hash == last_state_hash:
                    consecutive_stagnation += 1
                else:
                    consecutive_stagnation = 0
                last_state_hash = current_hash
                
                if consecutive_stagnation > 15:
                    action = "ESCAPE" # Befreiungsschlag
                    consecutive_stagnation = 0
                else:
                    action = self.brain.choose_action(state_before)
                
                print(f"[{session_name}][{step}] State: {state_before['game_id']} | Action: {action}")
                
                self._audit_speech_stomping()
                
                try:
                    self.env.perform_action(action)
                except Exception as e:
                    error_msg = f"CRASH in {state_before['game_id']} with {action}: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    self.errors.append({
                        "type": "CRASH",
                        "session": session_name,
                        "state": state_before,
                        "action": action,
                        "trace": traceback.format_exc()
                    })
                    self.env.game.setup_main_menu()
                time.sleep(0.1) # Etwas langsamer für realistischere Tests
                
                state_after = self.env.get_state()
                self.brain.record_transition(state_before, action, state_after)
                
                step += 1
                if step % 50 == 0:
                    self.brain.save_memory()

        except KeyboardInterrupt:
            print("\nTest vom Benutzer unterbrochen.")
        
        self.brain.save_memory()

    def _audit_speech_stomping(self):
        if len(self.env.last_tts) < 2: return
        t2 = self.env.last_tts[-1]
        t1 = self.env.last_tts[-2]
        diff = t2["time"] - t1["time"]
        if diff < 0.15 and t2["interrupt"]:
            msg = f"SPEECH STOMPING: '{t2['text']}' unterbrach '{t1['text']}' nach {diff:.3f}s"
            if msg not in [e.get("msg") for e in self.errors]:
                print(f"[WARN] {msg}")
                self.errors.append({"type": "STOMPING", "msg": msg, "time": t2["time"]})

    def generate_final_report(self):
        duration = time.time() - self.start_time
        report_path = os.path.join(ROOT_DIR, "agent_report_final.md")
        print(f"[AGENT] Generiere Abschlussbericht: {report_path}")
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"# Agentic Tester V4 - Global QA Report\n\n")
                f.write(f"- **Datum:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"- **Dauer gesamt:** {duration:.1f}s\n")
                f.write(f"- **Explorierte Zustände:** {len(self.brain.graph)}\n")
                f.write(f"- **Gesamtfehler:** {len(self.errors)}\n\n")
                
                f.write("## 🛑 Kritische Fehler (Crashes)\n")
                crashes = [e for e in self.errors if e["type"] == "CRASH"]
                if not crashes: 
                    f.write("Keine Crashes gefunden. Das Spiel ist stabil! ✅\n")
                else:
                    for c in crashes:
                        f.write(f"### {c['state']['game_id']} (Session: {c['session']})\n")
                        f.write(f"- **Aktion:** `{c['action']}`\n")
                        f.write(f"```python\n{c['trace']}\n```\n\n")
                    
                f.write("## 🔊 Audio-Inkonsistenzen (Stomping)\n")
                stomps = [e for e in self.errors if e["type"] == "STOMPING"]
                if not stomps: 
                    f.write("Kein relevantes Speech-Stomping erkannt. ✅\n")
                else:
                    for s in stomps:
                        f.write(f"- {s['msg']}\n")
                    
                f.write("\n## 🗺️ Wissens-Graph (Auszug)\n")
                f.write("| Zustand | Besuche | Bekannte TTS-Ansagen |\n")
                f.write("| :--- | :--- | :--- |\n")
                # Sortiere nach Besuchen
                sorted_nodes = sorted(self.brain.graph.items(), key=lambda x: x[1]['visit_count'], reverse=True)
                for s_hash, data in sorted_nodes[:30]: 
                    parts = s_hash.split("|")
                    g_id = parts[0] if len(parts) > 0 else "?"
                    m_title = parts[1] if len(parts) > 1 else "?"
                    f.write(f"| {g_id} / {m_title} | {data['visit_count']} | {', '.join(data['tts_history'][:2])} |\n")
            
            print(f"[AGENT] Bericht erfolgreich gespeichert unter: {report_path}")
        except Exception as e:
            print(f"[AGENT ERROR] Bericht konnte nicht geschrieben werden: {e}")

if __name__ == "__main__":
    # Iterative Test-Suite
    print("[START] Agentic Tester V4 Suite")
    
    # Reset memory for fresh start
    if os.path.exists("agent_memory.json"):
        os.remove("agent_memory.json")
    
    # 1. Lauf: Deutsch
    env_de = MiniGameEnv(lang="de")
    tester = AgenticTesterV4(env_de)
    tester.run(max_steps=300, session_name="DE_Exploration")
    
    # 2. Lauf: Englisch
    env_en = MiniGameEnv(lang="en")
    tester.env = env_en
    tester.run(max_steps=300, session_name="EN_Exploration")
    
    # 3. Lauf: Stress-Test
    tester.run(max_steps=400, session_name="Stress_Test")
    
    tester.generate_final_report()
    print("[FINISH] Agentic Tester V4 Suite")
