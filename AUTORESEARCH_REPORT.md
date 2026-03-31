# Pipeline Audit & Optimization Report

> **Generated:** 2026-03-31
> **Project:** kuyper-antirevolutionary-politics
> **Scope:** Full repo audit — every file, script, workflow, and gap
> **Goal:** Design the optimal end-to-end pipeline for chapter-by-chapter Substack rollout → final PDF publication

---

## 1. Current State Assessment

### What Exists (and Works)

| Component | Status | Quality |
|-----------|--------|---------|
| Dutch source PDFs (Vol 1: 37MB, Vol 2: 33MB) | ✅ Complete | Original 1916-1917 editions |
| Dutch source MD (Vol 1: 1.7MB, Vol 2: 1.4MB) | ✅ Complete | Page-aligned with `—- Page N —-` markers |
| English translation MD (Vol 1: 1.7MB, Vol 2: 1.4MB) | ✅ Complete | AI-generated, human-guided |
| Parallel HTML editions (Vol 1 & 2) | ✅ Generated | Dutch/English side-by-side |
| Annotated HTML editions (Vol 1 & 2) | ✅ Generated | With analytical headnotes |
| Full reading HTML editions (Vol 1 & 2) | ✅ Generated | Clean reading format |
| Print-ready PDFs (Vol 1: 4.2MB, Vol 2: 3.7MB) | ✅ Generated | Via WeasyPrint/Playwright |
| Manuscript chapters (18 of ~31) | ⚠️ Partial | Only `english_refined.md` — no dutch_source or english_draft |
| Translation protocol | ✅ Complete | `config/kuyper_translation_protocol.md` |
| Glossary (30+ terms) | ✅ Complete | `review/GLOSSARY.md` |
| Translation memory (20+ pairs) | ✅ Complete | `review/TRANSLATION_MEMORY.md` |
| Terminology checker | ✅ Working | `workflow/check_terminology.py` |
| Legal review | ✅ Complete | `review/LEGAL_REVIEW.md` |
| Security audit | ✅ Clean | `review/AUDIT_REPORT.md` |
| GitHub issue templates (4 types) | ✅ Complete | Translation error, suggestion, philosophy, bug |
| CONTRIBUTING.md | ✅ Complete | Clear contribution workflow |
| requirements.txt | ✅ Present | 5 dependencies documented |
| Makefile | ✅ Present | 6 targets |

### What's Missing or Broken

| Gap | Impact | Priority |
|-----|--------|----------|
| **No chapter-by-chapter Substack export** | Cannot roll out incrementally | 🔴 Critical |
| **No Substack-formatted output** | HTML/PDFs don't match Substack's editor format | 🔴 Critical |
| **Manuscript chapters incomplete** | Only 18 of ~31 chapters have files; no 3-file workflow (dutch/draft/refined) | 🔴 Critical |
| **No automated quality gate** | No way to know when a chapter is "ready to publish" | 🟡 High |
| **No pipeline orchestration** | Scripts run independently, no `make substack-chapter` | 🟡 High |
| **No chapter status tracking** | PROGRESS.md is manual, not automated | 🟡 High |
| **No diff tool for Dutch vs English** | Manual comparison only | 🟡 High |
| **No automated terminology check on chapter save** | check_terminology.py only runs on editions/ | 🟠 Medium |
| **No Substack API integration** | Manual copy-paste to Substack | 🟠 Medium |
| **No version tagging per published chapter** | Can't track which revision was published | 🟠 Medium |

---

## 2. Repository Structure Audit

### File-by-File Assessment

