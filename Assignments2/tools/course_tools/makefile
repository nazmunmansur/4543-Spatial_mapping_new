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

