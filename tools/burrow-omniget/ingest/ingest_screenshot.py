import os
import sys
import json
import shutil
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.db import get_connection

BASE = os.path.expanduser("~/BirdsNest/burrow-data/screenshots")

def ingest_screenshot(image_path, host, tags, summary, exercise, sidecar_path=None):
    timestamp = datetime.now().isoformat()
    date_str = datetime.now().strftime("%Y-%m-%d")
    dest_dir = os.path.join(BASE, date_str, exercise)
    os.makedirs(dest_dir, exist_ok=True)

    filename = os.path.basename(image_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(image_path, dest_path)

    sidecar = {
        "timestamp": timestamp,
        "host": host,
        "tags": tags,
        "summary": summary,
        "exercise": exercise,
        "path": dest_path
    }
    sidecar_out = dest_path.replace(".png", ".json").replace(".jpg", ".json")
    with open(sidecar_out, "w") as f:
        json.dump(sidecar, f, indent=2)

    conn = get_connection()
    conn.execute("""
        INSERT INTO evidence (type, source, timestamp, host, tags, summary, path, exercise)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ("screenshot", filename, timestamp, host, json.dumps(tags), summary, dest_path, exercise))
    conn.commit()
    conn.close()
    print(f"[ingest_screenshot] Ingested: {dest_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    parser.add_argument("--host", default="jynx13")
    parser.add_argument("--tags", nargs="+", default=[])
    parser.add_argument("--summary", default="")
    parser.add_argument("--exercise", default="general")
    args = parser.parse_args()
    ingest_screenshot(args.image_path, args.host, args.tags, args.summary, args.exercise)
