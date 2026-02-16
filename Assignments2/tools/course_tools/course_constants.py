"""
course_constants.py

Authoritative constants + small helper functions for course repo structure.

Repo layout (course root):
  Assignments/
  Lectures/
  Resources/

Inside Assignments:
  Sections: NN-Section_Name/
    Groups: NN-Group_Name/
      _header.md, _autogen.md, README.md
      Lessons/
        Atomic folders: NN-Title/
          _header.md, _autogen.md, README.md, meta.yaml, *.ipynb
      Assessments/
      Resources/
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Tuple

# ─────────────────────────────────────────────────────────────
# Core file conventions
# ─────────────────────────────────────────────────────────────

HEADER_NAME = "_header.md"
AUTOGEN_NAME = "_autogen.md"
README_NAME = "README.md"
META_NAME = "meta.yaml"

RESERVED_MD = {HEADER_NAME, AUTOGEN_NAME, README_NAME}

REQUIRED_ATOMIC_FILES = {HEADER_NAME, AUTOGEN_NAME, README_NAME, META_NAME}

PROTECTED_FILES = {HEADER_NAME, AUTOGEN_NAME, README_NAME, META_NAME}

# ─────────────────────────────────────────────────────────────
# Legacy / deprecated containers
# ─────────────────────────────────────────────────────────────

LEGACY_DIRNAMES = {
    "notebooks",   # pre-constitution structure
}

# ─────────────────────────────────────────────────────────────
# Folder conventions
# ─────────────────────────────────────────────────────────────

ASSIGNMENTS_DIRNAME = "Assignments"
LECTURES_DIRNAME = "Lectures"
RESOURCES_DIRNAME = "Resources"

LESSONS_DIRNAME = "Lessons"
ASSESSMENTS_DIRNAME = "Assessments"

# ─────────────────────────────────────────────────────────────
# Heuristics for classification
# ─────────────────────────────────────────────────────────────

ASSESSMENT_KEYWORDS: Tuple[str, ...] = (
    "quiz",
    "mini_quiz",
    "miniquiz",
    "worksheet",
    "exam",
    "test",
    "assessment",
)

RESOURCE_EXTENSIONS: Tuple[str, ...] = (
    ".md",
    ".pdf",
    ".csv",
    ".tsv",
    ".json",
    ".geojson",
    ".gpkg",
    ".shp",
    ".tif",
    ".tiff",
    ".png",
    ".jpg",
    ".jpeg",
    ".zip",
)



# ─────────────────────────────────────────────────────────────
# Default grading values (used at meta creation only)
# ─────────────────────────────────────────────────────────────

DEFAULT_POINTS = {
    "assignment": 100,
    "assessment": 100,
    "resource": None,
}

DEFAULT_ASSIGNMENT_POINTS = 100
DEFAULT_ASSESSMENT_POINTS = 100

# ─────────────────────────────────────────────────────────────
# Naming patterns (strict on purpose)
# ─────────────────────────────────────────────────────────────

NUMBERED_PREFIX_RE = re.compile(r"^(?P<num>\d{2})-(?P<rest>.+)$")


def is_numbered_name(name: str) -> bool:
    """True if name matches NN-Anything."""
    return bool(NUMBERED_PREFIX_RE.match(name))


def split_numbered(name: str) -> tuple[int, str] | None:
    """Return (NN, rest) if name is NN-..., else None."""
    m = NUMBERED_PREFIX_RE.match(name)
    if not m:
        return None
    return int(m.group("num")), m.group("rest")


def is_hidden_path(p: Path) -> bool:
    """True if any path segment starts with '.'."""
    return any(part.startswith(".") for part in p.parts)


def normalize_token(s: str) -> str:
    """Lowercase tokenization helper for keyword matching."""
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def classify_notebook_stem(stem: str) -> str:
    """
    Classify a notebook name stem into: 'assessment' | 'resource' | 'lesson'

    NOTE: folder-based inference is preferred for meta typing.
    This is only for routing notebooks during scaffolding.
    """
    tokens = set(filter(None, normalize_token(stem).split("_")))
    assess_tokens = {normalize_token(k) for k in ASSESSMENT_KEYWORDS}

    if tokens & assess_tokens:
        return "assessment"

    # If it says "glossary" or similar, treat as resource notebook
    # (You can expand these tokens later without changing callers)
    resource_tokens = {"glossary", "resource", "resources", "helper", "helpers", "reference", "video", "videos"}
    if tokens & resource_tokens:
        return "resource"

    return "lesson"


def is_resource_file(path: Path) -> bool:
    """Resource artifact decision: extension-based."""
    return path.is_file() and path.suffix.lower() in RESOURCE_EXTENSIONS