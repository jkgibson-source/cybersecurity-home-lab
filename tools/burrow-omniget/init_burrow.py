import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from db.db import init_db

BASE = os.path.expanduser("~/BirdsNest/burrow-data")

DIRS = [
    "screenshots",
    "artifacts/pcaps",
    "artifacts/loot",
    "artifacts/transcripts",
    "artifacts/reports",
    "notes",
    "wazuh",
]

def init_burrow():
    print(f"[init] Creating Burrow data tree at {BASE}")
    for d in DIRS:
        path = os.path.join(BASE, d)
        os.makedirs(path, exist_ok=True)
        print(f"  [+] {path}")
    print("[init] Folder structure complete.")
    init_db()
    print("[init] Burrow initialized successfully.")

if __name__ == "__main__":
    init_burrow()
