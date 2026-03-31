
import spacy
import re
import os
import json
from collections import Counter, defaultdict
import sys

# Add local path if needed, but we will run with the specific venv python
# Files
VOL1_MD = 'Definitive_Edition/Kuyper_Antirevolutionary_Politics_Vol1_FULL.md'
VOL2_MD = 'Definitive_Edition/Kuyper_Antirevolutionary_Politics_Vol2_FULL.md'
OUTPUT_JSON = 'Definitive_Edition/nlp_index_data.json'

def load_spacy_model():
    print("Loading Spacy model (en_core_web_sm)...")
    try:
        nlp = spacy.load("en_core_web_sm")
        # Increase max length for book parsing
        nlp.max_length = 2000000 
        return nlp
    except OSError:
        print("Error: en_core_web_sm model not found. Please run 'python -m spacy download en_core_web_sm'")
        sys.exit(1)

def clean_markdown(text):
    # Remove metadata
    text = re.sub(r'^---[\s\S]*?---', '', text)
    # Remove page markers
    text = re.sub(r'—- Page \d+ —-', '', text)
    # Remove markdown links/formatting
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text) 
    text = re.sub(r'[*_`#]', '', text)
    return text

def extract_entities(nlp, text, vol_label):
    print(f"Analyzing text for Volume {vol_label}...")
    doc = nlp(text)
    
    entities = defaultdict(list)
    
    # We want specific categories relevant to a political theology book
    relevant_types = ["PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW"]
    
    for ent in doc.ents:
        if ent.label_ in relevant_types:
            clean_text = ent.text.strip().replace('\n', ' ')
            if len(clean_text) > 2: # Filter noise
                entities[clean_text].append(ent.label_)
                
    return entities

def process_volume(nlp, filename, vol_label):
    with open(filename, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    # Split by pages to track page numbers? 
    # Spacy is contextual, splitting by page might break sentence boundary detection across pages.
    # Better strategy for an Index: 
    # 1. Parse whole text for entities.
    # 2. Then scan pages to find where those entities occur.
    
    # Let's extract valid entities first from the whole text to get a "Canonical List"
    clean_text = clean_markdown(raw_text)
    # Chunking to avoid memory issues if needed, but en_core_web_sm is light.
    # Actually, for 200k+ words, we should use nlp.pipe on chunks? 
    # Kuyper Vol 1 is ~400 pages, maybe 150k words. doc(text) might hit limit.
    # Limit is 1,000,000 chars default. Max length increased above.
    
    doc = nlp(clean_text)
    
    found_entities = Counter()
    entity_types = {}
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC", "WORK_OF_ART", "LAW", "EVENT"]:
            txt = ent.text.strip().replace('\n', ' ')
            if len(txt) > 3 and not re.match(r'^\d+$', txt): # Skip short/numeric
                found_entities[txt] += 1
                entity_types[txt] = ent.label_
                
    # Filter by frequency (at least 2 mentions to be significant?)
    significant_entities = {k: v for k, v in found_entities.items() if v >= 2}
    
    return significant_entities, entity_types

def map_entities_to_pages(entity_list, filename, vol_label):
    print(f"Mapping {len(entity_list)} entities to pages in {vol_label}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        
    page_map = defaultdict(set)
    
    # Regex split pages
    parts = re.split(r'—- Page (\d+) —-', content)
    # parts[0] is header
    # parts[1] is page num, parts[2] is text
    
    current_page = 0
    
    # Create simple regexes for entities? Or just string check?
    # String check is faster but Case Sensitive? Spacy was case sensitive.
    # We'll use the exact text Spacy found.
    
    for i in range(1, len(parts), 2):
        pg_num = int(parts[i])
        text = parts[i+1].lower() # Search in lower case to catch variations?
        
        for entity in entity_list:
            if entity.lower() in text:
                page_map[entity].add(pg_num)
                
    return page_map

def main():
    nlp = load_spacy_model()
    
    # 1. Discover Entities in Vol 1
    ents_v1, types_v1 = process_volume(nlp, VOL1_MD, "I")
    
    # 2. Discover Entities in Vol 2
    ents_v2, types_v2 = process_volume(nlp, VOL2_MD, "II")
    
    # 3. Merge Entity Lists
    all_entities = set(ents_v1.keys()) | set(ents_v2.keys())
    all_types = {**types_v1, **types_v2}
    
    print(f"Found {len(all_entities)} unique significant entities.")
    
    # 4. Map pages for ALL entities across BOTH volumes
    # (So if 'Abraham Kuyper' is found in Vol 1 only by Spacy, but appears in Vol 2, we catch it)
    
    map_v1 = map_entities_to_pages(all_entities, VOL1_MD, "Vol I")
    map_v2 = map_entities_to_pages(all_entities, VOL2_MD, "Vol II")
    
    # 5. Structure Data
    final_index = {}
    for entity in all_entities:
        final_index[entity] = {
            "type": all_types.get(entity, "UNKNOWN"),
            "vol_1_pages": sorted(list(map_v1.get(entity, []))),
            "vol_2_pages": sorted(list(map_v2.get(entity, [])))
        }
        
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_index, f, indent=2)
        
    print(f"Saved enhanced index data to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
