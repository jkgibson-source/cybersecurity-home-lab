import os
import shutil
import json
from datetime import datetime
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.db import get_connection

BASE = os.path.expanduser("~/BirdsNest/burrow-data")


def ingest_note(note_path, host, tags, summary, exercise):
    if not note_path.endswith(".md"):
        raise ValueError(f"Expected a markdown (.md) file, got: {note_path}")

    timestamp = datetime.now().isoformat()
    date_str = datetime.now().strftime("%Y-%m-%d")

    dest_dir = os.path.join(BASE, "notes", date_str, exercise)
    os.makedirs(dest_dir, exist_ok=True)

    filename = os.path.basename(note_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(note_path, dest_path)

    sidecar = {
        "timestamp": timestamp,
        "type": "note",
        "host": host,
        "tags": tags,
        "summary": summary,
        "exercise": exercise,
        "path": dest_path,
    }
    sidecar_out = os.path.splitext(dest_path)[0] + ".json"
    with open(sidecar_out, "w") as f:
        json.dump(sidecar, f, indent=2)

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO evidence (type, source, timestamp, host, tags, summary, path, exercise)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("note", filename, timestamp, host, json.dumps(tags), summary, dest_path, exercise),
    )
    conn.commit()
    conn.close()

    print(f"[ingest_note] Ingested: {dest_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("note_path", help="Path to the markdown (.md) file to ingest")
    parser.add_argument("--host", default="unknown")
    parser.add_argument("--tags", nargs="+", default=[])
    parser.add_argument("--summary", default="")
    parser.add_argument("--exercise", default="general")
    args = parser.parse_args()

    ingest_note(
        args.note_path,
        args.host,
        args.tags,
        args.summary,
        args.exercise,
    )
