# Next Phase: Quality Audit & Print-Ready Compilation

> **Status:** Planning document — awaiting execution
> **Created:** 2026-03-31
> **Predecessor:** [OCR_AND_LATEX_PLAN.md](OCR_AND_LATEX_PLAN.md)

This document defines the three-phase workflow to move from the current AI-generated translation to a print-ready scholarly edition. It covers OCR quality auditing, translation quality auditing, and LaTeX book compilation.

---

## Phase 1: OCR Quality Audit (Dutch Source)

### Current State

The Dutch source text was extracted from the original 1916 PDFs (`source-materials/antirevolutionai01kuyp.pdf` and `antirevolutiona02kuyp.pdf`). It lives in `editions/Kuyper_Antirevolutionary_Politics_Vol{1,2}_Dutch.md`.

**Known OCR artifacts observed:**
- Missing spaces: `tothetschrijven`, `meerdanverleid`, `Kerkiiistorie` (should be `Kerkhistorie`)
- Hyphenation artifacts: `geschied-` / `kundig` split across lines
- Character substitutions: `Schwëizer` (should be `Schweizer`)
- Page header/footer bleed: Roman numeral page numbers (`VIII`, `IX`) mixed into body text
- Punctuation spacing issues: `? ,` instead of `?,`

### Tools to Build

#### 1. `scripts/audit_ocr_quality.py` — Automated OCR Scan

Compares extracted Markdown against the raw PDF text layer (using `pdfminer.six`, already installed).

**What it does:**
- Scans every page for common Dutch OCR error patterns
- Flags: double spaces, missing spaces around punctuation, known character confusions (ë/e, ij/y, long s), hyphenated word fragments at line breaks, page number bleed into body text
- Outputs a scored report: pages ranked by error density (0-100)
- Generates `reports/ocr_errors_vol{1,2}.csv` with page/line/position for each error

**Dependencies:** `pdfminer.six` (installed), `pandas`

#### 2. `scripts/spot_check_ocr.py` — Random Sampling Review

Selects N random pages from the PDF, renders them as images, and displays side-by-side: original PDF image vs extracted text.

**What it does:**
- Randomly samples pages for manual review
- Lets you score each page (1-5 quality scale)
- Tracks scores over time to measure improvement
- Outputs `reports/ocr_spot_check_scores.csv`

**Dependencies:** `pdf2image`, `poppler` (brew install poppler)

#### 3. `scripts/fix_ocr_common.py` — Automated Cleanup

Fixes known patterns: rejoins hyphenated words, fixes spacing, corrects common character confusions.

**What it does:**
- Applies rule-based fixes for common Dutch OCR errors
- Optionally uses `byt5-base-dutch-ocr-correction` model from HuggingFace for post-correction
- Produces a "cleaned" version with a diff report
- Never overwrites originals — writes to `editions/*_Dutch_cleaned.md`

**Dependencies:** `transformers` (optional, for byt5 model)

### When to Re-Run Full OCR

| Condition | Action |
|-----------|--------|
| Audit score < 85/100 on any chapter | Re-extract that chapter with MinerU or Marker |
| Spot-check reveals systematic errors | Re-run full OCR pipeline |
| Dutch source has poor text layer | Use image-based OCR (PaddleOCR) |

### Recommended Pipeline

```
Dutch PDF → Current MD (existing)
                ↓
        [audit_ocr_quality.py]
                ↓
    ┌───────────┼───────────────┐
    ↓           ↓               ↓
  Error      Error          Quality
  Report     Score          Report
  (CSV)      (0-100)        (summary)
                ↓
        [fix_ocr_common.py] (if score < 90)
                ↓
        Cleaned Dutch MD
```

---

## Phase 2: Translation Quality Audit

### Current State

The English translation exists in `editions/Kuyper_Antirevolutionary_Politics_Vol{1,2}_FULL.md` (~1.7MB Vol 1, ~1.4MB Vol 2). It was AI-generated with human guidance following the protocol in `config/kuyper_translation_protocol.md`.

### Tools to Build

#### 1. `scripts/audit_translation_quality.py` — Multi-Pass Audit

**Pass 1 — Alignment Check:**
- Verifies Dutch and English have matching section counts (§ numbers, chapter boundaries)
- Flags missing or extra sections
- Outputs `reports/translation_alignment_vol{1,2}.csv`

**Pass 2 — Terminology Consistency:**
Checks that key theological terms are translated consistently per the protocol:

