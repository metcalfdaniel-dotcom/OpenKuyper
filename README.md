# Kuyper: Antirevolutionary Politics

**An open English translation of Abraham Kuyper's *Antirevolutionaire Staatkunde* (1916–1917)**

A 2-volume open translation project of Abraham Kuyper's magnum opus on political theology — the mature synthesis of Neo-Calvinist thought applied to the machinery of the modern state.

**Open to the public. Open to critique. Open to improvement.**

📝 **Follow the project blog:** [openkuyper.substack.com](https://openkuyper.substack.com)

---

## About This Project

This is an **open translation** — not a closed scholarly edition. The methodology, pipeline code, and clean translations live here in the open. Anyone can read, fork, critique the translation choices, suggest improvements to the pipeline, or build their own edition from the materials here.

The original Dutch text *Antirevolutionaire Staatkunde* (1916–1917) is in the public domain. This English translation and all project materials are released under the **MIT License** — use it however you want.

---

## Repository Structure

This is the **public, auditable repository**. It contains:
- ✅ Translation pipeline code (open for improvement)
- ✅ Methodology and style database
- ✅ Clean English translations
- ✅ Critical editions with translator notes
- ✅ Terminology database

**Working files** (raw OCR outputs, source PDFs, draft iterations) are kept in the private companion repo:
🔗 `github.com/metcalfdaniel-dotcom/antirevolutionary-politics` (private)

This split keeps the public repo clean and auditable while preserving full working materials for the translation team.

---

## Overview

*Antirevolutionaire Staatkunde* (Antirevolutionary Politics) is Kuyper's most systematic work of political theory. Originally published in 1916–1917, it represents the culmination of his lifelong project: articulating a Christian life-system that engages the modern state not by retreating into isolation, but by asserting the **Sphere Sovereignty** of social institutions under the ultimate Sovereignty of God.

This repository contains:
- **Dutch source texts** — original 1916–1917 editions (PDF and Markdown)
- **English translation** — full 2-volume translation (Markdown, HTML, PDF)
- **Parallel editions** — Dutch/English side-by-side reading editions

- **Translation protocol** — standards and stylistic constraints for the translation
- **Build scripts** — PDF generation, parallel edition synthesis, NLP indexing
- **OCR & compilation plan** — roadmap for refining the translation and producing print-ready LaTeX volumes

---

## Project Structure

```
├── pipeline/                          # Translation pipeline (open for contribution)
│   ├── three_tier_pipeline.py         # Main orchestrator: Flash→Pro→Flash
│   ├── gemini_ocr_pipeline.py         # OCR + Draft generation
│   ├── adjudicator.py                 # Multi-draft comparison agent
│   ├── qa_gates.py                    # Quality assurance suite
│   └── termbase.py                    # Dynamic terminology lockfile
│
├── termbase/
│   └── kuyper_termbase.json           # 54 Dutch→English mappings with context rules
│
├── analysis/
│   └── COMPREHENSIVE_STYLE_DATABASE.md # Algorithmic style analysis (5,123 sentences)
│
├── manuscript/                        # Translation output
│   ├── front-matter/                  # Foreword (clean + critical editions)
│   ├── volume_1/                      # Chapters 1–9
│   └── volume_2/                      # Chapters 10–22
│
├── reference/                         # Source texts for style analysis
│   ├── Faith - Abraham Kuyper.txt
│   ├── Lectures on Calvinism.pdf
│   └── ...
│
├── config/
│   └── kuyper_translation_protocol.md # Translation standards
│
├── tools/                             # Analysis scripts
│   └── kuyper_comprehensive_analyzer.py
│
├── archive/                           # Superseded files (documented)
│   └── ARCHIVE_NOTES.md
│
├── editions/                          # Compiled outputs
│   └── (PDF, HTML, parallel editions)
```

**Note:** Source PDFs and raw OCR JSON outputs are kept in the private working repo.

---

## Translation Pipeline

This project uses a **three-tier AI pipeline** for translation:

### Tier 1: OCR + Draft Generation (Gemini 2.5 Flash)
- OCRs scanned 1916 Dutch pages
- Generates Draft A (faithful/periodic style) and Draft B (literal gloss)
- Fast and cost-effective (~$0.001/page)

### Tier 2: Adjudication (Gemini 2.5 Pro)
- Compares Draft A vs Draft B vs existing Haiku translation (Draft C)
- Evaluates on: theological precision (30%), voice fidelity (30%), structural integrity (20%), modernization avoidance (15%), consistency (5%)
- Selects winner automatically with detailed rationale

### Tier 3: Final Polish (Gemini 2.5 Flash)
- Produces **two editions**:
  1. **Clean Edition** — Publication-ready English text
  2. **Critical Edition** — English text with inline translator notes [like this] for contested terms, ambiguities, and alternative renderings

### Context-Aware Terminology
The pipeline includes a dynamic termbase with **context rules** for polysemous Dutch terms. The most important:
- **"Recht"** → "LAW" in institutional/jurisprudential contexts, "RIGHT" in moral/theological contexts
- **"Geest"** → "spirit" (context determines: human spirit vs Holy Spirit)
- **"Wetenschap"** → "science" (Kuyper's era: systematized knowledge, not modern empirical science)

---

│   ├── Antirevolutionary_Politics_Parallel_Vol1.html     # Parallel reading
│   ├── Antirevolutionary_Politics_Parallel_Vol2.html
│   ├── Antirevolutionary_Politics_Vol1_Annotated_Edition.html
│   ├── Antirevolutionary_Politics_Vol1_Full_Reading_Edition.html
│   ├── Antirevolutionary_Politics_Vol2_Annotated_Edition.html
│   └── Antirevolutionary_Politics_Vol2_Full_Reading_Edition.html
├── scripts/
│   ├── generate_parallel_edition.py      # Dutch/English parallel HTML
│   ├── generate_scholarly_master.py      # Master edition synthesis
│   ├── scholarly_data_expansion.py       # NLP index generation
│   ├── create_print_ready.py             # Print-ready PDF prep
│   ├── export_pdf_*.py/js                # Various PDF export pipelines
│   ├── generate_dutch_md.py              # Dutch text → Markdown
│   ├── refine_markdown_v2.py             # Translation refinement
│   ├── enhance_index_nlp.py              # NLP-enhanced indexing
│   ├── sync_scholarly_to_md.py           # Scholarly → Markdown sync
│   ├── analyze_pdf_alignment.py          # PDF alignment verification
│   └── optimize_for_pod.sh               # Print-on-demand optimization
├── manuscript/
│   ├── volume_1/
│   │   ├── ch01-introduction/
│   │   ├── ch02-concept-of-state/
│   │   ├── ... (8 chapters total)
│   │   └── ch08-sovereignty/
│   └── volume_2/
│       ├── ch01-introduction/
│       ├── ch04-council-state/
│       ├── ... (10 chapters total)
│       └── ch22-party-policy/
├── reference/
│   ├── Faith - Abraham Kuyper.*          # Reference text
│   ├── Lectures on Calvinism.*           # Stone Lectures (ground truth)
│   ├── Saved by Grace Alone.*            # Reference text
│   └── The Sanctifying Work of the Hol.* # Reference text
    └── compendium.md                     # Computational theology reference
├── prepend_md_rights.py                  # Rights/attribution front matter
├── OCR_AND_LATEX_PLAN.md                 # OCR options & LaTeX compilation plan
├── LICENSE                               # MIT License
└── README.md
```

---

## Translation Protocol

The translation follows a rigorous protocol (see `config/kuyper_translation_protocol.md`):

### Voice Ground Truth
- **Primary:** *Lectures on Calvinism* (1898 Stone Lectures) — definitive standard for Kuyper's English cadence
- **Terminology:** *The Work of the Holy Spirit* and *To Be Near Unto God* (trans. Henri de Vries) — baseline for theological nomenclature

### Key Theological Concepts
| Dutch Term | English Translation | Notes |
|------------|-------------------|-------|
| Souvereiniteit in eigen kring | Sphere Sovereignty | Central structural principle |
| Gemene Gratie | Common Grace | God's restraint of sin |
| Ordinantiën | Ordinances of God | Never "rules" or "laws" |
| De Overheid | The Magistrate | Not "The State" |
| Antithese | The Antithesis | Spiritual cleavage |
| Organisch vs. Mechanisch | Organic vs. Mechanical | Living growth vs. artificial construct |
| Palingenesis | Regeneration | the new birth |

### Stylistic Constraints
- Late 19th/Early 20th Century Academic Reformed prose
- Preserve Kuyper's sweeping periodic sentences
- No modern colloquialisms or dynamic equivalence that risks theological imprecision
- Elevated, classical vocabulary (*ordinance*, *sphere*, *sovereignty*, *antithesis*)

---

## Volume Contents

### Volume I: Principles
The foundational principles of Antirevolutionary politics — the concept of law, the sense of right, the origin of the state, sphere sovereignty, and the antithesis between Christian and Revolutionary worldviews.

### Volume II: Application
The application of Antirevolutionary principles to concrete political questions — suffrage, education, labor, church-state relations, and the organic development of society.


- **Encyclopedic Glossary** — Neo-Calvinist concepts with detailed definitions
- **Biographical Register** — Key figures (Groen van Prinsterer, Thorbecke, Schaepman, etc.)
- **Master Index** — Comprehensive topical index with NLP-enhanced thematic clustering
- **Synopticon** — Cross-reference index of "Great Ideas" across the work

---

## Building Editions

### Prerequisites
```bash
# Python scripts
pip install weasyprint playwright

# Puppeteer (for JS-based PDF export)
cd scripts && npm install
```

### Generate Parallel Edition (Dutch/English side-by-side)
```bash
python scripts/generate_parallel_edition.py
```

### Generate Master Edition
```bash
python scripts/generate_scholarly_master.py
```

### Export to PDF
```bash
# WeasyPrint
python scripts/export_pdf_weasyprint.py

# Playwright (visible browser)
python scripts/export_pdf_visible.py

# Puppeteer
node scripts/export_pdf_puppeteer.js
```

### Print-on-Demand Optimization
```bash
bash scripts/optimize_for_pod.sh
```

---

## OCR Refinement & LaTeX Compilation

See [`OCR_AND_LATEX_PLAN.md`](OCR_AND_LATEX_PLAN.md) for:
- **Best OCR tools** for re-extracting Dutch source text (MinerU, Marker, PDFMathTranslate, PaddleOCR, and more)
- **Translation pipeline options** using Claude, OpenAI, Gemini, or local models
- **Systematic workflow** for working through the original text chapter by chapter
- **LaTeX compilation plan** for producing 3 print-ready volumes with:
  - Two appendices per volume (Theological Glossary + Biographical Register)

  - Master index and synopticon cross-references
  - Print-on-demand ready PDFs

---

## Contributing

This is an open translation. Contributions are welcome:

- **Translation improvements** — spot errors, suggest better phrasing, refine theological terminology
- **OCR refinement** — help re-extract and clean up the Dutch source text
- **Index work** — improve the master index, add cross-references, expand the synopticon
- **LaTeX typesetting** — help build the print-ready volumes
- **Critique and review** — read the translation, flag issues, suggest improvements

Open an issue or submit a pull request. No gatekeeping — this project exists to be improved.

---

## Rights & License

**Original Work:** *Antirevolutionaire Staatkunde* by Abraham Kuyper (1916–1917) — public domain worldwide.

**This Translation & Project Materials:** MIT License. Free to use, modify, distribute, and build upon for any purpose. See [`LICENSE`](LICENSE) for full terms, including what is and isn't covered.

**Reference Materials:** Included for translation guidance only. See [`review/REFERENCE_MATERIALS_LICENSE.md`](review/REFERENCE_MATERIALS_LICENSE.md) for provenance and copyright status of each reference text.

**AI Disclosure:** This translation was prepared with the assistance of advanced AI systems. The translation is human-guided and verified. AI was used for text extraction, initial translation drafts, index synthesis, parallel text alignment, and apparatus generation.

---

## Background

Abraham Kuyper (1837–1920) was a Dutch statesman, theologian, journalist, and Prime Minister of the Netherlands (1901–1905). He founded the Free University of Amsterdam, the Anti-Revolutionary Party, and the Reformed Churches in the Netherlands. His political theology of **Sphere Sovereignty** remains influential in Christian democratic thought worldwide.

This open translation project aims to make Kuyper's granular, principled application of Neo-Calvinist thought accessible to a modern English-speaking audience — in the open, for anyone to read, critique, and improve.
