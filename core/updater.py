"""
Auto-Updater Modul für Mini Game Sammlung.
Überprüft Releases auf GitHub (Lauju1909/Mini_Game_Sammlungv1.0).
Lädt neuere Versionen herunter und bietet barrierefreies Feedback.
"""

import json
import threading
import urllib.request
from typing import Callable, Optional, Tuple, Dict

GITHUB_API = "https://api.github.com/repos/Lauju1909/Mini_Game_Sammlungv1.0/releases"
UPDATE_TIMEOUT = 10  # Sekunden


def parse_version(v_str: str) -> Tuple[Tuple[int, ...], str]:
    """Konvertiert Versions-Strings wie 'v1.1.0' oder '1.1.0-beta' in vergleichbare Tuples."""
    try:
        v_str = v_str.strip().lstrip("v")
        if "-" in v_str:
            core, suffix = v_str.split("-", 1)
        else:
            core = v_str
            suffix = "z_stable"
        
        parts = [int(x) for x in core.split(".") if x.isdigit()]
        while len(parts) < 3:
            parts.append(0)
        return (tuple(parts), suffix)
    except Exception:
        return ((0, 0, 0), "")


def fetch_releases(timeout: int = UPDATE_TIMEOUT) -> Optional[list]:
    """Holt Releases von der GitHub REST API. Gibt None bei Fehler zurück."""
    try:
        req = urllib.request.Request(
            f"{GITHUB_API}?per_page=10",
            headers={"User-Agent": "MGS-Updater/1.1"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as res:
            if res.status != 200:
                return None
            return json.loads(res.read().decode("utf-8"))
    except Exception as err:
        print(f"[Updater] Fehler beim Abrufen der Releases: {err}")
        return None


def get_latest_release() -> Optional[Dict]:
    """Ermittelt das neueste gültige Release."""
    releases = fetch_releases()
    if not releases:
        return None
    valid = [r for r in releases if not r.get("draft", False)]
    if not valid:
        return None
    valid.sort(key=lambda r: parse_version(r.get("tag_name", "0.0.0")), reverse=True)
    return valid[0]


def check_for_update(current_version: str) -> Tuple[bool, Optional[Dict]]:
    """Prüft, ob ein neueres Release verfügbar ist als current_version."""
    latest = get_latest_release()
    if not latest:
        return False, None
    
    latest_tag = latest.get("tag_name", "0.0.0")
    if parse_version(latest_tag) > parse_version(current_version):
        return True, latest
    return False, None


def check_for_update_async(current_version: str, callback: Callable[[bool, Optional[Dict]], None]):
    """Führt die Update-Prüfung asynchron in einem Hintergrund-Thread aus."""
    def worker():
        has_update, release_info = check_for_update(current_version)
        callback(has_update, release_info)
    
    t = threading.Thread(target=worker, daemon=True)
    t.start()