#### `editions/` — Output Directory
| File | Size | Purpose | Keep? |
|------|------|---------|-------|
| `Kuyper_Antirevolutionary_Politics_Vol1_FULL.md` | 1.7MB | Full English translation Vol 1 | ✅ Keep — source of truth |
| `Kuyper_Antirevolutionary_Politics_Vol2_FULL.md` | 1.4MB | Full English translation Vol 2 | ✅ Keep — source of truth |
| `Kuyper_Antirevolutionary_Politics_Vol1_Dutch.md` | 1.7MB | Dutch source Vol 1 | ✅ Keep — source of truth |
| `Kuyper_Antirevolutionary_Politics_Vol2_Dutch.md` | 1.4MB | Dutch source Vol 2 | ✅ Keep — source of truth |
| `Antirevolutionary_Politics_Vol1.pdf` | 4.2MB | Print-ready PDF Vol 1 | ✅ Keep |
| `Antirevolutionary_Politics_Vol2.pdf` | 3.7MB | Print-ready PDF Vol 2 | ✅ Keep |
| `Antirevolutionary_Politics_Parallel_Vol1.html` | 3.6MB | Parallel edition Vol 1 | ✅ Keep |
| `Antirevolutionary_Politics_Parallel_Vol2.html` | 3.1MB | Parallel edition Vol 2 | ✅ Keep |
| `Antirevolutionary_Politics_Vol1_Annotated_Edition.html` | 2.3MB | Annotated edition Vol 1 | ✅ Keep |
| `Antirevolutionary_Politics_Vol2_Annotated_Edition.html` | 2.4MB | Annotated edition Vol 2 | ✅ Keep |
| `Antirevolutionary_Politics_Vol1_Full_Reading_Edition.html` | 1.8MB | Reading edition Vol 1 | ✅ Keep |
| `Antirevolutionary_Politics_Vol2_Full_Reading_Edition.html` | 1.6MB | Reading edition Vol 2 | ✅ Keep |

