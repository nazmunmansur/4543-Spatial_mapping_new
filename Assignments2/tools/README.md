```yaml
topic: course_tools_readme
deliverable: "README.md for tools/course_tools"
includes:
  - "United Courses Constitution summary"
  - "repo layout expectations"
  - "install/venv notes"
  - "how to run each script (module + direct)"
  - "common workflows (one-liners)"
  - "troubleshooting (imports, root, section)"
tone: "supportive with light roast"
```

This is a **feature-rich** app. Like an enterprise Java app from 2009. 😄

Here’s a **drop-in `README.md`** for `tools/course_tools/README.md` that:
- encodes the Constitution (wallet version)
- shows **all run modes** in one place
- includes “do-this-first” workflows
- includes troubleshooting for the exact stuff you hit (module imports, root, section, legacy notebooks)

---

## `tools/course_tools/README.md`

```markdown
# 🧰 Course Tools (MSU United Courses Constitution)

These scripts manage course repo structure under `Assignments/`, generate/refresh `meta.yaml`, export a CSV of due items, generate a global calendar, and build group-level README tables.

They’re instructor tools — but students are welcome to browse them, learn from them, and roast the professor for writing bash wrappers at 2am.

---

## ✅ Repo Constitution (Wallet Edition)

**Top-level course layout (repo root):**
```
COURSE_ROOT/
  Assignments/        # ✅ structural content (tools operate here)
  Lectures/           # free-form
  Resources/          # free-form
  tools/              # this folder
```

**Within `Assignments/`:**
- **Sections:** `Assignments/NN-Section_Title/`
- **Groups:** `Assignments/NN-Section/MM-Group_Title/`
- **Inside each group:**
  ```
  MM-Group_Title/
    README.md
    _header.md
    _autogen.md
    Lessons/
    Assessments/
    Resources/
  ```

**Atomic lessons** live in:
```
.../Lessons/LL-Atomic_Lesson_Title/
```

Atomic lesson folder MUST contain:
- `_header.md`
- `_autogen.md`
- `README.md`
- `meta.yaml`
- at least one notebook (`main.ipynb` recommended)

---

## 🗂️ “Legacy” folders

Some older content may still contain legacy containers such as `notebooks/`.

These tools ignore any folder listed in `LEGACY_DIRNAMES` in `course_constants.py` (ex: `notebooks/`).

---

## 🔧 How to run (recommended approach)

Run scripts as Python modules from **repo root**.

### General pattern
```bash
python -m tools.course_tools.<script_name> --root .
```

### Example
```bash
python -m tools.course_tools.generate_meta --root . --dry-run --section 02 --verbose
```

---

## 📌 Common flags

- `--root .`  
  Always points to the course repo root. If you run from a subfolder, still pass the repo root (e.g., `--root ..`).

- `--section 02` or `--section 02-Spatial_Data_Core`  
  Limits scanning to one section.

- `--dry-run`  
  Prints actions without writing.

- `--verbose`  
  Prints discovery and skips.

---

## 🧱 Scripts

### 1) `generate_scaffolding.py`
Scaffolds group structure and “explodes” root-level notebooks into atomic lesson folders.

**AA Trigger Rule:** a group is processed only if it has `.ipynb` files directly in the group folder.

#### Dry-run
```bash
python -m tools.course_tools.generate_scaffolding --root . --section 02 --dry-run
```

#### Execute
```bash
python -m tools.course_tools.generate_scaffolding --root . --section 02
```

#### Target a specific group path
```bash
python -m tools.course_tools.generate_scaffolding --root . --group Assignments/02-Spatial_Data_Core/01-Hello_GeoJson --dry-run
```

---

### 2) `generate_meta.py`
Creates and refreshes `meta.yaml` anywhere under `Assignments/` that *should* have metadata.

- Assignments and assessments use `notebooks: [...]`
- Resources use `files: [...]`

#### Dry-run + verbose
```bash
python -m tools.course_tools.generate_meta --root . --section 02 --dry-run --verbose
```

#### Refresh notebooks/files lists (recommended)
```bash
python -m tools.course_tools.generate_meta --root . --section 02 --refresh
```

#### Force overwrite existing `meta.yaml`
```bash
python -m tools.course_tools.generate_meta --root . --section 02 --refresh --force
```

#### Create meta.yaml for one folder only
```bash
python -m tools.course_tools.generate_meta --root . --create --path Assignments/02-Spatial_Data_Core/01-Hello_GeoJson/Resources
```

---

### 3) `export_assignments_csv.py`
Exports an `assignments.csv` by scanning `meta.yaml` under `Assignments/`.

#### Export only section 02
```bash
python -m tools.course_tools.export_assignments_csv --root . --section 02
```

#### Include undated items
```bash
python -m tools.course_tools.export_assignments_csv --root . --section 02 --include-undated
```

#### Custom output path
```bash
python -m tools.course_tools.export_assignments_csv --root . --section 02 --output .manager/assignments.csv
```

---

### 4) `build_global_calendar.py`
Builds `GLOBAL_CALENDAR.md` by scanning `meta.yaml` under `Assignments/`.

#### Build calendar for section 02
```bash
python -m tools.course_tools.build_global_calendar --root . --section 02
```

#### Include undated items
```bash
python -m tools.course_tools.build_global_calendar --root . --section 02 --include-undated
```

#### Custom output path
```bash
python -m tools.course_tools.build_global_calendar --root . --section 02 --output .manager/GLOBAL_CALENDAR.md
```

---

### 5) `build_folder_readmes.py`
Builds group-level `_autogen.md` and `README.md` with a dated items table (from `meta.yaml`).

#### Dry-run
```bash
python -m tools.course_tools.build_folder_readmes --root . --section 02 --dry-run
```

#### Execute
```bash
python -m tools.course_tools.build_folder_readmes --root . --section 02
```

---

## 🚀 Recommended workflows

### Workflow A: "I created content and want all artifacts updated"
```bash
python -m tools.course_tools.generate_meta --root . --refresh --section 02 \
&& python -m tools.course_tools.export_assignments_csv --root . --section 02 \
&& python -m tools.course_tools.build_global_calendar --root . --section 02 \
&& python -m tools.course_tools.build_folder_readmes --root . --section 02
```

### Workflow B: "I dropped notebooks into group folders; scaffold everything"
```bash
python -m tools.course_tools.generate_scaffolding --root . --section 02 \
&& python -m tools.course_tools.generate_meta --root . --refresh --section 02
```

---

## 🧨 Troubleshooting

### “No module named tools”
You are not running from repo root, or `tools/` is not at repo root.

✅ Fix: run from repo root and use module mode:
```bash
cd /path/to/COURSE_ROOT
python -m tools.course_tools.generate_meta --root . --dry-run
```

### “Assignments folder not found”
You passed the wrong `--root` (or ran from a subfolder without `--root`).

✅ Fix: point `--root` to the repo root:
```bash
python -m tools.course_tools.generate_meta --root . --dry-run
```

or if running from a subfolder:
```bash
python -m tools.course_tools.generate_meta --root .. --dry-run
```

### “Why is it scanning notebooks/ ?”
It shouldn’t (if `notebooks` is in `LEGACY_DIRNAMES`).  
Check `course_constants.py` → `LEGACY_DIRNAMES`.

---

## 🤝 Philosophy: “Machine-authored, human-edited”
These tools create consistent structure and metadata. Humans own meaning:

- you set real titles
- you set due dates
- you set points
- you rewrite README content

Automation sets the table. You serve the food.

# `Makefile` (repo root)

```makefile
# ============================================================
# Course Tools Makefile
# United Courses Constitution — MSU Edition
#
# Usage examples:
#   make meta SECTION=02
#   make scaffold SECTION=02
#   make calendar SECTION=02
#   make all SECTION=02
# ============================================================

