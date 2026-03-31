# Kuyper: Antirevolutionary Politics

**English translation of Abraham Kuyper's *Antirevolutionaire Staatkunde* (1916–1917)**

A 3-volume scholarly edition of Abraham Kuyper's magnum opus on political theology — the mature synthesis of Neo-Calvinist thought applied to the machinery of the modern state.

---

## Overview

*Antirevolutionaire Staatkunde* (Antirevolutionary Politics) is Kuyper's most systematic work of political theory. Originally published in 1916–1917, it represents the culmination of his lifelong project: articulating a Christian life-system that engages the modern state not by retreating into isolation, but by asserting the **Sphere Sovereignty** of social institutions under the ultimate Sovereignty of God.

This repository contains:
- **Dutch source texts** — original 1916–1917 editions (PDF)
- **English translation** — full 3-volume scholarly edition (Markdown, HTML, PDF)
- **Parallel editions** — Dutch/English side-by-side reading editions
- **Companion volume** — encyclopedic glossary, biographical register, master index
- **Translation protocol** — scholarly standards and stylistic constraints
- **Build scripts** — PDF generation, parallel edition synthesis, NLP indexing

---

## Project Structure

```
├── config/
│   └── kuyper_translation_protocol.md    # Translation standards & pipeline
├── source-materials/
│   ├── antirevolutionai01kuyp.pdf        # Dutch Vol. 1 (original, 37MB)
│   ├── antirevolutiona02kuyp.pdf         # Dutch Vol. 2 (original, 33MB)
│   ├── lectures_on_calvinism.*           # Stone Lectures (voice ground truth)
│   ├── holy_spirit.*                     # Work of the Holy Spirit (terminology)
│   ├── to_be_near_unto_god.*             # To Be Near Unto God (terminology)
│   └── compendium.md                     # Computational theology reference
├── editions/
│   ├── Kuyper_Antirevolutionary_Politics_Vol1_FULL.md    # English Vol. 1
│   ├── Kuyper_Antirevolutionary_Politics_Vol2_FULL.md    # English Vol. 2
│   ├── Kuyper_Antirevolutionary_Politics_Vol1_Dutch.md   # Dutch Vol. 1 (MD)
│   ├── Kuyper_Antirevolutionary_Politics_Vol2_Dutch.md   # Dutch Vol. 2 (MD)
│   ├── Kuyper_Antirevolutionary_Politics_Vol3_Companion.md
│   ├── Antirevolutionary_Politics_Vol3_Master_Index.md
│   ├── Antirevolutionary_Politics_Vol3_Synopticon.md
│   ├── Antirevolutionary_Politics_Vol1.pdf               # Print-ready Vol. 1
│   ├── Antirevolutionary_Politics_Vol2.pdf               # Print-ready Vol. 2
│   ├── Antirevolutionary_Politics_Vol3_Master_Index.pdf
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
│   ├── generate_synopticon.py            # Syntopicon generation
│   ├── sync_scholarly_to_md.py           # Scholarly → Markdown sync
│   ├── analyze_pdf_alignment.py          # PDF alignment verification
│   ├── optimize_for_pod.sh               # Print-on-demand optimization
│   └── synopticon_data.json              # Syntopicon cross-reference data
├── manuscript/
│   └── volume_1/
│       └── chapter_01/
│           ├── dutch_source.md           # Original Dutch
│           ├── english_draft.md          # AI rough draft
│           └── english_refined.md        # Human-refined translation
├── reference/
│   ├── Faith - Abraham Kuyper.*          # Reference text
│   ├── Lectures on Calvinism.*           # Stone Lectures (ground truth)
│   ├── Saved by Grace Alone.*            # Reference text
│   └── The Sanctifying Work of the Hol.* # Reference text
├── prepend_md_rights.py                  # Rights/attribution front matter
├── LICENSE                               # Rights & attribution
└── README.md
```

---

## Translation Protocol

The translation follows a rigorous scholarly protocol (see `config/kuyper_translation_protocol.md`):

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
| Palingenesis | Regeneration | Social order "birth again" |

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

### Volume III: Companion & Master Index
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

### Generate Scholarly Master Edition
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

## Rights & Attribution

**Original Work:** *Antirevolutionaire Staatkunde* by Abraham Kuyper (1916–1917) — public domain.

**Translation & Scholarly Apparatus:** Copyright © 2026 Daniel Metcalf. All rights reserved.

This edition is provided for educational, research, and personal use. Attribution is required for any public citation or reuse. Commercial reproduction is strictly prohibited without express written permission.

**AI Disclosure:** This text was prepared with the assistance of advanced AI systems. The core text is a human-verified translation. AI was used for index synthesis, parallel text alignment, and scholarly apparatus generation.

---

## Background

Abraham Kuyper (1837–1920) was a Dutch statesman, theologian, journalist, and Prime Minister of the Netherlands (1901–1905). He founded the Free University of Amsterdam, the Anti-Revolutionary Party, and the Reformed Churches in the Netherlands. His political theology of **Sphere Sovereignty** remains influential in Christian democratic thought worldwide.

This translation project aims to restore the monumental scope of Kuyper's political theology for a modern English-speaking audience, making his granular, principled application of Neo-Calvinist thought accessible to contemporary scholars.
