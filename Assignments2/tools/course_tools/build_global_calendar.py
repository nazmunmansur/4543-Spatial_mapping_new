#!/usr/bin/env python3
"""
Docstring for tools.course_tools.build_global_calendar
python -m tools.course_tools.build_global_calendar --root . --section 02
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import yaml

from .course_constants import META_NAME, LEGACY_DIRNAMES, is_hidden_path
from .course_paths import resolve_course_root, resolve_assignments_root, resolve_sections


def parse_due(val) -> Optional[datetime]:
    if not val or str(val).lower() == "null":
        return None
    try:
        return datetime.fromisoformat(str(val))
    except Exception:
        return None


def is_under_legacy(path: Path) -> bool:
    return any(p.name.lower() in LEGACY_DIRNAMES for p in path.parents)


def truncate_string(s: str, max_length: int = 40) -> str:
    return (s[: max_length - 3] + "...") if len(s) > max_length else s


def load_meta(meta_path: Path) -> dict:
    with meta_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="build_global_calendar", description="Build GLOBAL_CALENDAR.md from meta.yaml under Assignments/.")
    ap.add_argument("--root", default=".", help="Course repo root (default: cwd).")
    ap.add_argument("--section", default=None, help="Only process one section (e.g. '02' or '02-Spatial_Data_Core').")
    ap.add_argument("--output", default="GLOBAL_CALENDAR.md", help="Output markdown filename/path (default: GLOBAL_CALENDAR.md at repo root).")
    ap.add_argument("--include-undated", action="store_true", help="Include items with no due date (shows as blank).")
    return ap


def main() -> int:
    args = build_parser().parse_args()

    NOW = datetime.now()

    course_root = resolve_course_root(args.root)
    assignments_root = resolve_assignments_root(course_root)
    sections = resolve_sections(assignments_root, args.section)

    items: List[dict] = []

    for sec in sections:
        sec_name = sec.name
        for meta in sec.rglob(META_NAME):
            parent = meta.parent
            if is_hidden_path(parent):
                continue
            if is_under_legacy(parent):
                continue

            data = load_meta(meta)
            title = data.get("title", parent.name)
            mtype = data.get("type", "")
            points = data.get("points", "")
            due_dt = parse_due(data.get("due"))

            if due_dt is None and not args.include_undated:
                continue

            items.append(
                {
                    "course": sec_name,
                    "title": title,
                    "type": mtype,
                    "due": due_dt,
                    "points": "" if points is None else str(points),
                    "path": parent.relative_to(course_root).as_posix(),
                }
            )

    def sort_key(a):
        # undated last
        if a["due"] is None:
            return (1, "9999-99-99", a["title"].lower())
        return (0, a["due"].isoformat(), a["title"].lower())

    items.sort(key=sort_key)

    if not items:
        print("⚠️  No items found (check due dates / section filter).")
        return 0

    lines = []
    lines.append("# 📅 Global Assignment Calendar\n")
    lines.append("| Status | Course | Type | Title | Due | Points | Folder |")
    lines.append("|--------|--------|------|-------|-----|--------|--------|")

    for a in items:
        due_dt = a["due"]
        is_late = (due_dt is not None) and (due_dt < NOW)
        status = "🔴 LATE" if is_late else "🟢"

        due_str = "" if due_dt is None else due_dt.strftime("%Y-%m-%d %H:%M")
        folder_link = f"[{truncate_string(a['path'])}]({a['path']})"
        title = f"**{a['title']}**" if is_late else a["title"]

        lines.append(
            f"| {status} | {a['course']} | {a['type']} | {title} | {due_str} | {a['points']} | {folder_link} |"
        )

    out_path = (course_root / args.output) if not Path(args.output).is_absolute() else Path(args.output)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"✅ Wrote {out_path} ({len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())