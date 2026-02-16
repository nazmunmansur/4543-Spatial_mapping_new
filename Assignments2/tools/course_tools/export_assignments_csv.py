#!/usr/bin/env python3
"""
Docstring for tools.course_tools.export_assignments
python -m tools.course_tools.export_assignments_csv --root . --section 02
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import yaml

from .course_constants import META_NAME, LEGACY_DIRNAMES, is_hidden_path
from .course_paths import (
    resolve_course_root,
    resolve_assignments_root,
    resolve_sections,
)


FIELDS = ["course", "title", "type", "due", "points", "path"]


def parse_due(val) -> Optional[datetime]:
    if not val or str(val).lower() == "null":
        return None
    try:
        return datetime.fromisoformat(str(val))
    except Exception:
        return None


def is_under_legacy(path: Path) -> bool:
    return any(p.name.lower() in LEGACY_DIRNAMES for p in path.parents)


def load_meta(meta_path: Path) -> dict:
    with meta_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="export_assignments_csv", description="Export assignments.csv from meta.yaml under Assignments/.")
    ap.add_argument("--root", default=".", help="Course repo root (default: cwd).")
    ap.add_argument("--section", default=None, help="Only process one section (e.g. '02' or '02-Spatial_Data_Core').")
    ap.add_argument("--output", default="assignments.csv", help="Output CSV path (default: assignments.csv in repo root).")
    ap.add_argument("--include-undated", action="store_true", help="Include rows with no due date.")
    return ap


def main() -> int:
    args = build_parser().parse_args()

    course_root = resolve_course_root(args.root)
    assignments_root = resolve_assignments_root(course_root)
    sections = resolve_sections(assignments_root, args.section)

    rows: List[dict] = []

    for sec in sections:
        sec_name = sec.name

        for meta in sec.rglob(META_NAME):
            parent = meta.parent

            if is_hidden_path(parent):
                continue
            if is_under_legacy(parent):
                continue

            data = load_meta(meta)
            mtype = data.get("type", "")
            title = data.get("title", parent.name)
            due_raw = data.get("due", None)
            points = data.get("points", "")

            due_dt = parse_due(due_raw)
            if (due_dt is None) and (not args.include_undated):
                continue

            rows.append(
                {
                    "course": sec_name,
                    "title": title,
                    "type": mtype,
                    "due": "" if due_dt is None else due_dt.isoformat(timespec="minutes"),
                    "points": "" if points is None else str(points),
                    "path": parent.relative_to(course_root).as_posix(),
                }
            )

    # sort: undated last, then by due, then title
    def sort_key(r):
        return (r["due"] == "", r["due"], r["title"].lower())

    rows.sort(key=sort_key)

    out_path = (course_root / args.output) if not Path(args.output).is_absolute() else Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"✅ Exported {len(rows)} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())