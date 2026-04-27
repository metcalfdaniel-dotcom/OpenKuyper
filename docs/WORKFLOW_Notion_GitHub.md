# OpenKuyper Workflow: Notion → GitHub Handoff

## Canonical Source of Truth

| Stage | Canonical Location | Status |
|-------|-------------------|--------|
| **OCR cleanup** | Notion Translation Chunks DB | Active |
| **Initial translation** | Notion Translation Chunks DB | Active |
| **Terminology / Senses** | Notion Lexicon + Senses DBs | Active |
| **Stabilized chapters** | GitHub `manuscript/volume_1/` | Archive |
| **Termbase lockfile** | GitHub `termbase/kuyper_termbase.json` | Compiled from Notion |

## Notion Databases

| Database | ID | Purpose |
|----------|-----|---------|
| Translation Chunks | `bf39edf0-86e6-4f03-926b-30f3f4d7edac` | Bilingual drafts (NL + EN paragraphs) |
| Project Lexicon | `b675507f-bad8-4478-abeb-00745a893f65` | Canonical lemma list |
| Lexicon Senses | `353a9d93-dfa5-42e7-8688-cf13b04d9cf6` | Polyseme disambiguation |

## Workflow

```
OCR Scan → Notion (Translation Chunks)
    ↓
OCR Cleanup + Initial Translation (Notion)
    ↓
Terminology Review + Sense Locking (Notion Lexicon/Senses)
    ↓
Chapter Stabilized
    ↓
Export to GitHub manuscript/volume_1/ch{NN}-{slug}/
    ↓
Drift Detection + Final Termbase Compile
```

### Phase 1: Active Work (Notion)
- Dutch OCR text lives in Notion Translation Chunks
- English translation drafted alongside Dutch source
- Terminology auto-enriched via ODWN + Princeton WordNet
- Human reviews and locks senses in Lexicon Senses DB

### Phase 2: Stabilization (Notion → GitHub)
When a chapter is finalized:
1. Export Dutch source from Notion → `manuscript/volume_1/ch{NN}-{slug}/dutch_source.md`
2. Export English translation from Notion → `manuscript/volume_1/ch{NN}-{slug}/english_final.md`
3. Run `scripts/notion_worker.py --once` to compile latest termbase
4. Commit to GitHub with chapter tag

### Phase 3: Archive (GitHub)
- GitHub holds versioned, stabilized content only
- Drift detection runs against GitHub archives for cross-chapter consistency
- Termbase JSON is the compiled snapshot of all Locked/Approved senses

## Stale Drafts

Existing `english_draft.md` files in `manuscript/` are **archived snapshots**. They are marked with an HTML comment header. Do not edit them directly. The active drafts are in Notion.

## Export Command (when ready)

```bash
# Export a chapter from Notion to GitHub
PYTHONPATH=scripts python3 scripts/export_chapter.py \
  --chapter "Ch I" \
  --output manuscript/volume_1/ch01-introduction/
```

(Note: `export_chapter.py` is a placeholder — implement when first chapter stabilizes.)
