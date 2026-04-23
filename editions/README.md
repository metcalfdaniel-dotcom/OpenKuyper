# Editions

This directory contains the final published editions of *Antirevolutionary Politics*.

## Generation

Editions are produced automatically by the three-tier pipeline:

```bash
python3 pipeline/three_tier_pipeline.py --pdf <source.pdf> --start <page> --end <page> --output editions/
```

The pipeline produces two formats for every page range:

- **CLEAN EDITION** (`*_CLEAN.md`) — Publication-ready English text only
- **CRITICAL EDITION** (`*_CRITICAL.md`) — English text with inline translator notes [like this] and adjudication rationale

## Current Editions

| Edition | Status | File |
|---------|--------|------|
| Volume 1, Foreword | In Progress | `foreword_CLEAN.md`, `foreword_CRITICAL.md` |
| Volume 1, Chapters 1–9 | Pending | — |
| Volume 2 | Pending | — |

## Archive

Old editions from previous pipelines (parallel, annotated, reading) are preserved in the private working repo:
`https://github.com/metcalfdaniel-dotcom/antirevolutionary-politics`
