import time
import subprocess
import sys

def run_tests():
    print("Starte Super-KI-Tests in Endlosschleife...")
    while True:
        try:
            result = subprocess.run([sys.executable, "-m", "pytest", "tests_super_qa", "-v"], capture_output=True, text=True)
            if result.returncode != 0:
                print("FEHLER GEFUNDEN! Repariere Code...")
                with open("qa_error.log", "a", encoding="utf-8") as f:
                    f.write(result.stdout)
                    f.write(result.stderr)
            else:
                print("Alle Fuzzing- und Edge-Case-Tests bestanden. Tolk/TTS simuliert. Warte auf nächsten Zyklus...")
            
        except Exception as e:
            print(f"Fehler im Test-Runner: {e}")
        time.sleep(5)

if __name__ == "__main__":
    run_tests()
