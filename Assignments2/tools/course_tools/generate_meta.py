#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore

from rich import print

from .course_constants import (
    META_NAME,
    ASSESSMENTS_DIRNAME,
    RESOURCES_DIRNAME,
    LEGACY_DIRNAMES,
    is_hidden_path,
    is_resource_file,
)
from .course_paths import (
    resolve_course_root,
    resolve_assignments_root,
    resolve_sections,
)


TZ_NAME = "America/Chicago"
SCHEMA_VERSION = 1
DEFAULT_STATUS = "draft"


# def find_assignment_folder(section_path: Path, assignment: str) -> Path:
#     """
#     Find a single folder anywhere under the section whose name starts with the assignment id/prefix.
#     Examples: assignment='02B' matches '02B-Distance_Depends_on_Assumptions'
#               assignment='02A' matches '02A-When_Coordinates_Arent_Enough'
#               assignment='03'  matches '03-Visualize_And_Explore'
#     """
#     needle = assignment.strip().lower()

#     matches: list[Path] = []

#     for p in section_path.rglob("*"):
#         if not p.is_dir():
#             continue
#         name = p.name.lower()

#         # Skip hidden dirs quickly ('.git', '__pycache__', etc.)
#         if any(part.startswith(".") for part in p.parts):
#             continue

#         # Optional: skip common containers that aren't atomic lessons
#         if name in ("lessons", "assessments", "resources", "notebooks"):
#             continue

#         if name == needle or name.startswith(needle + "-"):
#             matches.append(p)

#     if not matches:
#         raise RuntimeError(
#             f"No assignment folder found under {section_path} matching '{assignment}'"
#         )

#     if len(matches) > 1:
#         options = "\n".join(f"  - {m}" for m in matches[:25])
#         raise RuntimeError(
#             f"Multiple folders match '{assignment}'. Be more specific.\nMatches:\n{options}"
#         )

#     return matches[0]


def select_single_assignment(folders: list[Path], assignment: str) -> list[Path]:
    needle = assignment.strip().lower()

    matches = []
    for f in folders:
        name = f.name.lower()
        if name == needle or name.startswith(needle + "-"):
            matches.append(f)

    if not matches:
        options = "\n".join(f"  - {f}" for f in folders[:25])
        raise RuntimeError(
            f"No folder matched assignment '{assignment}'.\n"
            f"Expected something like '{assignment}-Something'.\n"
            f"First folders seen:\n{options}"
        )

    if len(matches) > 1:
        opts = "\n".join(f"  - {m}" for m in matches)
        raise RuntimeError(
            f"Multiple folders matched assignment '{assignment}'. Be more specific.\nMatches:\n{opts}"
        )

    return matches


def now_iso() -> str:
    if ZoneInfo is None:
        return datetime.now().isoformat(timespec="seconds")
    tz = ZoneInfo(TZ_NAME)
    return datetime.now(tz=tz).isoformat(timespec="seconds")


def infer_type(folder: Path) -> str:
    n = folder.name.lower()
    if n == ASSESSMENTS_DIRNAME.lower():
        return "assessment"
    if n == RESOURCES_DIRNAME.lower():
        return "resource"
    return "assignment"


def list_notebooks(folder: Path) -> List[str]:
    return sorted([p.name for p in folder.glob("*.ipynb") if p.is_file()])


def list_resource_files(folder: Path) -> List[str]:
    exclude = {META_NAME, "_header.md", "_autogen.md", "README.md"}
    out: List[str] = []
    for p in sorted(folder.iterdir()):
        if not p.is_file():
            continue
        if p.name in exclude:
            continue
        if is_resource_file(p):
            out.append(p.name)
    return out


def yaml_quote(s: str) -> str:
    if ":" not in s and "\n" not in s:
        return s
    return '"' + s.replace('"', '\\"') + '"'


def dump_yaml(meta: dict) -> str:
    order = [
        "schema_version",
        "title",
        "type",
        "status",
        "due",
        "points",
        "notebooks",
        "files",
        "created_at",
        "updated_at",
    ]
    lines: List[str] = []
    for k in order:
        if k not in meta:
            continue
        v = meta[k]
        if v is None:
            lines.append(f"{k}: null")
        elif isinstance(v, int):
            lines.append(f"{k}: {v}")
        elif isinstance(v, list):
            lines.append(f"{k}:")
            if not v:
                lines.append("  []")
            else:
                for item in v:
                    lines.append(f"  - {yaml_quote(str(item))}")
        else:
            lines.append(f"{k}: {yaml_quote(str(v))}")
    return "\n".join(lines) + "\n"


def parse_existing_meta(meta_path: Path) -> dict:
    meta: dict = {}
    if not meta_path.exists():
        return meta
    for line in meta_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        if v == "null":
            meta[k] = None
        elif v.isdigit():
            meta[k] = int(v)
        else:
            if (v.startswith('"') and v.endswith('"')) or (
                v.startswith("'") and v.endswith("'")
            ):
                v = v[1:-1]
            meta[k] = v
    return meta


@dataclass
class Writer:
    dry_run: bool = False
    force: bool = False
    verbose: bool = False
    show_existing: bool = False

    def write_text(self, path: Path, text: str) -> None:
        if path.exists() and not self.force:
            if self.show_existing:
                print(f"[keep] {path}")
            return
        if self.dry_run:
            action = "overwrite" if path.exists() else "create"
            print(f"[dry-run] {action} {path}")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"[write] {path}")


def should_have_meta(folder: Path) -> bool:
    ftype = infer_type(folder)
    if ftype == "assessment":
        return True
    if ftype == "resource":
        return bool(list_resource_files(folder) or list_notebooks(folder))
    return bool(list_notebooks(folder))