PYTHON := python
TOOLS  := tools.course_tools
ROOT   := .

SECTION ?=
DRY    ?=

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

define run
	$(PYTHON) -m $(TOOLS).$(1) --root $(ROOT) $(2)
endef

ifdef DRY
DRY_FLAG := --dry-run
else
DRY_FLAG :=
endif

ifdef SECTION
SECTION_FLAG := --section $(SECTION)
else
SECTION_FLAG :=
endif

# ------------------------------------------------------------
# Targets
# ------------------------------------------------------------

.PHONY: help scaffold meta csv calendar readmes all check clean

help:
	@echo ""
	@echo "Course Tools — Available Targets"
	@echo "--------------------------------"
	@echo "make scaffold SECTION=02     Scaffold proto-groups (AA trigger)"
	@echo "make meta SECTION=02         Generate/refresh meta.yaml"
	@echo "make csv SECTION=02          Export assignments.csv"
	@echo "make calendar SECTION=02     Build GLOBAL_CALENDAR.md"
	@echo "make readmes SECTION=02      Build group README.md files"
	@echo "make check SECTION=02        Run structural checks"
	@echo ""
	@echo "Flags:"
	@echo "  SECTION=02        Limit to a section"
	@echo "  DRY=1             Dry-run (where supported)"
	@echo ""
	@echo "Example:"
	@echo "  make all SECTION=02"
	@echo ""

# ------------------------------------------------------------
# Individual steps
# ------------------------------------------------------------

scaffold:
	$(call run,generate_scaffolding,$(SECTION_FLAG) $(DRY_FLAG))

meta:
	$(call run,generate_meta,$(SECTION_FLAG) --refresh $(DRY_FLAG))

csv:
	$(call run,export_assignments_csv,$(SECTION_FLAG))

calendar:
	$(call run,build_global_calendar,$(SECTION_FLAG))

readmes:
	$(call run,build_folder_readmes,$(SECTION_FLAG) $(DRY_FLAG))

check:
	$(call run,course_manager,check $(SECTION_FLAG))

# ------------------------------------------------------------
# Pipelines
# ------------------------------------------------------------

all:
	@echo "🚀 Running full course tool pipeline"
	@$(MAKE) scaffold SECTION=$(SECTION) DRY=$(DRY)
	@$(MAKE) meta     SECTION=$(SECTION) DRY=$(DRY)
	@$(MAKE) csv      SECTION=$(SECTION)
	@$(MAKE) calendar SECTION=$(SECTION)
	@$(MAKE) readmes  SECTION=$(SECTION) DRY=$(DRY)
	@echo "✅ Done."

# ------------------------------------------------------------
# Cleanup (optional)
# ------------------------------------------------------------

clean:
	@echo "⚠️  This Makefile does not delete content."
	@echo "If you want cleanup targets, we can add them intentionally."
```

---

## How this changes your life (dramatically)

### One command to rule them all
```bash
make all SECTION=02
```

### Dry-run *everything*
```bash
make all SECTION=02 DRY=1
```

### Just regenerate metadata
```bash
make meta SECTION=02
```

### Scaffold only (when you drop new notebooks)
```bash
make scaffold SECTION=02
```
