
import re
import json
import os

# Import ADLER_BRIDGE from local data
from scholarly_data_expansion import ADLER_BRIDGE

# Files
VOL1_MD = 'Kuyper_Antirevolutionary_Politics_Vol1_FULL.md'
VOL2_MD = 'Kuyper_Antirevolutionary_Politics_Vol2_FULL.md'
OUTPUT_JSON = 'synopticon_data.json'

def scan_text_for_ideas(file_path, vol_label):
    print(f"Scanning {vol_label} for Synopticon...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by pages
    parts = re.split(r'—- Page (\d+) —-', content)
    
    # We will store: Idea -> list of { "vol":, "page":, "excerpt": }
    # To avoid massive output, we might limit to 1 per page per idea, or 5 max per idea/volume.
    # User said "fill it out with content", so let's be generous but not infinite.
    # Max 10 excerpts per Idea per Volume? 
    # Or prioritise contexts where MULTIPLE keywords appear?
    
    hits = {}
    
    # Build regexes for efficiency
    idea_regexes = {}
    for idea, terms in ADLER_BRIDGE.items():
        # terms are list of strings. Create regex \b(term1|term2)\b
        # escape terms
        esc_terms = [re.escape(t) for t in terms]
        pattern = re.compile(r'\b(' + '|'.join(esc_terms) + r')\b', re.IGNORECASE)
        idea_regexes[idea] = pattern
        hits[idea] = []

    current_page = 0
    
    # iterate pages
    for i in range(1, len(parts), 2):
        pg_num = int(parts[i])
        text = parts[i+1] # The page content
        
        # Split page into sentences (rough approximation)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sent in sentences:
            sent_clean = sent.strip().replace('\n', ' ')
            if len(sent_clean) < 20: continue # Skip fragments
            
            for idea, pattern in idea_regexes.items():
                match = pattern.search(sent_clean)
                if match:
                    # Found a hit!
                    # Add to hits if not already too many for this page/idea combo
                    # Or just add all and filter later.
                    
                    term_found = match.group(1)
                    
                    # Highlight the term in the excerpt?
                    excerpt = sent_clean.replace(term_found, f'<strong>{term_found}</strong>')
                    
                    hits[idea].append({
                        "vol": vol_label,
                        "page": pg_num,
                        "excerpt": excerpt,
                        "term": term_found
                    })
                    
    return hits

def main():
    hits_v1 = scan_text_for_ideas(VOL1_MD, "Vol I")
    hits_v2 = scan_text_for_ideas(VOL2_MD, "Vol II")
    
    # Merge
    full_synopticon = {}
    
    for idea in ADLER_BRIDGE.keys():
        all_hits = hits_v1.get(idea, []) + hits_v2.get(idea, [])
        if not all_hits: continue
        
        # Filter: Select the "best" hits? 
        # Criteria: Length? Presence of multiple keywords? 
        # For now, let's take up to 8 from Vol I and 8 from Vol II distinct pages?
        # User wants "comprehensive" but readable.
        # Let's keep a max of 20 top occurrences to avoid flooding.
        
        # Sort by page order
        # (Vol I before Vol II is implicit by concatenation)
        
        # Dedup: If same sentence, skip.
        unique_hits = []
        seen = set()
        for h in all_hits:
            key = (h['vol'], h['page'], h['excerpt'][:30]) # dedup sig
            if key not in seen:
                unique_hits.append(h)
                seen.add(key)
        
        # Limit total to prevent 500 page Synopticon?
        # Maybe 15-20 citations per Idea is a good "Synopticon" style.
        # Adler's Syntopicon is huge, so maybe density is good.
        # Let's Limit to 30.
        
        full_synopticon[idea] = unique_hits[:30]
        
    # Write to JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(full_synopticon, f, indent=2)
        
    print(f"Generated Synopticon Data: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
