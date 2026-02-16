topic: generate_scaffolding
decision: proto_group_trigger
trigger_rule: "A (ONLY scaffold/explode when group root contains >=1 .ipynb)"
safety: "prevents empty-folder automation"
deliverable: "tools/course_tools/generate_scaffolding.py"
defaults:
  dry_run: true
  only_proto: true
  move_artifacts: true
  force: false

AA accepted. “Make me do something before I unleash automation” is the correct kind of paranoia.

Below is a ready-to-drop generate_scaffolding.py that follows your rule:

Only scaffold/explode a group folder if it has at least one .ipynb directly in the group root.

It also supports --section (same idea as course_manager), and --group for a single target.

⸻

tools/course_tools/generate_scaffolding.py

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from rich import print

from course_constants import (
    ASSIGNMENTS_DIRNAME,
    LESSONS_DIRNAME,
    ASSESSMENTS_DIRNAME,
    RESOURCES_DIRNAME,
    HEADER_NAME,
    AUTOGEN_NAME,
    README_NAME,
    META_NAME,
    PROTECTED_FILES,
    RESOURCE_EXTENSIONS,
    ASSESSMENT_KEYWORDS,
    is_resource_file,
    classify_notebook_stem,
)

# -----------------------------
# Naming helpers
# -----------------------------
NUMBERED_PREFIX_RE = re.compile(r"^(?P<num>\d{2})-(?P<rest>.+)$")

def is_numbered_folder_name(name: str) -> bool:
    return bool(NUMBERED_PREFIX_RE.match(name))

def split_numbered(name: str) -> tuple[int, str] | None:
    m = NUMBERED_PREFIX_RE.match(name)
    if not m:
        return None
    return int(m.group("num")), m.group("rest")

def slug_title(stem: str) -> str:
    """
    Convert notebook stem into folder title with underscores:
      "next_steps" -> "Next_Steps"
      "more-steps" -> "More_Steps"
      "data input output" -> "Data_Input_Output"
    """
    raw = re.sub(r"[_\-\s]+", " ", stem).strip()
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", raw) if p]
    if not parts:
        return "Untitled"
    parts = [p[0].upper() + p[1:] if len(p) > 1 else p.upper() for p in parts]
    return "_".join(parts)

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
    return (
        f"# {group_title}\n\n"
        "## Overview\n\n"
        "- TODO: Add overview and link to lessons/assessments/resources.\n"
    )

def tpl_lesson_readme(title: str) -> str:
    return (
        f"# {title}\n\n"
        "## Goals\n\n"
        "- TODO\n\n"
        "## Instructions\n\n"
        "- TODO\n"
    )

def tpl_meta(title: str, mtype: str) -> str:
    # minimal + matches your schema direction (machine-first, human-edit)
    # You can later unify with generate_meta if you prefer.
    if mtype == "lesson":
        return (
            "schema_version: 1\n"
            f"title: {title}\n"
            "type: assignment\n"
            "status: draft\n"
            "due: null\n"
            "points: null\n"
            "notebooks: []\n"
        )
    if mtype == "assessments":
        return (
            "schema_version: 1\n"
            "title: Assessments\n"
            "type: assessment\n"
            "status: draft\n"
            "due: null\n"
            "points: null\n"
            "notebooks: []\n"
        )
    if mtype == "resources":
        return (
            "schema_version: 1\n"
            "title: Resources\n"
            "type: resource\n"
            "status: draft\n"
            "files: []\n"
        )
    return "schema_version: 1\nstatus: draft\n"

# -----------------------------
# Writer
# -----------------------------
@dataclass
class Writer:
    dry_run: bool = True
    force: bool = False
    verbose: bool = False

    def log(self, msg: str) -> None:
        if self.verbose:
            print(msg)

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
# Discovery
# -----------------------------
def resolve_root(root_arg: str | None) -> Path:
    if not root_arg:
        return Path.cwd().expanduser().resolve()
    p = Path(root_arg).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    return p.resolve()

