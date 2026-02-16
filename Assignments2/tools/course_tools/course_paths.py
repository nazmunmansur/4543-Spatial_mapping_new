"""
course_paths.py

Shared path resolution + discovery utilities for the course repo.

Repository Constitution (enforced by tools):
  COURSE_ROOT/
    Assignments/   <-- structural tools operate ONLY under here
    Lectures/
    Resources/
    tools/

Under Assignments:
  Sections: NN-Section_Title/
    Groups:  NN-Group_Title/
      Lessons/
      Assessments/
      Resources/

This module is intentionally boring and reusable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .course_constants import (
    ASSIGNMENTS_DIRNAME,
    LESSONS_DIRNAME,
    ASSESSMENTS_DIRNAME,
    RESOURCES_DIRNAME,
    is_numbered_name,
    split_numbered,
    is_hidden_path,
)

# ─────────────────────────────────────────────────────────────
# Resolution
# ─────────────────────────────────────────────────────────────

def resolve_course_root(root_arg: str | None = None) -> Path:
    """
    Resolve the course repo root.
    - If root_arg is None: cwd
    - If relative: relative to cwd
    - Expand ~ and resolve symlinks
    """
    if not root_arg:
        return Path.cwd().expanduser().resolve()

    p = Path(root_arg).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    return p.resolve()


def resolve_assignments_root(course_root: Path) -> Path:
    """
    Return the Assignments/ directory, enforcing that tools should only operate under it.

    Accepts:
      - course_root pointing at repo root (contains Assignments/)
      - OR a direct path to Assignments/ itself
    """
    course_root = course_root.expanduser().resolve()

    if course_root.name == ASSIGNMENTS_DIRNAME and course_root.is_dir():
        return course_root

    assignments = course_root / ASSIGNMENTS_DIRNAME
    if not assignments.exists() or not assignments.is_dir():
        raise RuntimeError(f"{ASSIGNMENTS_DIRNAME}/ folder not found under: {course_root}")
    return assignments


def ensure_under(base: Path, target: Path) -> Path:
    """
    Ensure target is inside base directory (or equal).
    Useful for guarding `--path` / `--group` operations.
    """
    base = base.expanduser().resolve()
    target = target.expanduser().resolve()

    if target == base:
        return target
    if base in target.parents:
        return target
    raise RuntimeError(f"Refusing: target is not under {base}: {target}")


# ─────────────────────────────────────────────────────────────
# Discovery: sections / groups
# ─────────────────────────────────────────────────────────────

def list_sections(assignments_root: Path) -> List[Path]:
    """
    Sections are direct children of Assignments/ matching NN-*
    """
    assignments_root = assignments_root.expanduser().resolve()
    return sorted([
        p for p in assignments_root.iterdir()
        if p.is_dir() and is_numbered_name(p.name) and not p.name.startswith(".")
    ])


def resolve_sections(assignments_root: Path, section_arg: str | None) -> List[Path]:
    """
    Flexible section resolution:

    - None => all sections
    - "02" => unique match for prefix "02-"
    - "02-Spatial_Data_Core" => exact match
    - "Spatial_Data" => unique substring match

    Raises RuntimeError on no match or ambiguous match.
    """
    sections = list_sections(assignments_root)
    if not section_arg:
        return sections

    s = section_arg.strip()

    # exact match
    exact = [p for p in sections if p.name == s]
    if exact:
        return exact

    # numeric prefix match
    if s.isdigit() and len(s) == 2:
        pref = s + "-"
        by_num = [p for p in sections if p.name.startswith(pref)]
        if len(by_num) == 1:
            return by_num
        if len(by_num) > 1:
            raise RuntimeError(f"Multiple sections match '{s}': {[p.name for p in by_num]}")
        raise RuntimeError(f"No section matches number '{s}' under {assignments_root}")

    # substring match (only if unique)
    fuzzy = [p for p in sections if s.lower() in p.name.lower()]
    if len(fuzzy) == 1:
        return fuzzy
    if len(fuzzy) > 1:
        raise RuntimeError(f"Multiple sections match '{s}': {[p.name for p in fuzzy]}")
    raise RuntimeError(f"No section matches '{s}' under {assignments_root}")


def iter_groups(section: Path, strict_numbered: bool = True) -> Iterable[Path]:
    """
    Groups are direct children of section.
    If strict_numbered: only NN-* folders.
    """
    section = section.expanduser().resolve()
    for p in sorted(section.iterdir()):
        if not p.is_dir() or p.name.startswith("."):
            continue
        if strict_numbered and not is_numbered_name(p.name):
            continue
        yield p


def iter_all_groups(assignments_root: Path, section_arg: str | None = None, strict_numbered: bool = True) -> Iterable[Path]:
    """
    Yield all groups under Assignments, optionally filtered by section.
    """
    for sec in resolve_sections(assignments_root, section_arg):
        yield from iter_groups(sec, strict_numbered=strict_numbered)


# ─────────────────────────────────────────────────────────────
# Discovery: proto-groups (AA trigger)
# ─────────────────────────────────────────────────────────────

def root_level_notebooks(group: Path) -> List[Path]:
    """
    Return notebooks directly in the group root (proto indicator).
    """
    group = group.expanduser().resolve()
    return sorted([p for p in group.iterdir() if p.is_file() and p.suffix == ".ipynb"])


def is_proto_group(group: Path) -> bool:
    """
    AA trigger: group is proto iff it has >=1 .ipynb at group root.
    """
    return len(root_level_notebooks(group)) > 0


def iter_proto_groups(assignments_root: Path, section_arg: str | None = None, strict_numbered: bool = True) -> Iterable[Path]:
    """
    Yield only proto-groups under Assignments (AA trigger).
    """
    for g in iter_all_groups(assignments_root, section_arg=section_arg, strict_numbered=strict_numbered):
        if is_proto_group(g):
            yield g


# ─────────────────────────────────────────────────────────────
# Convenience: standard subpaths inside a group
# ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class GroupPaths:
    group: Path
    lessons: Path
    assessments: Path
    resources: Path

def group_paths(group: Path) -> GroupPaths:
    group = group.expanduser().resolve()
    return GroupPaths(
        group=group,
        lessons=group / LESSONS_DIRNAME,
        assessments=group / ASSESSMENTS_DIRNAME,
        resources=group / RESOURCES_DIRNAME,
    )