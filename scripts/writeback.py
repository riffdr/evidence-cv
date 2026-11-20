#!/usr/bin/env python3
"""Record an application in data/history.json and its gaps in data/gap-log.md.

    python3 scripts/writeback.py --file output/2026-01-01-acme-senior-fe/writeback.json

writeback.json:
  {
    "company": "...", "role": "...", "url": "...",
    "verdict": "Apply|Maybe|Skip", "score": 80, "outcome": "tailored",
    "gaps": [{"requirement": "...", "level": "none", "cost": "..."}]
  }

Re-running with the same URL (or, when the URL is empty, the same company and
role) updates the existing entry instead of appending a duplicate — that is how
"tailored" becomes "applied".

Standard library only. experience.yaml is never touched here: edit it explicitly.
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

FIELDS = ("company", "role", "url", "score", "verdict", "outcome")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", required=True, help="writeback JSON payload")
    ap.add_argument("--data", default=str(REPO / "data"), help="data directory")
    args = ap.parse_args()

    data_dir = Path(args.data).expanduser()
    if not data_dir.exists():
        sys.exit(f"error: data directory not found: {data_dir}\nRun scripts/init.py first.")

    payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    for key in ("company", "role"):
        if not payload.get(key):
            print(f"missing '{key}'", file=sys.stderr)
            return 1

    today = datetime.date.today().isoformat()
    history_path = data_dir / "history.json"
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []

    url = (payload.get("url") or "").strip()

    def same(entry: dict) -> bool:
        if url:
            return entry.get("url") == url
        return (entry.get("company") == payload["company"]
                and entry.get("role") == payload["role"])

    existing = next((e for e in history if same(e)), None)
    if existing is None:
        entry = {"date": today}
        entry.update({k: payload.get(k) for k in FIELDS if k != "date"})
        entry["outcome"] = payload.get("outcome", "tailored")
        history.append(entry)
    else:
        for key in FIELDS:
            if payload.get(key) is not None:
                existing[key] = payload[key]
        existing["date"] = today

    history_path.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    gaps = payload.get("gaps", [])
    if gaps:
        gap_path = data_dir / "gap-log.md"
        existing_text = gap_path.read_text(encoding="utf-8") if gap_path.exists() else "# Gap log\n"
        if not existing_text.endswith("\n"):
            existing_text += "\n"
        lines = [f"\n## {today} - {payload['company']} - {payload['role']}\n"]
        for gap in gaps:
            cost = f" (cost: {gap['cost']})" if gap.get("cost") else ""
            lines.append(f"- {gap['requirement']} [{gap.get('level', 'none')}]{cost}\n")
        gap_path.write_text(existing_text + "".join(lines), encoding="utf-8")

    action = "updated" if existing else "added"
    print(f"OK {action} history={len(history)} gaps_added={len(gaps)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