def resolve_assignments_root(root: Path) -> Path:
    a = root / ASSIGNMENTS_DIRNAME
    if not a.exists() or not a.is_dir():
        raise SystemExit(f"Assignments/ folder not found under: {root}")
    return a

def list_sections(assignments_root: Path) -> list[Path]:
    return sorted([p for p in assignments_root.iterdir() if p.is_dir() and is_numbered_folder_name(p.name)])

def resolve_sections(assignments_root: Path, section_arg: str | None) -> list[Path]:
    secs = list_sections(assignments_root)
    if not section_arg:
        return secs

    s = section_arg.strip()

    exact = [p for p in secs if p.name == s]
    if exact:
        return exact

    if s.isdigit() and len(s) == 2:
        pref = s + "-"
        by_num = [p for p in secs if p.name.startswith(pref)]
        if len(by_num) == 1:
            return by_num
        if len(by_num) > 1:
            raise SystemExit(f"Multiple sections match '{s}': {[p.name for p in by_num]}")
        raise SystemExit(f"No section matches '{s}' under {assignments_root}")

    fuzzy = [p for p in secs if s.lower() in p.name.lower()]
    if len(fuzzy) == 1:
        return fuzzy
    if len(fuzzy) > 1:
        raise SystemExit(f"Multiple sections match '{s}': {[p.name for p in fuzzy]}")
    raise SystemExit(f"No section matches '{s}' under {assignments_root}")

def iter_groups(section: Path) -> Iterable[Path]:
    for p in sorted(section.iterdir()):
        if p.is_dir() and is_numbered_folder_name(p.name):
            yield p

def root_level_notebooks(group: Path) -> list[Path]:
    return sorted([p for p in group.iterdir() if p.is_file() and p.suffix == ".ipynb"])

def is_proto_group(group: Path) -> bool:
    # Rule AA: ONLY trigger if there is at least one ipynb at group root
    return len(root_level_notebooks(group)) > 0

# -----------------------------
# Scaffold actions
# -----------------------------
def ensure_group_scaffold(group: Path, w: Writer) -> tuple[Path, Path, Path]:
    group_title = split_numbered(group.name)[1] if split_numbered(group.name) else group.name

    # group-level files
    w.write(group / AUTOGEN_NAME, "")
    w.write(group / HEADER_NAME, "")
    w.write(group / README_NAME, tpl_group_readme(group_title.replace("_", " ")))

    lessons_dir = group / LESSONS_DIRNAME
    assessments_dir = group / ASSESSMENTS_DIRNAME
    resources_dir = group / RESOURCES_DIRNAME

    for d in (lessons_dir, assessments_dir, resources_dir):
        w.mkdir(d)

    # Baseline files in Assessments/ and Resources/
    w.write(assessments_dir / AUTOGEN_NAME, "")
    w.write(assessments_dir / HEADER_NAME, "")
    w.write(assessments_dir / README_NAME, "# Assessments\n\n")
    w.write(assessments_dir / META_NAME, tpl_meta("Assessments", "assessments"))

    w.write(resources_dir / README_NAME, "# Resources\n\n")
    w.write(resources_dir / META_NAME, tpl_meta("Resources", "resources"))

    return lessons_dir, assessments_dir, resources_dir

def make_atomic_folder(lessons_dir: Path, nb: Path, w: Writer) -> Path:
    num = next_atomic_number(lessons_dir)
    title = slug_title(nb.stem)
    atomic = lessons_dir / f"{num:02d}-{title}"
    w.mkdir(atomic)

    # required atomic files
    w.write(atomic / AUTOGEN_NAME, "")
    w.write(atomic / HEADER_NAME, "")
    w.write(atomic / README_NAME, tpl_lesson_readme(title.replace("_", " ")))
    w.write(atomic / META_NAME, tpl_meta(title.replace("_", " "), "lesson"))

    # move notebook in
    w.move(nb, atomic / nb.name)
    return atomic

