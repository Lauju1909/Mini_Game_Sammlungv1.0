import os
import zipfile

def create_zip():
    mgs_dir = r"C:\Users\lauri\.gemini\antigravity\scratch\Mini_Game_Sammlung"
    zip_name = os.path.join(mgs_dir, "Audio_Studio_Tycoon_v1.6.zip")
    
    include_files = [
        "main.py", "README.md", "Tolk.dll", "nvdaControllerClient64.dll", "run_game.bat"
    ]
    include_dirs = [
        "core", "games", "assets", "data"
    ]
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in include_files:
            file_path = os.path.join(mgs_dir, f)
            if os.path.exists(file_path):
                zf.write(file_path, f)
        
        for d in include_dirs:
            dir_path = os.path.join(mgs_dir, d)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    if "__pycache__" in root:
                        continue
                    for file in files:
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, mgs_dir)
                        zf.write(abs_path, rel_path)
    
    print(f"Zip created: {zip_name}")

if __name__ == "__main__":
    create_zip()
