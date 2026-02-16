#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List

from rich import print

from .course_constants import (
    HEADER_NAME,
    AUTOGEN_NAME,
    README_NAME,
    META_NAME,
    PROTECTED_FILES,
    is_resource_file,
    classify_notebook_stem,
)
from .course_paths import (
    resolve_course_root,
    resolve_assignments_root,
    resolve_sections,
    iter_groups,
    iter_proto_groups,
    group_paths,
    root_level_notebooks,
    ensure_under,
)

# -----------------------------
# Naming helpers
# -----------------------------
def slug_title(stem: str) -> str:
    raw = re.sub(r"[_\-\s]+", " ", stem).strip()
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", raw) if p]
    if not parts:
        return "Untitled"
    parts = [p[0].upper() + p[1:] if len(p) > 1 else p.upper() for p in parts]
    return "_".join(parts)

def split_numbered(name: str) -> tuple[int, str] | None:
    m = re.match(r"^(?P<num>\d{2})-(?P<rest>.+)$", name)
    if not m:
        return None
    return int(m.group("num")), m.group("rest")

def next_atomic_number(lessons_dir: Path) -> int:
    nums: List[int] = []
    if lessons_dir.exists():
        for p in lessons_dir.iterdir():
            if p.is_dir():
                s = split_numbered(p.name)
                if s:
                    nums.append(s[0])
    return (max(nums) + 1) if nums else 1

# -----------------------------
# Templates
# -----------------------------
def tpl_group_readme(group_title: str) -> str:
    return f"# {group_title}\n\n## Overview\n\n- TODO\n"

def tpl_lesson_readme(title: str) -> str:
    return f"# {title}\n\n## Goals\n\n- TODO\n\n## Instructions\n\n- TODO\n"

def tpl_meta_lesson(title: str) -> str:
    return (
        "schema_version: 1\n"
        f"title: {title}\n"
        "type: assignment\n"
        "status: draft\n"
        "due: null\n"
        "points: null\n"
        "notebooks: []\n"
    )

def tpl_meta_assessments() -> str:
    return (
        "schema_version: 1\n"
        "title: Assessments\n"
        "type: assessment\n"
        "status: draft\n"
        "due: null\n"
        "points: null\n"
        "notebooks: []\n"
    )

def tpl_meta_resources() -> str:
    return (
        "schema_version: 1\n"
        "title: Resources\n"
        "type: resource\n"
        "status: draft\n"
        "files: []\n"
    )

# -----------------------------
# Writer
# -----------------------------
@dataclass
class Writer:
    dry_run: bool = True
    force: bool = False
    verbose: bool = False

    def mkdir(self, p: Path) -> None:
        if self.dry_run:
            print(f"[dry-run] mkdir -p {p}")
            return
        p.mkdir(parents=True, exist_ok=True)

    def write(self, p: Path, content: str = "") -> None:
        if p.exists() and not self.force:
            return
        if self.dry_run:
            action = "overwrite" if p.exists() else "create"
            print(f"[dry-run] {action} {p}")
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def move(self, src: Path, dst: Path) -> None:
        if self.dry_run:
            print(f"[dry-run] move {src} -> {dst}")
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

# -----------------------------
# Scaffold actions
# -----------------------------
def ensure_group_scaffold(group: Path, gp, w: Writer):
    group_title = split_numbered(group.name)[1] if split_numbered(group.name) else group.name

    # group-level files
    w.write(group / AUTOGEN_NAME, "")
    w.write(group / HEADER_NAME, "")
    w.write(group / README_NAME, tpl_group_readme(group_title.replace("_", " ")))

    # subfolders
    for d in (gp.lessons, gp.assessments, gp.resources):
        w.mkdir(d)

    # baseline files in Assessments/ and Resources/
    w.write(gp.assessments / AUTOGEN_NAME, "")
    w.write(gp.assessments / HEADER_NAME, "")
    w.write(gp.assessments / README_NAME, "# Assessments\n\n")
    w.write(gp.assessments / META_NAME, tpl_meta_assessments())

    w.write(gp.resources / README_NAME, "# Resources\n\n")
    w.write(gp.resources / META_NAME, tpl_meta_resources())

def make_atomic_folder(lessons_dir: Path, nb: Path, w: Writer) -> Path:
    num = next_atomic_number(lessons_dir)
    title = slug_title(nb.stem)
    atomic = lessons_dir / f"{num:02d}-{title}"
    w.mkdir(atomic)

    w.write(atomic / AUTOGEN_NAME, "")
    w.write(atomic / HEADER_NAME, "")
    w.write(atomic / README_NAME, tpl_lesson_readme(title.replace("_", " ")))
    w.write(atomic / META_NAME, tpl_meta_lesson(title.replace("_", " ")))

    w.move(nb, atomic / nb.name)
    return atomic

def move_root_artifacts_to_resources(group: Path, resources_dir: Path, w: Writer) -> None:
    for p in sorted(group.iterdir()):
        if p.is_dir():
            continue
        if p.name in PROTECTED_FILES:
            continue
        if p.suffix == ".ipynb":
            continue
        if is_resource_file(p):
            w.move(p, resources_dir / p.name)

def explode_group(group: Path, w: Writer, move_artifacts: bool = True) -> None:
    gp = group_paths(group)
    ensure_group_scaffold(group, gp, w)

    # Route root-level notebooks
    for nb in root_level_notebooks(group):
        kind = classify_notebook_stem(nb.stem)  # assessment/resource/lesson
        if kind == "assessment":
            w.move(nb, gp.assessments / nb.name)
        elif kind == "resource":
            w.move(nb, gp.resources / nb.name)
        else:
            make_atomic_folder(gp.lessons, nb, w)

    if move_artifacts:
        move_root_artifacts_to_resources(group, gp.resources, w)

# -----------------------------
# CLI
# -----------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate_scaffolding",
        description="Scaffold/explode proto-groups (AA trigger: notebooks at group root)."
    )
    p.add_argument("--root", default=".", help="Course repo root (default: cwd).")
    p.add_argument("--section", default=None, help="Only process one section (e.g., '02' or '02-Spatial_Data_Core').")
    p.add_argument("--group", default=None, help="Only process one group folder path. Overrides --section.")
    p.add_argument("--dry-run", action="store_true", help="Print actions; do not modify files.")
    p.add_argument("--force", action="store_true", help="Overwrite scaffold files if they exist.")
    p.add_argument("--no-move-artifacts", action="store_true", help="Do NOT move non-notebook artifacts to Resources/.")
    p.add_argument("--verbose", action="store_true", help="Extra logging.")
    return p

def main() -> int:
    args = build_parser().parse_args()
    w = Writer(dry_run=args.dry_run, force=args.force, verbose=args.verbose)

    root = resolve_course_root(args.root)
    assignments_root = resolve_assignments_root(root)
    move_artifacts = not args.no_move_artifacts

    if args.group:
        group = ensure_under(assignments_root, Path(args.group))
        explode_group(group, w, move_artifacts=move_artifacts)
        print("Dry-run complete." if args.dry_run else "Done.")
        return 0

    # bulk mode: only proto groups (AA trigger)
    for group in iter_proto_groups(assignments_root, section_arg=args.section, strict_numbered=True):
        print(f"[group] {group}")
        explode_group(group, w, move_artifacts=move_artifacts)

    print("Dry-run complete." if args.dry_run else "Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())