**Verdict:** All editions are valuable. No duplicates found (audit report's duplicate warning was from a previous state — already cleaned).

#### `manuscript/` — Chapter Workflow Directory
| Volume | Chapters Present | Expected | Gap |
|--------|-----------------|----------|-----|
| Vol 1 | 8 chapters (ch01-ch08) | ~9 chapters | Missing ch09 (Purpose of State) |
| Vol 2 | 10 chapters (ch01,04,06,08,13,14,15,16,19,22) | ~22 chapters | Missing 12 chapters |

**Current manuscript structure per chapter:**
```
manuscript/volume_1/ch01-introduction/
└── english_refined.md    ← Only file present
```

**Needed structure per chapter:**
```
manuscript/volume_1/ch01-introduction/
├── dutch_source.md       ← Extracted from Dutch FULL.md
├── english_draft.md      ← AI-generated first pass
└── english_refined.md    ← Human-reviewed final
```

#### `scripts/` — Build Scripts
| Script | Function | Status | Issues |
|--------|----------|--------|--------|
| `generate_scholarly_master.py` | Creates annotated HTML editions | ✅ Working | 716 lines, monolithic, hard to maintain |
| `generate_parallel_edition.py` | Dutch/English side-by-side HTML | ✅ Working | Depends on pdfplumber |
| `export_pdf_weasyprint.py` | PDF via WeasyPrint | ✅ Working | |
| `export_pdf_playwright.py` | PDF via Playwright | ✅ Working | |
| `export_pdf_visible.py` | PDF via visible browser | ✅ Working | |
| `export_pdf_puppeteer.js` | PDF via Puppeteer | ✅ Working | Needs npm install |
| `export_to_pdf.py` | Generic PDF export | ✅ Working | |
| `create_print_ready.py` | Print-ready PDF prep | ✅ Working | |
| `analyze_pdf_alignment.py` | PDF alignment verification | ✅ Working | Depends on pypdf |
| `enhance_index_nlp.py` | NLP-enhanced indexing | ✅ Working | Depends on spacy |
| `generate_dutch_md.py` | Dutch PDF → Markdown | ✅ Working | Depends on pdfplumber |
| `generate_scholarly_master.py` | Master edition synthesis | ✅ Working | |
| `refine_markdown_v2.py` | Translation refinement | ✅ Working | |
| `sync_scholarly_to_md.py` | Scholarly → Markdown sync | ✅ Working | |
| `optimize_for_pod.sh` | Print-on-demand optimization | ✅ Working | Uses Ghostscript/QPDF |
| `scholarly_data_expansion.py` | NLP index generation | ✅ Working | |

**Issues:**
- No script for **chapter extraction** from FULL.md
- No script for **Substack formatting**
- No script for **chapter-level quality gates**
- `generate_scholarly_master.py` is 716 lines — should be split into modules

#### `workflow/` — Quality Tools
| Script | Function | Status |
|--------|----------|--------|
| `check_terminology.py` | Terminology consistency checker | ✅ Working |

**Missing:**
- Chapter alignment checker (Dutch vs English paragraph count)
- Omission detector (Dutch paragraphs with no English equivalent)
- Substack formatter
- Chapter status tracker

#### `review/` — Documentation
| File | Purpose | Status |
|------|---------|--------|
| `PROGRESS.md` | Chapter-by-chapter tracking | ⚠️ Manual, outdated |
| `GLOSSARY.md` | Dutch→English terminology | ✅ Complete (30+ terms) |
| `TRANSLATION_MEMORY.md` | Verified translation pairs | ✅ Complete (20+ pairs) |
| `AUDIT_REPORT.md` | Security + file audit | ✅ Complete |
| `LEGAL_REVIEW.md` | Legal analysis | ✅ Complete |
| `REFERENCE_MATERIALS_LICENSE.md` | Reference text provenance | ✅ Complete |

---

## 3. The Optimal Pipeline

### Design Principles

1. **Chapter-first, not volume-first** — Every tool operates at chapter granularity
2. **Automated quality gates** — A chapter doesn't publish until it passes all checks
3. **Substack-native output** — Clean Markdown that pastes directly into Substack's editor
4. **Incremental** — Publish chapter 1, then chapter 2, etc. No big-bang release
5. **Reproducible** — `make substack-chapter CHAPTER=ch01` should work for any chapter

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE: Chapter-by-Chapter                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Dutch FULL.md ──┐                                              │
│                  ├──→ [1. extract-chapter] ──→ dutch_source.md  │
│  Chapter map ────┤                                              │
│                  │                                              │
│  English FULL.md─┤                                              │
│                  ├──→ [2. extract-chapter] ──→ english_draft.md │
│                  │                                              │
│                  └──→ [3. align-check] ──→ alignment_report     │
│                                                                  │
│  dutch_source.md ──┐                                            │
│                    ├──→ [4. quality-gate] ──→ PASS/FAIL         │
│  english_draft.md──┤         ↓                                    │
│                    │    If FAIL: flag for review                 │
│  GLOSSARY.md ──────┤    If PASS: → english_refined.md            │
│                    │                                              │
│  english_refined.md──→ [5. substack-format] ──→ substack/        │
│                          ↓                                        │
│                     [6. publish-checklist]                        │
│                          ↓                                        │
│                     Ready for Substack                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE: Final Publication                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  All chapters refined ──→ [7. assemble-volume] ──→ FULL.md      │
│                              ↓                                    │
│                         [8. generate-editions]                    │
│                              ↓                                    │
│                    HTML editions + PDFs                           │
│                              ↓                                    │
│                         [9. optimize-for-pod]                     │
│                              ↓                                    │
│                    Print-ready PDFs → academia.edu                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1: Chapter Extraction & Alignment (One-Time Setup)

**Scripts to build:**

#### `scripts/extract_chapters.py`
```
Purpose: Split FULL.md files into chapter-level files
Input: editions/Kuyper_Antirevolutionary_Politics_Vol{1,2}_FULL.md
Output: manuscript/volume_{1,2}/ch{NN}-{slug}/dutch_source.md
        manuscript/volume_{1,2}/ch{NN}-{slug}/english_draft.md

Logic:
1. Parse chapter boundaries from § numbering and "CHAPTER" markers
2. For each chapter, extract the Dutch and English text
3. Write to manuscript/volume_N/chNN-slug/dutch_source.md
4. Write to manuscript/volume_N/chNN-slug/english_draft.md
5. Generate a chapter map JSON with chapter numbers, titles, section ranges
```

#### `scripts/check_chapter_alignment.py`
```
Purpose: Verify Dutch and English chapters have matching structure
Input: manuscript/volume_N/chNN-slug/dutch_source.md
       manuscript/volume_N/chNN-slug/english_draft.md
Output: Alignment report (paragraph count, section count, omissions)

Checks:
1. § number match (every Dutch § has an English §)
2. Paragraph count ratio (English should be 80-120% of Dutch)
3. Page marker alignment (same page boundaries)
4. Missing sections (Dutch § with no English equivalent)
5. Extra sections (English § with no Dutch equivalent)
```

### Phase 2: Quality Gate (Per Chapter)

#### `scripts/chapter_quality_gate.py`
```
Purpose: Automated quality check before a chapter can be marked "refined"
Input: manuscript/volume_N/chNN-slug/{dutch_source,english_draft}.md
       review/GLOSSARY.md
Output: PASS/FAIL with detailed report

Checks:
1. Alignment check (from check_chapter_alignment.py)
2. Terminology consistency (from check_terminology.py, chapter-scoped)
3. Forbidden terms scan (modern colloquialisms)
4. Paragraph completeness (no dropped paragraphs)
5. Section header integrity (§ numbering preserved)
6. Minimum length check (chapter isn't suspiciously short)

Output:
- PASS: Chapter is ready for refinement
- FAIL: List of specific issues with file:line references
```

### Phase 3: Substack Export (Per Chapter)

#### `scripts/export_substack.py`
```
Purpose: Format a refined chapter for Substack publication
Input: manuscript/volume_N/chNN-slug/english_refined.md
Output: substack/vol{N}-ch{NN}-{slug}.md

Substack format requirements:
1. Clean Markdown (no YAML frontmatter)
2. H2 for chapter title, H3 for sections
3. No page markers (—- Page N —-)
4. Blockquotes for Scripture/poetry
5. Italic for Dutch terms
6. Footnotes as Substack-compatible footnotes
7. Opening hook paragraph (first 2-3 sentences)
8. Closing CTA ("Next: Chapter X — [title]")
9. Series header ("Antirevolutionary Politics, Vol. I, Chapter X")
10. Tags for Substack's tagging system

Also generates:
- substack/vol{N}-ch{NN}-{slug}-preview.html (for preview before publishing)
- substack/vol{N}-ch{NN}-{slug}-checklist.md (publishing checklist)
```

#### `substack/vol{N}-ch{NN}-{slug}-checklist.md`
```
Purpose: Per-chapter publishing checklist
Contents:
- [ ] Terminology check passed
- [ ] Alignment check passed
- [ ] Human review completed
- [ ] Substack formatting verified
- [ ] Preview HTML reviewed
- [ ] Opening hook compelling
- [ ] Closing CTA links to next chapter
- [ ] Tags added
- [ ] Published to Substack
- [ ] URL recorded
- [ ] Cross-posted to openkuyper.substack.com
```

### Phase 4: Final Assembly (After All Chapters Published)

#### `scripts/assemble_volume.py`
```
Purpose: Reassemble all refined chapters into a single volume
Input: manuscript/volume_N/ch*/english_refined.md
Output: editions/Kuyper_Antirevolutionary_Politics_Vol{N}_FINAL.md

Logic:
1. Read chapter map JSON
2. Concatenate chapters in order
3. Add frontmatter (title page, preface, TOC)
4. Add backmatter (glossary, biographical register, index)
5. Verify section numbering continuity
6. Generate final PDF via existing export scripts
```

---

## 4. Recommended Repository Changes

### New Directories to Create

```
substack/                    ← Substack-formatted chapter exports
├── vol1-ch01-introduction.md
├── vol1-ch01-introduction-preview.html
├── vol1-ch01-introduction-checklist.md
├── vol1-ch02-concept-of-state.md
└── ...

pipeline/                    ← Pipeline orchestration scripts
├── extract_chapters.py
├── check_chapter_alignment.py
├── chapter_quality_gate.py
├── export_substack.py
├── assemble_volume.py
└── chapter_map_vol1.json    ← Generated chapter map
└── chapter_map_vol2.json
```

### Files to Update

| File | Change |
|------|--------|
| `Makefile` | Add `substack-chapter`, `quality-gate`, `extract-chapters`, `assemble-volume` targets |
| `review/PROGRESS.md` | Convert to automated status from pipeline output |
| `requirements.txt` | Add any new dependencies |
| `.gitignore` | Add `substack/*-preview.html` if too large |

### Files to Keep As-Is

All existing scripts, editions, review files, and config files are solid. The pipeline **adds** to them, doesn't replace them.

---

## 5. Execution Order

### Step 1: One-Time Setup (30 minutes)
```bash
# Extract all chapters from FULL.md files
python pipeline/extract_chapters.py

# Verify extraction
make check-alignment
```

### Step 2: Per-Chapter Workflow (Repeat for Each Chapter)
```bash
# 1. Run quality gate
python pipeline/chapter_quality.py --chapter vol1-ch01

# 2. If PASS: refine the chapter (human review)
#    Edit manuscript/volume_1/ch01-introduction/english_refined.md

# 3. Export for Substack
python pipeline/export_substack.py --chapter vol1-ch01

# 4. Review preview
open substack/vol1-ch01-introduction-preview.html

# 5. Publish to Substack (manual copy-paste or API)
# 6. Update checklist
```

### Step 3: After All Chapters Published
```bash
# Assemble final volumes
python pipeline/assemble_volume.py --volume 1
python pipeline/assemble_volume.py --volume 2

# Generate final editions
make editions
make pdf

# Optimize for print-on-demand
bash scripts/optimize_for_pod.sh

# Upload to academia.edu
```

---

## 6. Substack Rollout Strategy

### Recommended Order

**Volume I: Principles** (foundational concepts first)
1. Ch 1: Introduction (§§ 1-24) — Kuyper's foreword, why this book exists
2. Ch 2: The Concept of the State — What is law? What is right?
3. Ch 3: The Essence of the State — State as surgical bandage
4. Ch 8: The Sovereignty — Sphere Sovereignty (the big idea)
5. Ch 6: The Land — Organic development
6. Ch 7: The Supreme Authority — De Overheid
7. Ch 5: The Constitution
8. Ch 4: Transition to Modern Era
9. Ch 9: The Purpose of the State

**Volume II: Application** (concrete politics)
1. Ch 1: Introduction
2. Ch 19: Church and State (most relevant to modern readers)
3. Ch 8: Administration of the Provinces
4. Ch 13: Justice
5. Ch 16: Care for Public Health
6. Ch 14: The Finances
7. Ch 4: Council of State and Ministers
8. Ch 6: General Accounting Office
9. Ch 15: The Public Propriety
10. Ch 22: Party Policy at the Ballot Box

### Substack Post Structure

Each chapter post should follow this template:

```
Title: Kuyper on [Topic]: [Compelling Hook]
Subtitle: Antirevolutionary Politics, Vol. I, Chapter X

[Opening hook — 2-3 sentences that draw the reader in]

[Chapter content — formatted for Substack's editor]

[Closing CTA]
→ Next: Chapter X+1 — [Title]
→ Read the full open translation: [repo URL]
→ Suggest an improvement: [GitHub issues URL]

Tags: abraham-kuyper, neo-calvinism, political-theology, sphere-sovereignty, reformed, dutch-history
```

---

## 7. GitHub Repo Optimization

### Repos to Study (Prioritized)

| Repo | Why | Action |
|------|-----|--------|
| [yihong0618/bilingual_book_maker](https://github.com/yihong0618/bilingual_book_maker) (9k⭐) | Most popular AI book translation tool | Study chunking strategy, glossary system |
| [DiScholEd/pipeline-digital-scholarly-editions](https://github.com/DiScholEd/pipeline-digital-scholarly-editions) | EU-funded scholarly edition pipeline | Study their OCR→correction→encoding→publication flow |
| [sources.neocalvinism.org](https://sources.neocalvinism.org/translations.php) | Your exact domain — existing translation corrections | Cross-reference their corrections against your translation |
| [FrankensteinVariorum](https://github.com/FrankensteinVariorum) | Multi-version text collation | Study their parallel edition approach |
| [homermultitext/hmt-archive](https://github.com/homermultitext/hmt-archive) | Ancient text → translation pipeline | Study their scholarly apparatus model |
| [TEIC/TEI](https://github.com/TEIC/TEI) (329⭐) | Text Encoding Initiative standard | Understand scholarly encoding patterns |
| [dh-tech/awesome-digital-humanities](https://github.com/dh-tech/awesome-digital-humanities) (364⭐) | DH tools directory | Browse for tools you didn't know existed |
| [KazKozDev/book-translator](https://github.com/KazKozDev/book-translator) (48⭐) | Two-stage: translate → self-refine | Study their quality refinement loop |

### What to Skip

| Repo | Why Skip |
|------|----------|
| `xunbu/docutranslate` (913⭐) | Chinese-focused, not relevant for Dutch→English |
| `LibreTranslate/LibreTranslate` (14k⭐) | Generic MT engine — you need scholarly quality, not speed |
| `ElegantLaTeX/ElegantBook` (2.4k⭐) | Chinese LaTeX class — different typography needs |
| Most LaTeX templates | You already have TeX Live 2025 + memoir + EB Garamond |

---

## 8. Cost & Time Estimates

| Phase | Time | Cost |
|-------|------|------|
| Pipeline setup (scripts) | 4-6 hours | $0 |
| Chapter extraction (one-time) | 30 minutes | $0 |
| Per-chapter quality gate + review | 2-4 hours/chapter | $0 |
| Substack formatting + publish | 30 min/chapter | $0 |
| Full Vol 1 (9 chapters) | 18-36 hours | $0 |
| Full Vol 2 (22 chapters) | 44-88 hours | $0 |
| Final assembly + PDF generation | 4-8 hours | $0 |
| **Total** | **70-140 hours** | **$0** |

### Accelerated Option (AI-Assisted)

If you use AI for initial refinement (then human-review):
- Per-chapter review: 30-60 minutes instead of 2-4 hours
- Full Vol 1: 5-10 hours
- Full Vol 2: 12-22 hours
- **Total: 25-50 hours** + API costs (~$20-60)

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Dutch OCR has systematic errors | Medium | High | Run audit_ocr_quality.py before extraction |
| Translation has theological errors | High | High | Quality gate + human review + NRI cross-reference |
| Substack formatting breaks | Low | Medium | Preview HTML before publishing |
| Chapter order confusion | Low | Low | Chapter map JSON enforces order |
| Scope creep (Vol III companion) | Medium | Medium | Phase it — Vol I & II first, Vol III later |
| API costs for AI refinement | Low | Low | Set budget cap, use local models where possible |

---

## 10. Immediate Next Steps

1. **Create `pipeline/` directory** with the 5 scripts defined above
2. **Run `extract_chapters.py`** to populate manuscript/ with all chapters
3. **Run `check_chapter_alignment.py`** to identify gaps
4. **Pick Chapter 1** (Vol 1, Ch 1: Introduction) as the pilot
5. **Run quality gate** on Chapter 1
6. **Export to Substack format**
7. **Publish to Substack** as a test
8. **Iterate** on the pipeline based on what works

---

## Appendix: Current Chapter Inventory

### Volume I: Principles (9 chapters expected)

| # | Chapter | Sections | Manuscript File | Size | Status |
|---|---------|----------|-----------------|------|--------|
| 1 | Introduction | §§ 1-24 | ch01-introduction/english_refined.md | 202K | ✅ Exists |
| 2 | The Concept of the State | §§ 1-6 | ch02-concept-of-state/english_refined.md | 107K | ✅ Exists |
| 3 | The Essence of the State | §§ 1-13 | ch03-essence-of-state/english_refined.md | 27K | ✅ Exists |
| 4 | Transition to Modern Era | — | ch04-transition-modern-era/english_refined.md | 49K | ✅ Exists |
| 5 | The Constitution | — | ch05-constitution/english_refined.md | 83K | ✅ Exists |
| 6 | The Land | §§ 1-7 | ch06-the-land/english_refined.md | 140K | ✅ Exists |
| 7 | The Supreme Authority | §§ 1-10 | ch07-supreme-authority/english_refined.md | 64K | ✅ Exists |
| 8 | The Sovereignty | §§ 1-8 | ch08-sovereignty/english_refined.md | 985K | ✅ Exists |
| 9 | The Purpose of the State | §§ 1-24+ | — | — | ❌ Missing |

### Volume II: Application (22 chapters expected)

| # | Chapter | Manuscript File | Size | Status |
|---|---------|-----------------|------|--------|
| 1 | Introduction | ch01-introduction/english_refined.md | 264K | ✅ Exists |
| 2-3 | — | — | — | ❌ Missing |
| 4 | Council of State | ch04-council-state/english_refined.md | 147K | ✅ Exists |
| 5 | — | — | — | ❌ Missing |
| 6 | General Accounting Office | ch06-accounting-office/english_refined.md | 102K | ✅ Exists |
| 7 | — | — | — | ❌ Missing |
| 8 | Administration of Provinces | ch08-provinces/english_refined.md | 366K | ✅ Exists |
| 9-12 | — | — | — | ❌ Missing |
| 13 | Justice | ch13-justice/english_refined.md | 75K | ✅ Exists |
| 14 | The Finances | ch14-finances/english_refined.md | 40K | ✅ Exists |
| 15 | The Public Propriety | ch15-public-propriety/english_refined.md | 27K | ✅ Exists |
| 16 | Care for Public Health | ch16-public-health/english_refined.md | 199K | ✅ Exists |
| 17-18 | — | — | — | ❌ Missing |
| 19 | Church and State | ch19-church-state/english_refined.md | 179K | ✅ Exists |
| 20-21 | — | — | — | ❌ Missing |
| 22 | Party Policy at the Ballot Box | ch22-party-policy/english_refined.md | 67K | ✅ Exists |

**Summary:** 18 of 31 chapters have manuscript files. All are `english_refined.md` only — no `dutch_source.md` or `english_draft.md` yet.