def move_root_artifacts_to_resources(group: Path, resources_dir: Path, w: Writer) -> None:
    """
    Move root-level non-notebook resource artifacts into Resources/, excluding protected files and folders.
    """
    for p in sorted(group.iterdir()):
        if p.is_dir():
            continue
        if p.name in PROTECTED_FILES:
            continue
        if p.suffix == ".ipynb":
            continue
        if is_resource_file(p) or p.suffix.lower() in (".geojson",):  # geojson included by is_resource_file if you added it
            w.move(p, resources_dir / p.name)

def explode_group(group: Path, w: Writer, move_artifacts: bool = True) -> None:
    if not is_proto_group(group):
        w.log(f"[skip] not proto-group (no root notebooks): {group}")
        return

    print(f"[group] {group}")
    lessons_dir, assessments_dir, resources_dir = ensure_group_scaffold(group, w)

    # Route root-level notebooks
    for nb in root_level_notebooks(group):
        kind = classify_notebook_stem(nb.stem)  # assessment/resource/lesson

        if kind == "assessment":
            w.move(nb, assessments_dir / nb.name)
        elif kind == "resource":
            w.move(nb, resources_dir / nb.name)
        else:
            make_atomic_folder(lessons_dir, nb, w)

    # Move other artifacts (json/geojson/pdf/etc.) into Resources/
    if move_artifacts:
        move_root_artifacts_to_resources(group, resources_dir, w)

# -----------------------------
# CLI
# -----------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="generate_scaffolding",
        description="Scaffold/explode proto-groups into standard folder structure (AA trigger: notebooks at group root)."
    )
    p.add_argument("--root", default=".", help="Course repo root (default: cwd).")
    p.add_argument("--section", default=None, help="Only process one section (e.g., '02' or '02-Spatial_Data_Core').")
    p.add_argument("--group", default=None, help="Only process one group folder (path). Overrides --section.")
    p.add_argument("--dry-run", action="store_true", help="Print actions; do not modify files.")
    p.add_argument("--force", action="store_true", help="Overwrite scaffold files if they exist.")
    p.add_argument("--no-move-artifacts", action="store_true", help="Do NOT move non-notebook artifacts to Resources/.")
    p.add_argument("--verbose", action="store_true", help="Extra logging.")

    return p

def main() -> int:
    args = build_parser().parse_args()

    w = Writer(
        dry_run=args.dry_run,
        force=args.force,
        verbose=args.verbose,
    )

    root = resolve_root(args.root)
    assignments_root = resolve_assignments_root(root)

    move_artifacts = not args.no_move_artifacts

    if args.group:
        group = Path(args.group).expanduser()
        if not group.is_absolute():
            group = (Path.cwd() / group).resolve()
        explode_group(group, w, move_artifacts=move_artifacts)
        return 0

    sections = resolve_sections(assignments_root, args.section)

    for sec in sections:
        for group in iter_groups(sec):
            explode_group(group, w, move_artifacts=move_artifacts)

    print("Dry-run complete." if args.dry_run else "Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())


⸻

How you run it (module-style, repo-local)

From repo root:

python -m tools.course_tools.generate_scaffolding --root . --dry-run --section 02

Actually do it:

python -m tools.course_tools.generate_scaffolding --root . --section 02

Single group:

python -m tools.course_tools.generate_scaffolding --group ./Assignments/02-Spatial_Data_Core/01-Hello_GeoJson --dry-run


⸻

What happens to your “proto” folder example

Given:

Assignments/02-Spatial_Data_Core/01-Hello_GeoJson/
  00-Hello_GeoJSON.ipynb
  broken_world.json
  campus_world.geojson
  README.md
  meta.yaml

This script will (when not dry-run):
	•	create Lessons/ Assessments/ Resources/ (if missing)
	•	move 00-Hello_GeoJSON.ipynb into Lessons/01-Hello_GeoJSON/
	•	move broken_world.json, campus_world.geojson into Resources/
	•	create atomic _autogen/_header/README/meta.yaml for the new atomic folder

It triggers only because .ipynb is at group root. That’s your AA safeguard.

⸻

If you want, next step is making course_manager check aware of proto-groups and gently warn:
“Group has notebook at root → run scaffolding.”
(So it becomes a nice workflow instead of tribal knowledge.)