import os
import shutil
import json
from datetime import datetime
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.db import get_connection

TYPE_DIR_MAP = {
    "pcap": "artifacts/pcaps",
    "loot": "artifacts/loot",
    "transcript": "artifacts/transcripts",
    "report": "artifacts/reports",
}

BASE = os.path.expanduser("~/BirdsNest/burrow-data")


def ingest_artifact(artifact_path, artifact_type, host, tags, summary, exercise):
    if artifact_type not in TYPE_DIR_MAP:
        raise ValueError(
            f"Unknown artifact type '{artifact_type}'. "
            f"Valid types: {', '.join(TYPE_DIR_MAP.keys())}"
        )

    timestamp = datetime.now().isoformat()
    date_str = datetime.now().strftime("%Y-%m-%d")

    subdir = TYPE_DIR_MAP[artifact_type]
    dest_dir = os.path.join(BASE, subdir, date_str, exercise)
    os.makedirs(dest_dir, exist_ok=True)

    filename = os.path.basename(artifact_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(artifact_path, dest_path)

    sidecar = {
        "timestamp": timestamp,
        "type": artifact_type,
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
        (artifact_type, filename, timestamp, host, json.dumps(tags), summary, dest_path, exercise),
    )
    conn.commit()
    conn.close()

    print(f"[ingest_artifact] Ingested: {dest_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_path")
    parser.add_argument("--type", dest="artifact_type", required=True,
                        choices=list(TYPE_DIR_MAP.keys()),
                        help="Artifact type: pcap, loot, transcript, report")
    parser.add_argument("--host", default="unknown")
    parser.add_argument("--tags", nargs="+", default=[])
    parser.add_argument("--summary", default="")
    parser.add_argument("--exercise", default="general")
    args = parser.parse_args()

    ingest_artifact(
        args.artifact_path,
        args.artifact_type,
        args.host,
        args.tags,
        args.summary,
        args.exercise,
    )
