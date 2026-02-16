#!/usr/bin/env python3
"""
Docstring for tools.course_tools.build_folder_readmees
python -m tools.course_tools.build_folder_readmes --root . --section 02 --dry-run
python -m tools.course_tools.build_folder_readmes --root . --section 02
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import yaml

from .course_constants import (
    META_NAME,
    HEADER_NAME,
    AUTOGEN_NAME,
    README_NAME,
    LEGACY_DIRNAMES,
    is_hidden_path,
)
from .course_paths import (
    resolve_course_root,
    resolve_assignments_root,
    resolve_sections,
    iter_groups,
)


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


def rel_link(from_folder: Path, target_folder: Path) -> str:
    return target_folder.relative_to(from_folder).as_posix()


def build_group_table(group: Path) -> str:
    NOW = datetime.now()
    items: List[dict] = []

    for meta in group.rglob(META_NAME):
        parent = meta.parent
        if is_hidden_path(parent):
            continue
        if is_under_legacy(parent):
            continue

        data = load_meta(meta)
        due_dt = parse_due(data.get("due"))
        if due_dt is None:
            continue

        items.append(
            {
                "title": data.get("title", parent.name),
                "type": data.get("type", ""),
                "due": due_dt,
                "points": "" if data.get("points") is None else str(data.get("points")),
                "path": rel_link(group, parent),
            }
        )

    if not items:
        return ""

    items.sort(key=lambda a: (a["due"], a["title"].lower()))

    lines = []
    lines.append("## 📅 Group Calendar\n")
    lines.append("| Status | Type | Item | Due | Points |")
    lines.append("|--------|------|------|-----|--------|")

    for a in items:
        late = a["due"] < NOW
        status = "🔴 LATE" if late else "🟢"
        title = f"**{a['title']}**" if late else a["title"]
        due = a["due"].strftime("%Y-%m-%d %H:%M")
        lines.append(f"| {status} | {a['type']} | [{title}]({a['path']}) | {due} | {a['points']} |")

    return "\n".join(lines) + "\n"


def assemble_readme(group: Path) -> str:
    parts: List[str] = []

    header = group / HEADER_NAME
    if header.exists():
        parts.append(header.read_text(encoding="utf-8").strip())

    autogen = group / AUTOGEN_NAME
    if autogen.exists():
        parts.append(autogen.read_text(encoding="utf-8").strip())

    # if nothing, at least return something sane
    if not parts:
        parts.append(f"# {group.name}\n")

    return "\n\n".join(parts).strip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="build_folder_readmes", description="Build group README.md + _autogen.md calendars from meta.yaml.")
    ap.add_argument("--root", default=".", help="Course repo root (default: cwd).")
    ap.add_argument("--section", default=None, help="Only process one section (e.g. '02' or '02-Spatial_Data_Core').")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be written, do not write.")
    return ap


def main() -> int:
    args = build_parser().parse_args()

    course_root = resolve_course_root(args.root)
    assignments_root = resolve_assignments_root(course_root)
    sections = resolve_sections(assignments_root, args.section)

    updated = 0

    for sec in sections:
        for group in iter_groups(sec, strict_numbered=True):
            table = build_group_table(group)
            if not table:
                continue

            autogen_path = group / AUTOGEN_NAME
            readme_path = group / README_NAME

            if args.dry_run:
                print(f"[dry-run] write {autogen_path}")
                print(f"[dry-run] write {readme_path}")
                updated += 1
                continue

            autogen_path.write_text(table, encoding="utf-8")
            readme_path.write_text(assemble_readme(group), encoding="utf-8")
            print(f"✅ Updated README in {group}")
            updated += 1

    print(f"Done. Updated {updated} group(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())