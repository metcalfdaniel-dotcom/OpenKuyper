# Archive Notes

This directory contains superseded files from earlier phases of the OpenKuyper project.

## Contents

### `pipeline.go` + `go.mod`
- **Original purpose**: Early Go-based pipeline for OCR and translation
- **Superseded by**: `pipeline/gemini_ocr_pipeline.py` (Python + Gemini 2.5 Flash)
- **Date archived**: 2025-04-22
- **Reason**: Switched to Python ecosystem for better integration with ML libraries; Gemini Flash offers superior OCR accuracy on 1916 Dutch typography

### `NEXT_PHASE.md`
- **Original purpose**: Planning document for next steps after Phase 1
- **Superseded by**: Integrated pipeline in `pipeline/master_pipeline.py`
- **Date archived**: 2025-04-22
- **Reason**: Plans consolidated into executable code; no longer need static planning doc

### `OCR_AND_LATEX_PLAN.md`
- **Original purpose**: Detailed plan for OCR processing and LaTeX output
- **Superseded by**: `pipeline/gemini_ocr_pipeline.py` with automatic markdown compilation
- **Date archived**: 2025-04-22
- **Reason**: Pipeline now handles OCR + translation + compilation automatically

## Current Pipeline Architecture

See `pipeline/` directory for active components:
- `gemini_ocr_pipeline.py` — OCR + Draft A generation
- `adjudicator.py` — Multi-draft (A/B/C) comparison with agentic selection
- `qa_gates.py` — Quality assurance (style, terminology, anachronisms)
- `termbase.py` — Dynamic terminology lockfile
- `master_pipeline.py` — Integrated orchestrator
