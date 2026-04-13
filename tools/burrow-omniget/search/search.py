import os
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db.db import get_connection

DIVIDER = "-" * 90


def format_tags(tags_json):
    try:
        tags = json.loads(tags_json)
        return ", ".join(tags) if tags else "—"
    except Exception:
        return tags_json or "—"


def print_result(row):
    id_, type_, source, timestamp, host, tags, summary, path, exercise = row
    print(DIVIDER)
    print(f"  ID       : {id_}")
    print(f"  Type     : {type_}")
    print(f"  Host     : {host}")
    print(f"  Exercise : {exercise}")
    print(f"  Tags     : {format_tags(tags)}")
    print(f"  Summary  : {summary or '—'}")
    print(f"  Source   : {source}")
    print(f"  Time     : {timestamp}")
    print(f"  Path     : {path}")


def search(type_=None, host=None, exercise=None, tags=None, date=None, limit=20):
    conn = get_connection()

    query = "SELECT id, type, source, timestamp, host, tags, summary, path, exercise FROM evidence WHERE 1=1"
    params = []

    if type_:
        query += " AND type = ?"
        params.append(type_)

    if host:
        query += " AND host = ?"
        params.append(host)

    if exercise:
        query += " AND exercise = ?"
        params.append(exercise)

    if date:
        query += " AND timestamp LIKE ?"
        params.append(f"{date}%")

    if tags:
        tag_clauses = " OR ".join(["tags LIKE ?" for _ in tags])
        query += f" AND ({tag_clauses})"
        for tag in tags:
            params.append(f"%{tag}%")

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\n[search] No results found.\n")
        return

    print(f"\n[search] {len(rows)} result(s) found:\n")
    for row in rows:
        print_result(row)
    print(DIVIDER)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search the Burrow OmniGet evidence database."
    )
    parser.add_argument("--type", dest="type_", default=None,
                        help="Filter by type: screenshot, pcap, loot, transcript, report, note")
    parser.add_argument("--host", default=None,
                        help="Filter by hostname")
    parser.add_argument("--exercise", default=None,
                        help="Filter by exercise/engagement label")
    parser.add_argument("--tags", nargs="+", default=None,
                        help="Filter by tags (match any)")
    parser.add_argument("--date", default=None,
                        help="Filter by date prefix, e.g. 2026-04-13")
    parser.add_argument("--limit", type=int, default=20,
                        help="Max results to return (default: 20)")
    args = parser.parse_args()

    search(
        type_=args.type_,
        host=args.host,
        exercise=args.exercise,
        tags=args.tags,
        date=args.date,
        limit=args.limit,
    )