| Dutch Term | Required English | Common Errors |
|------------|-----------------|---------------|
| Souvereiniteit in eigen kring | Sphere Sovereignty | "sovereignty in own sphere" |
| De Overheid | The Magistrate | "The State", "The Government" |
| Ordinantiën | Ordinances | "rules", "laws", "ordinances of God" |
| Gemene Gratie | Common Grace | "general grace" |
| Antithese | The Antithesis | "opposition", "conflict" |
| Palingenesis | Regeneration | "rebirth", "renewal" |

**Pass 3 — Voice Ground Truth Comparison:**
- Samples passages and compares against *Lectures on Calvinism* (Stone Lectures) for cadence matching
- Flags modern colloquialisms, dynamic equivalence that risks theological imprecision
- Checks for anachronistic vocabulary

**Pass 4 — Omission Detection:**
- Finds Dutch paragraphs with no English equivalent (and vice versa)
- Reports paragraph count mismatches per chapter

#### 2. `scripts/translation_diff_viewer.py` — Interactive Review

Renders Dutch and English side-by-side, paragraph-aligned.

**What it does:**
- Highlights terminology deviations from the protocol
- Lets you flag passages for human review
- Exports a "review queue" of flagged passages
- Can run as a local web app or terminal TUI

**Dependencies:** `rich` (for terminal) or `flask` (for web)

#### 3. `scripts/glossary_audit.py` — Terminology Tracker

**What it does:**
- Extracts all Dutch theological terms from the source
- Maps each to its English translation in the current text
- Flags inconsistencies (same Dutch term → different English translations)
- Outputs `reports/terminology_map_vol{1,2}.csv`

### Quality Thresholds

| Score | Status | Action |
|-------|--------|--------|
| Green: < 2% deviations, 100% alignment, zero omissions | Ship-ready | Proceed to LaTeX |
| Yellow: 2-5% deviations, minor alignment gaps | Needs review | Fix flagged passages |
| Red: > 5% deviations, missing sections | Needs rework | Re-translate affected chapters |

### Recommended Pipeline

```
Dutch MD ──┐
           ├──→ [audit_translation_quality.py] ──→ Quality Report
English MD ─┘           ↓
                  ┌─────┼──────┐
                  ↓     ↓      ↓
             Terminology  Style    Accuracy
             Consistency  Audit    Check
                  ↓
             [translation_diff_viewer.py] (for flagged passages)
                  ↓
             [glossary_audit.py] (final terminology pass)
                  ↓
             Approved English MD
```

---

## Phase 3: LaTeX Book Compilation

### Current State

- **XeLaTeX:** TeX Live 2025 ✅
- **latexmk:** Installed ✅
- **EB Garamond font:** Installed via Homebrew ✅
- **memoir class:** Available ✅
- **Required packages:** fontspec, polyglossia, xcolor, graphicx, hyperref, geometry, setspace, microtype, footmisc, titlesec, imakeidx — all installed ✅

### Tools to Build

#### 1. `scripts/md_to_latex.py` — Markdown → LaTeX Converter

Reads the existing English `.md` files and converts them to a structured LaTeX project.

**What it does:**
- Converts Markdown headings → `\chapter{}`, `\section{}`, `\subsection{}`
- Preserves `§` numbering as `\sectionnum{}`
- Converts italic/bold → `\textit{}` / `\textbf{}`
- Handles Dutch terms with `\dutch{}` macro
- Splits output into chapter files matching the plan structure
- Generates frontmatter (title page, copyright, TOC, preface)
- Generates backmatter (glossary, biographical register, index)

**Output structure:**
```
latex/
├── kuyper-common.sty          # Shared style package
├── kuyper-vol1/
│   ├── vol1.tex               # Master document
│   ├── frontmatter/
│   │   ├── titlepage.tex
│   │   ├── copyright.tex
│   │   ├── preface.tex
│   │   └── contents.tex
│   ├── mainmatter/
│   │   ├── ch01-introduction.tex
│   │   ├── ch02-concept-of-law.tex
│   │   └── ... (all chapters)
│   └── backmatter/
│       ├── appendix-a-glossary.tex
│       ├── appendix-b-biographical.tex
│       └── index.tex
└── kuyper-vol2/
    └── (same structure)
```

#### 2. `latex/kuyper-common.sty` — Shared Style Package

