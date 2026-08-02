import os
import subprocess
import json

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v_path = os.path.join(APP_DIR, "version.json")
try:
    with open(v_path, "r", encoding="utf-8") as f:
        v_data = json.load(f)
        VERSION = v_data.get("version", "1.1.0")
except Exception:
    VERSION = "1.1.0"

EXE_NAME = f"Mini_Game_Sammlung_v{VERSION}.exe"

def build():
    os.chdir(APP_DIR)
    
    print(f"Erstelle PyInstaller Single-File Build für version {VERSION}...")
    cmd = [
        "python", "-m", "PyInstaller", "main.py", "--noconfirm", "--onefile",
        "--name", f"Mini_Game_Sammlung_v{VERSION}",
        "--add-data", "Tolk.dll;.",
        "--add-data", "nvdaControllerClient64.dll;.",
        "--add-data", "assets;assets",
        "--add-data", "core;core",
        "--add-data", "games;games",
        "--add-data", "version.json;.",
        "--hidden-import", "urllib.request",
        "--hidden-import", "urllib.error"
    ]
    
    subprocess.run(cmd, check=True)
    
    dist_exe = os.path.join(APP_DIR, "dist", EXE_NAME)
    if os.path.exists(dist_exe):
        size_mb = os.path.getsize(dist_exe) / (1024 * 1024)
        print(f"ERFOLG: Single-File Executable erfolgreich erstellt: {dist_exe} ({size_mb:.2f} MB)")
    else:
        raise FileNotFoundError(f"EXE wurde nicht gefunden unter {dist_exe}")

if __name__ == "__main__":
    build()
