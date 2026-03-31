# Kuyper Translation - Build & Workflow

.PHONY: all editions pdf parallel check-terms review clean help \
        pipeline extract-vol1 extract-vol2 align quality substack assemble-vol1 assemble-vol2

# Default: show help
all: help

help:
	@echo "Kuyper: Antirevolutionary Politics — Build Commands"
	@echo ""
	@echo "  make editions      Generate all edition files from source"
	@echo "  make pdf           Export all volumes to PDF"
	@echo "  make parallel      Generate Dutch/English parallel editions"
	@echo "  make check-terms   Check terminology consistency"
	@echo "  make review        Run review checklist on all chapters"
	@echo "  make clean         Remove build artifacts"
	@echo "  make help          Show this help"
	@echo ""
	@echo "Pipeline Commands (Go):"
	@echo "  make pipeline          Build the Go pipeline binary"
	@echo "  make extract-vol1      Extract Volume 1 chapters"
	@echo "  make extract-vol2      Extract Volume 2 chapters"
	@echo "  make align CHAPTER=... Check Dutch/English alignment"
	@echo "  make quality CHAPTER=... Run quality gate on a chapter"
	@echo "  make substack CHAPTER=... Export chapter to Substack format"
	@echo "  make assemble-vol1     Assemble Volume 1 from chapters"
	@echo "  make assemble-vol2     Assemble Volume 2 from chapters"

# ─── Pipeline (Go) ────────────────────────────────────────────────────────────

PIPELINE = ./pipeline/pipeline

pipeline:
	@echo "Building pipeline binary..."
	cd pipeline && go build -o ../pipeline/pipeline .
	@echo "Pipeline binary built: pipeline/pipeline"

extract-vol1: pipeline
	$(PIPELINE) extract 1

extract-vol2: pipeline
	$(PIPELINE) extract 2

align: pipeline
	@if [ -z "$(CHAPTER)" ]; then \
		echo "Usage: make align CHAPTER=manuscript/volume_1/ch01-introduction"; \
		exit 1; \
	fi
	$(PIPELINE) align $(CHAPTER)

quality: pipeline
	@if [ -z "$(CHAPTER)" ]; then \
		echo "Usage: make quality CHAPTER=manuscript/volume_1/ch01-introduction"; \
		exit 1; \
	fi
	$(PIPELINE) quality $(CHAPTER)

substack: pipeline
	@if [ -z "$(CHAPTER)" ]; then \
		echo "Usage: make substack CHAPTER=manuscript/volume_1/ch01-introduction"; \
		exit 1; \
	fi
	$(PIPELINE) substack $(CHAPTER)

assemble-vol1: pipeline
	$(PIPELINE) assemble 1

assemble-vol2: pipeline
	$(PIPELINE) assemble 2

# ─── Python Scripts ───────────────────────────────────────────────────────────

# Generate editions from source materials
editions:
	@echo "Generating scholarly master edition..."
	python scripts/generate_scholarly_master.py
	@echo "Generating parallel editions..."
	python scripts/generate_parallel_edition.py
	@echo "Generating synopticon..."
	python scripts/generate_synopticon.py
	@echo "Editions generated."

# Export to PDF
pdf:
	@echo "Exporting to PDF (WeasyPrint)..."
	python scripts/export_pdf_weasyprint.py
	@echo "PDF export complete."

# Generate parallel Dutch/English editions
parallel:
	@echo "Generating parallel editions..."
	python scripts/generate_parallel_edition.py
	@echo "Parallel editions generated."

# Check terminology consistency
check-terms:
	@echo "Checking terminology consistency..."
	python workflow/check_terminology.py editions/

# Review checklist
review:
	@echo "Review checklist:"
	@echo "  1. Open review/PROGRESS.md and update chapter status"
	@echo "  2. Run: make check-terms"
	@echo "  3. Review each chapter against Dutch source"
	@echo "  4. Update GLOSSARY.md with new terms"
	@echo "  5. Update TRANSLATION_MEMORY.md with verified pairs"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf latex_build/
	find . -name "*.aux" -delete
	find . -name "*.log" -delete
	find . -name "*.out" -delete
	find . -name "*.toc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete."