```latex
% Typography: EB Garamond 11pt
\setmainfont{EB Garamond}[
  Ligatures=TeX,
  Numbers=OldStyle,
]

% Section formatting matching Kuyper's original § numbering
\newcommand{\sectionnum}[1]{\S\,#1}

% Dutch term highlighting
\newcommand{\dutch}[1]{\textit{#1}}
\newcommand{\term}[2]{\textbf{#1} (\dutch{#2})}

% Page headers with volume/chapter info
\pagestyle{ruled}
```

#### 3. `Makefile` — Build System

```makefile
VOLUMES = vol1 vol2

all: $(VOLUMES)

vol1:
	cd latex/kuyper-vol1 && latexmk -xelatex vol1.tex

vol2:
	cd latex/kuyper-vol2 && latexmk -xelatex vol2.tex

clean:
	latexmk -c latex/kuyper-vol1 latex/kuyper-vol2

pdf: all
	# Output: latex/kuyper-vol1/vol1.pdf, latex/kuyper-vol2/vol2.pdf
```

#### 4. `scripts/verify_pdf_quality.py` — Post-Compilation Check

**What it does:**
- Verifies PDF page count matches expected chapter count
- Checks for missing fonts (all should be EB Garamond)
- Validates trim size (6"×9")
- Checks for orphan/widow lines
- Reports any compilation warnings

### Print-Ready Output Specifications

| Property | Value |
|----------|-------|
| Trim size | 6" × 9" (standard academic) |
| Font | EB Garamond 11pt |
| Margins | 0.75" inner, 0.5" outer (gutter for binding) |
| Headers | Chapter title (verso) / Section title (recto) |
| Footnotes | Bottom of page, single-spaced |
| Output | PDF suitable for IngramSpark, Amazon KDP |

### Recommended Pipeline

```
Approved English MD
        ↓
  [md_to_latex.py]
        ↓
  ┌─────┴─────┐
  ↓           ↓
kuyper-vol1/  kuyper-vol2/
  ↓           ↓
  latexmk     latexmk
  ↓           ↓
vol1.pdf      vol2.pdf
  ↓           ↓
  [verify_pdf_quality.py]
  ↓
Print-ready PDFs → editions/
```

---

## Execution Plan

### Phase 1: Audit (1-2 days)
- [ ] Run `audit_ocr_quality.py` on both volumes
- [ ] Run `spot_check_ocr.py` (sample 20 pages per volume)
- [ ] Run `audit_translation_quality.py` on both volumes
- [ ] Generate reports → decide what needs rework

### Phase 2: Fix (as needed)
- [ ] Re-run OCR on low-scoring chapters (if audit score < 85)
- [ ] Fix translation inconsistencies (if deviations > 2%)
- [ ] Re-audit until green

### Phase 3: Compile (1 day)
- [ ] Build LaTeX project structure (`latex/` directory)
- [ ] Run `md_to_latex.py` to convert approved MD → LaTeX
- [ ] Compile Vol 1: `make vol1`
- [ ] Compile Vol 2: `make vol2`
- [ ] Run `verify_pdf_quality.py` on both PDFs
- [ ] Copy print-ready PDFs to `editions/`

### Phase 4: Publish
- [ ] Commit PDFs to repo
- [ ] Tag release (e.g., `v1.0-print-ready`)
- [ ] Update README with download links

---

## Dependencies Summary

| Tool | Status | Install Command |
|------|--------|----------------|
| pdfminer.six | ✅ Installed | `pip install pdfminer.six` |
| pdf2image | ❌ Needed | `pip install pdf2image && brew install poppler` |
| pandas | ❌ Needed | `pip install pandas` |
| transformers | ⚠️ Optional | `pip install transformers` (for byt5 OCR correction) |
| rich | ❌ Needed | `pip install rich` (for terminal diff viewer) |
| XeLaTeX | ✅ Installed | TeX Live 2025 |
| EB Garamond | ✅ Installed | `brew install --cask font-eb-garamond` |
| latexmk | ✅ Installed | TeX Live 2025 |

---

## Cost Estimates

| Phase | Cost | Time |
|-------|------|------|
| OCR Audit | $0 (local tools) | 2-4 hours |
| Translation Audit | $0 (local tools) | 4-8 hours |
| OCR Rework (if needed) | $0 (local) or $10-20 (API) | 1-2 days |
| Translation Rework (if needed) | $10-40 (API credits) | 1-3 days |
| LaTeX Compilation | $0 | 4-8 hours |
| **Total** | **$0-60** | **3-7 days** |
