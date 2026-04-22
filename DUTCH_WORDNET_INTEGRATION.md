# Dutch WordNet Integration

## Overview

The OpenKuyper project integrates the **Open Dutch Wordnet (ODWN)** to provide algorithmic semantic disambiguation, synonym discovery, and domain tagging for our Dutch-to-English translation pipeline.

This addresses a critical challenge in translating Kuyper: many 1916 Dutch theological and political terms carry semantic nuances that are not captured by simple bilingual dictionaries. WordNet provides **cognitive synonym sets (synsets)** that map Dutch terms to their conceptual meanings, enabling more precise English rendering.

## Sources

- **R Wrapper:** https://github.com/weRbelgium/wordnet.dutch
- **Original Data:** https://github.com/MartenPostma/OpenDutchWordnet
- **Data File:** `odwn_orbn_gwg-LMF_1.3.xml.gz` (LMF format)
- **License:** CC BY-SA 4.0 (applies to WordNet data)

## Setup

### 1. Download the Data

```bash
mkdir -p reference/odwn
cd reference/odwn
wget https://github.com/MartenPostma/OpenDutchWordnet/raw/master/resources/odwn/odwn_orbn_gwg-LMF_1.3.xml.gz
gunzip odwn_orbn_gwg-LMF_1.3.xml.gz
```

### 2. Install Python Dependencies

No external dependencies beyond Python's standard library (`xml.etree.ElementTree`).

## How It Supports Translation

### 1. Semantic Disambiguation

When Kuyper uses a term like **"staat"** (state), it could mean:
- The political state/government
- A condition or state of being
- The estate or status of a person

WordNet provides separate synsets with glosses (definitions) that help identify which sense is operative in a given context.

**Example:**
```python
from tools.dutch_wordnet import DutchWordNet

dwn = DutchWordNet("reference/odwn/odwn_orbn_gwg-LMF_1.3.xml")
senses = dwn.suggest_translation_senses("staat")

# Returns multiple senses with:
# - Dutch gloss (definition)
# - Part of speech
# - Domain tags (political, theological, etc.)
# - ILI (Inter-Lingual Index mapping to Princeton WordNet)
```

### 2. Synonym Discovery

WordNet groups near-synonyms into synsets. This helps translators understand the semantic field Kuyper is drawing from.

**Example:**
```python
field = dwn.get_semantic_field("genade")  # grace
print(field["synonyms"])
# Might reveal related terms like: "barmhartigheid", "welwillendheid"
```

### 3. Domain and Register Tagging

ODWN includes pragmatics domains that identify whether a term belongs to:
- Religious/theological registers
- Political/legal registers
- Formal vs. informal registers
- Archaic vs. modern usage

This is critical for Kuyper, whose vocabulary spans formal political theory, classical theology, and 19th-century elevated prose.

### 4. Cross-Lingual Alignment (ILI)

Each Dutch synset has an **Inter-Lingual Index (ILI)** that maps to Princeton WordNet. This provides a bridge to English conceptual equivalents.

**Workflow:**
1. Identify Dutch term in context
2. Look up synset in ODWN
3. Retrieve ILI code
4. Query Princeton WordNet for English synset members
5. Select English equivalent that matches Kuyper's register and domain

## Integration in the Translation Pipeline

### Pre-Translation Phase

Before translating a chapter, run the semantic analyzer:

```bash
python pipeline/semantic_analysis.py \
  --input manuscript/dutch/chapter_01.md \
  --output review/semantic_map_ch01.json
```

This produces a JSON file mapping each significant Dutch term to:
- Its synset IDs
- Domain tags
- Suggested English senses
- Confidence scores

### During Translation

Translators can query the WordNet interface to resolve ambiguities:

```python
# In translation notebook or script
from tools.dutch_wordnet import DutchWordNet

dwn = DutchWordNet("reference/odwn/odwn_orbn_gwg-LMF_1.3.xml")

# Resolve ambiguous term
context = "De soevereiniteit in eigen kring"
senses = dwn.suggest_translation_senses("soevereiniteit")

# Filter by domain
political_senses = [s for s in senses if "politics" in s["domains"]]
```

### Quality Assurance

After translation, verify that English terms map back to the correct Dutch semantic fields:

```python
# Check that "sovereignty" maps to the same conceptual space
# as Kuyper's "soevereiniteit"
dutch_field = dwn.get_semantic_field("soevereiniteit")
english_equivalent = dwn.get_semantic_field("soevereiniteit")  # via ILI lookup
```

## Key Features of the Python Interface

### `DutchWordNet.lookup(term)`
Returns all lexical entries for a lemma with their senses, definitions, and domains.

### `DutchWordNet.get_synset(synset_id)`
Retrieves a synset with its gloss, relations, and member lemmas.

### `DutchWordNet.get_semantic_field(term, depth=1)`
Builds a semantic field including synonyms, hypernyms (broader terms), and hyponyms (narrower terms).

### `DutchWordNet.get_domains(term)`
Returns domain tags (e.g., "religion", "politics", "law", "philosophy").

### `DutchWordNet.get_ili_mapping(term)`
Returns Princeton WordNet ILI codes for cross-lingual alignment.

### `DutchWordNet.suggest_translation_senses(term)`
High-level method returning candidate English translation senses with glosses, domains, and semantic summaries.

## Theological Term Enhancements

The base ODWN covers general Dutch vocabulary well but may lack specialized 1916 theological terminology. We supplement it with:

1. **Custom Synset Extensions:** Adding Kuyper-specific synsets for terms like:
   - "anti-revolutionair" (anti-revolutionary)
   - "gemeene gratie" (common grace)
   - "sfeer" (sphere, in the technical Kuyperian sense)
   - "levenssysteem" (life-system/worldview)

2. **Domain Taxonomy Extension:** Adding theological domains:
   - `theology.reformed`
   - `theology.soteriology`
   - `political_theory.sphere_sovereignty`
   - `philosophy.calvinism`

3. **Historical Register Tags:** Marking terms as:
   - `register.archaic_1916`
   - `register.elevated_political`
   - `register.classical_theological`

## Citation

When using the Open Dutch Wordnet in published research or translations:

```
Marten Postma, Ruben Izquierdo Bevia, and Pick Vossen (2013).
Open Dutch WordNet.
In Proceedings of the Global WordNet Conference (GWC-2013).
```

## License Note

The ODWN data is licensed under CC BY-SA 4.0. Our Python wrapper and integration code is MIT licensed. When redistributing the data, ensure compliance with the CC BY-SA 4.0 terms.
