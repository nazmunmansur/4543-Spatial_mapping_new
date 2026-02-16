"""
# python -m tools.course_tools.generate_scaffolding --root . --section 02 --dry-run

CLI flags you’ll want (simple but useful)
	•	--root (default .)
	•	--section (optional filter like we added to course_manager)
	•	--group (optional: run on one group path directly)
	•	--dry-run (print actions only)
	•	--force (overwrite scaffold files if they exist)
	•	--move-artifacts (whether to move .json/.geojson/... into Resources; default True)
	•	--only-proto (default True; only scaffold if proto detected)
	•	--verbose (print what it finds even if no changes)
"""

__all__ = [
    "course_constants",
    "course_paths",
    "course_manager",
    "generate_meta",
    "generate_scaffolding",
]

__version__ = "0.1.0"