def walk_candidate_folders(
    assignments_root: Path, section_arg: str | None, verbose: bool
) -> List[Path]:
    candidates: List[Path] = []
    sections = resolve_sections(assignments_root, section_arg)

    if verbose:
        print(f"[info] scan root: {assignments_root}")
        print(f"[info] sections: {[s.name for s in sections]}")

    for sec in sections:
        for p in sorted(sec.rglob("*")):
            if not p.is_dir():
                continue
            if is_hidden_path(p):
                continue

            # Skip legacy containers entirely
            if p.name.lower() in LEGACY_DIRNAMES:
                if verbose:
                    print(f"[skip] legacy container: {p}")
                continue

            # Skip anything nested under legacy containers
            if any(parent.name.lower() in LEGACY_DIRNAMES for parent in p.parents):
                continue

            if should_have_meta(p):
                candidates.append(p)
                if verbose:
                    print(f"[found] {infer_type(p):<10} {p}")
    return candidates


def build_meta(folder: Path, existing: dict, refresh: bool, prune: bool) -> dict:
    ftype = infer_type(folder)
    title = existing.get("title") or folder.name

    created_at = existing.get("created_at") or now_iso()
    updated_at = now_iso()

    meta: dict = {
        "schema_version": existing.get("schema_version") or SCHEMA_VERSION,
        "title": title,
        "type": ftype,
        "status": existing.get("status") or DEFAULT_STATUS,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    if ftype in {"assignment", "assessment"}:
        meta["due"] = existing.get("due")
        meta["points"] = existing.get("points")
        if refresh or ("notebooks" not in existing) or prune:
            meta["notebooks"] = list_notebooks(folder)

    elif ftype == "resource":
        if refresh or ("files" not in existing) or prune:
            meta["files"] = list_resource_files(folder)

    return meta


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="generate_meta",
        description="Generate/refresh meta.yaml under Assignments/.",
    )
    ap.add_argument("--root", default=".", help="Course repo root (default: cwd).")
    ap.add_argument(
        "--section",
        default=None,
        help="Only process one section (e.g., '02' or '02-Spatial_Data_Core').",
    )
    ap.add_argument(
        "--dry-run", action="store_true", help="Show actions, do not write."
    )
    ap.add_argument(
        "--force", action="store_true", help="Overwrite existing meta.yaml files."
    )
    ap.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh notebooks/files lists (preserves title/due/points/status).",
    )
    ap.add_argument(
        "--prune",
        action="store_true",
        help="Rewrite notebooks/files keys even if they existed (cleanup).",
    )
    ap.add_argument(
        "--verbose", action="store_true", help="Print discovered candidates."
    )
    ap.add_argument(
        "--show-existing",
        action="store_true",
        help="Print meta.yaml paths that are kept (not overwritten).",
    )

    ap.add_argument(
        "--create",
        action="store_true",
        help="Create meta.yaml for a specific folder only.",
    )
    ap.add_argument("--path", default=None, help="Folder path used with --create.")

    ap.add_argument(
        "--assignment",
        type=str,
        default=None,
        help="Process only one atomic assignment by ID/prefix (e.g. 02B, 01, 03-Visualize).",
    )

    ap.add_argument(
        "--print",
        dest="print_only",
        action="store_true",
        help="Print the selected assignment's meta.yaml to stdout (no writes).",
    )
    return ap


def ensure_under(assignments_root: Path, target: Path) -> Path:
    target = target.expanduser().resolve()
    assignments_root = assignments_root.expanduser().resolve()
    if target == assignments_root or assignments_root in target.parents:
        return target
    raise SystemExit(f"Refusing: target path is not under {assignments_root}: {target}")


def main() -> int:
    args = build_parser().parse_args()
    course_root = resolve_course_root(args.root)
    assignments_root = resolve_assignments_root(course_root)

    w = Writer(
        dry_run=args.dry_run,
        force=args.force,
        verbose=args.verbose,
        show_existing=args.show_existing,
    )

    if args.create:
        if not args.path:
            raise SystemExit("--create requires --path <folder>")
        target = ensure_under(assignments_root, Path(args.path))
        if not target.exists() or not target.is_dir():
            raise SystemExit(f"--path is not an existing folder: {target}")

        meta_path = target / META_NAME
        existing = parse_existing_meta(meta_path) if meta_path.exists() else {}
        meta = build_meta(target, existing, refresh=args.refresh, prune=args.prune)
        w.write_text(meta_path, dump_yaml(meta))
        return 0

    folders = walk_candidate_folders(
        assignments_root, args.section, verbose=args.verbose
    )
    if not folders:
        print("No candidate folders found.")
        return 0

    # for folder in folders:
    #     meta_path = folder / META_NAME
    #     existing = parse_existing_meta(meta_path) if meta_path.exists() else {}
    #     meta = build_meta(folder, existing, refresh=args.refresh, prune=args.prune)
    #     w.write_text(meta_path, dump_yaml(meta))

    # Optionally narrow to a single assignment folder
    if args.assignment:
        folders = select_single_assignment(folders, args.assignment)

    for folder in folders:
        meta_path = folder / META_NAME
        existing = parse_existing_meta(meta_path) if meta_path.exists() else {}
        meta = build_meta(folder, existing, refresh=args.refresh, prune=args.prune)

        # Print-only mode: show YAML and do not write
        if args.print_only:
            print(dump_yaml(meta).rstrip())
            continue

        w.write_text(meta_path, dump_yaml(meta))

    print("Dry-run complete." if args.dry_run else "Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
