
import os
import re
import json
from collections import defaultdict
# Import the expanded data
try:
    # Need to import the new dictionaries: ENCYCLOPEDIC_CONCEPTS, BIOGRAPHICAL_REGISTER
    from scholarly_data_expansion import ANNOTATIONS as EXPANDED_ANNOTATIONS, ADLER_BRIDGE, EXPANDED_AUTHORS, EXPANDED_CONCEPTS, NEW_ANNOTATIONS, AI_DISCLOSURE, PREFACE_DRAFT, DISCOVERY_CLUSTERS, BOOKS_OF_BIBLE, ENCYCLOPEDIC_CONCEPTS, BIOGRAPHICAL_REGISTER
    
    ANNOTATIONS = EXPANDED_ANNOTATIONS
    CONCEPTS = list(set(EXPANDED_CONCEPTS))
    AUTHORS = list(set(EXPANDED_AUTHORS))
except ImportError as e:
    print(f"WARNING: Could not import expansion module: {e}")
    # Defaults
    ANNOTATIONS = {}
    ADLER_BRIDGE = {}
    CONCEPTS = []
    AUTHORS = []
    DISCOVERY_CLUSTERS = {}
    AI_DISCLOSURE = ""
    PREFACE_DRAFT = ""
    BOOKS_OF_BIBLE = "Gen|Ex"
    ENCYCLOPEDIC_CONCEPTS = {}
    BIOGRAPHICAL_REGISTER = {}

def clean_text_segment(text):
    # Strip YAML frontmatter (only at start of file)
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL, count=1)
    # Remove old preface - must be very specific to avoid removing content!
    # Only remove if it appears in first 500 chars
    if text[:500].find('# Translator') >= 0:
        text = re.sub(r'^.*?# Volume [IVX]+:', '# Volume', text, flags=re.DOTALL, count=1)
    
    text = re.sub(r'Digitized by.*?\n', '', text)
    text = re.sub(r'W\. ten HAVEL.*?\n', '', text)
    text = re.sub(r'\n(Antirevolutionary|ANTIREVOLUTIONARY)\s+POLITICS\n', '\n', text)
    text = re.sub(r'\n(KUYPER’S|KUYPER)\s+Antirevolutionary\s+POLITICS\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def parse_analytical_register(raw_content):
    summaries = {} 
    # Limit search to the end of the file where the register is located
    # This prevents matching "Analytical Register" mentions in the preface
    search_start_pos = max(0, len(raw_content) - 50000)
    search_area = raw_content[search_start_pos:]
    
    register_start = re.search(r'REGISTER', search_area, re.IGNORECASE)
    if not register_start:
        return {}
    register_text = search_area[register_start.start():]
    current_ch = None
    current_sec = None
    lines = register_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        ch_match = re.search(r'CHAPTER\s+([IVXLCDM]+)\.?\s*(.*)', line, re.IGNORECASE)
        if ch_match:
            current_ch = ch_match.group(1)
            continue
        sec_match = re.search(r'§\s*(\d+)\.', line)
        if sec_match:
            current_sec = sec_match.group(1)
            summary = line[sec_match.end():].strip()
            if current_ch and current_sec:
                summaries[(current_ch, current_sec)] = summary
    return summaries

def create_scholarly_edition(md_file, output_html, vol_title, vol_num, translator, start_chap=None, end_chap=None, paged_js=True):
    print(f"📖 Generating Annotated Edition for {vol_title} ({'All' if start_chap is None else f'Ch {start_chap}-{end_chap}'})...")
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    register_map = parse_analytical_register(content)
    
    scripture_index = defaultdict(set)
    great_ideas_index = defaultdict(set)
    general_index = defaultdict(set)
    formatted_paras = []
    
    page_marker_pat = re.compile(r'—- Page (\d+) —-')
    section_marker_pat = re.compile(r'^§\s*(\d+)\.\s*(.*)')
    bible_pat = re.compile(rf'\b({BOOKS_OF_BIBLE})\s+(\d+:\d+(?:–\d+)?)\b')
    
    content = clean_text_segment(content)
    lines = content.split('\n')
    toc_data = [] 
    current_page = 0
    current_sec_num = 0
    
    # Track if we are in the desired chapter range
    in_range = True if start_chap is None else False
    chap_count = 0
    current_ch_num = None

    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        
        pg_match = page_marker_pat.search(line)
        if pg_match:
            current_page = int(pg_match.group(1))
            if in_range:
                anchor = f'<span id="vol{vol_num}_p{current_page}" class="page-marker" data-page="{current_page}">[{current_page}]</span>'
                formatted_paras.append(f'<div class="page-break-container">{anchor}</div>')
            continue
            
        sec_match = section_marker_pat.match(line)
        if sec_match:
            s_num = sec_match.group(1)
            full_text = sec_match.group(2)
            current_sec_num = int(s_num)
            sec_id = f"sec_{s_num}"
            
            # Split title from text
            # Title is usually the first sentence or up to 80 chars
            title = ""
            remaining_text = ""
            
            # Identify a likely title end (dot followed by space or end of line)
            dot_match = re.search(r'\.\s+', full_text)
            if dot_match and dot_match.start() < 80:
                pos = dot_match.start() + 1
                title = full_text[:pos].strip()
                remaining_text = full_text[pos:].strip()
            elif len(full_text) < 80:
                title = full_text.strip()
                remaining_text = ""
            else:
                # No clear title split, use first 60 chars
                title = full_text[:60].strip() + "..."
                remaining_text = full_text.strip()

            if in_range:
                headnote_html = ""
                summary_text = ""
                if current_ch_num and (current_ch_num, s_num) in register_map:
                    summary_text = register_map[(current_ch_num, s_num)]
                
                if summary_text:
                    headnote_html = f'<div class="analytical-headnote"><strong>Analytical Summary:</strong> {summary_text}</div>'
                
                formatted_paras.append(f'<h3 id="{sec_id}">§{s_num}. {title}</h3>{headnote_html}')
                toc_data.append({"type": "section", "id": sec_id, "title": f"§{s_num} {title}", "page": current_page})
            
            if not remaining_text:
                continue
            else:
                line = remaining_text # Let fall through to standard para processing

        chapter_match = re.search(r'^(?:CHAPTER|Chapter)\s+([IVXLCDM]+)\.?\s*(.*)', line, re.IGNORECASE)
        if chapter_match:
            chap_count += 1
            current_ch_num = chapter_match.group(1).upper()
            c_title = chapter_match.group(2).strip()
            
            if start_chap is not None:
                if chap_count >= start_chap and (end_chap is None or chap_count <= end_chap):
                    in_range = True
                else:
                    in_range = False

            if not c_title and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('§') and not page_marker_pat.search(next_line):
                    c_title = next_line
            
            c_id = f"chap_{current_ch_num}"
            if in_range:
                formatted_paras.append(f'<h2 id="{c_id}">CHAPTER {current_ch_num}<br><span style="font-size:0.8em">{c_title}</span></h2>')
                toc_data.append({"type": "chapter", "id": c_id, "title": f"CHAPTER {current_ch_num}: {c_title}", "page": current_page})
            continue

        if not in_range:
            continue

        # --- Standard Paragraph Processing (In Range) ---
        
        # Scripture Indexing
        def tag_bible(m):
            ref = m.group(0)
            scripture_index[ref].add((f"Vol {vol_num}", current_page))
            return f'<a href="#idx_bible_{current_page}" class="scripture-ref">{ref}</a>'
        line = bible_pat.sub(tag_bible, line)

        # Indexing Logic
        line_lower = line.lower()
        found_in_line = set()
        for author in AUTHORS:
            if author in line and author not in found_in_line:
                general_index[author].add(current_page)
                found_in_line.add(author)
        for concept in CONCEPTS:
            if concept in line and concept not in found_in_line:
                general_index[concept].add(current_page)
                found_in_line.add(concept)
        
        for cluster_name, keywords in DISCOVERY_CLUSTERS.items():
            for kw in keywords:
                if kw in line_lower:
                    general_index[cluster_name].add(current_page)
                    break
        
        for idea, terms in ADLER_BRIDGE.items():
            for term in terms:
                if re.search(rf'\b{re.escape(term)}\b', line_lower):
                    great_ideas_index[idea].add(current_page)
                    break 

        # Cross References
        def link_replacer(m):
            full_ref = m.group(0)
            if "Vol II" in full_ref or "Vol. II" in full_ref:
                p_m = re.search(r'\d+', full_ref.split('p.')[-1])
                if p_m: return f'<a href="Antirevolutionary_Politics_Vol2_Part1.html#volII_p{p_m.group(0)}" class="cross-reference">{full_ref}</a>'
            return full_ref
        line = re.sub(r'\(Vol\.?\s*[IVX]+,?\s*p\.\s*\d+\)', link_replacer, line)

        if line.startswith('> '):
            formatted_paras.append(f'<blockquote>{line[2:]}</blockquote>')
        else:
            formatted_paras.append(f'<p>{line}</p>')

    # --- INTEGRATE NLP INDEX DATA ---
    try:
        import json
        nlp_path = 'nlp_index_data.json'
        if os.path.exists(nlp_path):
            with open(nlp_path, 'r', encoding='utf-8') as f:
                nlp_data = json.load(f)
            
            for term, data in nlp_data.items():
                pages_to_add = []
                if vol_num == 'I' or vol_num == 1:
                    pages_to_add = data.get('vol_1_pages', [])
                elif vol_num == 'II' or vol_num == 2:
                    pages_to_add = data.get('vol_2_pages', [])
                
                if pages_to_add:
                    for p in pages_to_add:
                        general_index[term].add(p)
    except Exception as e:
        print(f"   (Warning: Could not merge NLP data: {e})")

    generate_html_file(output_html, vol_title, vol_num, translator, formatted_paras, toc_data, 
                       general_index, great_ideas_index, scripture_index, 
                       use_paged_js=paged_js)
    
    return {
        "general": general_index,
        "great_ideas": great_ideas_index,
        "scripture": scripture_index
    }

def generate_html_file(filename, title, vol_label, translator, content_paras, toc_data, general_idx, ideas_idx, bible_idx, is_master=False, use_paged_js=True):
    paged_script = '<script src="paged.polyfill.js"></script>' if use_paged_js else ''
    hud_html = ""
    if use_paged_js:
        hud_html = """
    <div id="render-hud">⏳ INITIALIZING BOOK ENGINE (PLEASE WAIT)...</div>
    <script>
        window.PagedConfig = {
            auto: true,
            after: (flow) => {
                document.body.classList.add("pagedjs_done");
                const hud = document.getElementById("render-hud");
                if (hud) {
                    hud.innerHTML = "✅ DOCUMENT COMPLETE: READY FOR PDF EXPORT (" + document.querySelectorAll('.pagedjs_page').length + " pages)";
                    hud.style.background = "#2e7d32";
                }
            }
        };
        const observer = new MutationObserver((mutations) => {
            const pages = document.querySelectorAll('.pagedjs_page').length;
            const hud = document.getElementById("render-hud");
            if (hud && !document.body.classList.contains("pagedjs_done")) {
                hud.innerHTML = "⏳ RENDERING BOOK LAYOUT: " + pages + " pages processed...";
            }
        });
        observer.observe(document.documentElement, { childList: true, subtree: true });
    </script>
    <style>
        #render-hud { position: fixed; top:0; left:0; right:0; background: #8b2222; color: white; text-align: center; padding: 10px; font-family: 'Outfit'; font-weight: bold; z-index: 99999; font-size: 14pt; }
        @media print { #render-hud { display: none !important; } }
    </style>
"""
    
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=Outfit:wght@300;600&display=swap');
    
    @page {
        size: 7in 10in;
        margin-top: 1in;
        margin-bottom: 1in;
        margin-inside: 1.25in; /* Gutter margin */
        margin-outside: 0.85in;
    }

    @page :left {
        @top-left { content: counter(page); font-family: 'Crimson Pro'; font-size: 10pt; }
        @top-center { content: "Antirevolutionary Politics | """ + str(vol_label) + """"; font-family: 'Outfit'; font-size: 8pt; text-transform: uppercase; letter-spacing: 1px; color: #666; }
    }

    @page :right {
        @top-right { content: counter(page); font-family: 'Crimson Pro'; font-size: 10pt; }
        @top-center { content: string(chapter-title); font-family: 'Outfit'; font-size: 8pt; text-transform: uppercase; letter-spacing: 1px; color: #666; }
    }
    
    /* Chapter titles set the running header variable */
    h2 { 
        string-set: chapter-title content(); 
        font-family: 'Outfit'; font-size: 18pt; border-bottom: 2px solid #333; margin-top: 30px; 
        page-break-before: always;
        prince-bookmark-level: 1;
        text-align: left; /* Fix justification issue */
    }
    
    body { 
        font-family: 'Crimson Pro', serif; 
        font-size: 11.5pt; 
        line-height: 1.45; 
        text-align: left; 
    }
    
    h1 { font-family: 'Outfit'; font-size: 32pt; text-align: center; text-transform: uppercase; page-break-before: always; }
    h3 { font-family: 'Outfit'; font-size: 14pt; margin-top: 25px; break-after: avoid; text-align: left; }
    
    .index-section { page-break-before: always; font-size: 9pt; font-family: 'Outfit'; text-align: left; }
    .index-entry { break-inside: avoid; margin-bottom: 4px; }
    .index-term { font-weight: 600; }
    
    .glossary-section { page-break-before: always; }
    .encyclo-entry { margin-bottom: 30px; break-inside: avoid; }
    .encyclo-term { display: block; font-family: 'Outfit', sans-serif; font-size: 14pt; font-weight: 600; color: #8b2222; border-bottom: 1px solid #ddd; margin-bottom: 8px; padding-bottom: 4px; break-after: avoid; text-align: left; }
    .encyclo-body { font-size: 11pt; line-height: 1.6; color: #333; text-align: left; }
    
    .preface-container, .technical-note { margin-bottom: 40px; page-break-inside: avoid; text-align: left; }
    
    blockquote { margin: 1em 2em; padding-left: 1em; border-left: 3px solid #ccc; font-style: italic; background: #fafafa; break-inside: avoid; text-align: left; }
    .analytical-headnote { background: #fdfbf7; border: 1px solid #e0d8c8; padding: 10px; margin-bottom: 15px; font-size: 10pt; font-family: 'Outfit'; break-inside: avoid; text-align: left; }
    
    .toc-root { list-style-type: none; padding-left: 0; }
    .toc-chapter { margin-top: 15px; font-weight: 600; font-family: 'Outfit', sans-serif; text-align: left; }
    .toc-chapter ul { list-style-type: none; padding-left: 20px; font-weight: normal; margin-top: 5px; }
    .toc-section { margin-bottom: 5px; font-family: 'Crimson Pro', serif; text-align: left; }
    .toc a { text-decoration: none; color: #333; border-bottom: none; }
    .toc a:hover { color: #8b2222; }

    .synopticon-list { font-size: 10.5pt; margin-left: 15px; text-align: left; }
    .syn-item { margin-bottom: 6px; }
    .syn-ref { font-weight: bold; color: #555; font-size: 0.9em; }
    .syn-text { font-style: italic; color: #333; }

    .synthesis-essay {
        background: #fcfcfc;
        border-left: 4px solid #8b2222;
        padding: 15px;
        margin: 10px 0 15px 15px;
        font-family: 'Crimson Pro', serif;
        font-size: 11pt;
        color: #222;
        text-align: left;
    }
    .synthesis-essay h4 {
        margin-top: 0;
        font-family: 'Outfit', sans-serif;
        color: #8b2222;
        text-transform: uppercase;
        font-size: 0.9em;
        letter-spacing: 1px;
    }
    .syn-refs {
        margin-left: 15px;
        font-size: 0.95em;
        color: #444;
        margin-top: 5px;
        text-align: left;
    }
    """
    
    # Specific Front Matter logic
    volume_specific_preface = ""
    vol_str = str(vol_label).strip()

    if is_master:
        # Volume III
        volume_specific_preface = PREFACE_DRAFT 
        # Ideally the specific Vol 3 one, but we use PREFACE_DRAFT which covers general scope.
    elif vol_str == 'I' or vol_str == '1':
        # Volume I gets the full preface
        volume_specific_preface = PREFACE_DRAFT
    elif vol_str == 'II' or vol_str == '2':
        # Shorter preface for Vol II
        volume_specific_preface = """<div class="preface-container"><h2>Preface to Volume II</h2><p>This second volume, titled <em>The Application</em>, moves from the theoretical foundations laid in Volume I to the concrete political program. Here Kuyper addresses the practical machinery of the State: Representation, Justice, Army, and Social Policy.</p></div>"""

    toc_html = ""
    if toc_data:
        toc_items = ""
        # Skeleton TOC: Only Chapters
        for item in toc_data:
            if item.get("type") == "chapter":
                link = f'<a href="#{item["id"]}"><span>{item["title"]}</span></a>'
                toc_items += f'<li class="toc-chapter">{link}</li>'
        # Add Index sections to TOC
        toc_items += '<li class="toc-chapter" style="margin-top: 15px; border-top: 1px solid #ccc; padding-top: 10px;"><a href="#general-index"><span>General Index</span></a></li>'
        toc_items += '<li class="toc-chapter"><a href="#great-ideas-index"><span>Great Ideas Index (Syntopicon)</span></a></li>'
        toc_items += '<li class="toc-chapter"><a href="#scripture-index"><span>Scripture Index</span></a></li>'
        toc_html = f'<div class="toc"><h2>Table of Contents</h2><ul class="toc-root">{toc_items}</ul></div>'

    def format_idx(idx_data, title, section_id=None):
        if not idx_data: return ""
        id_attr = f' id="{section_id}"' if section_id else ''
        html = f'<div class="index-section"{id_attr}><h2>{title}</h2>'
        for term in sorted(idx_data.keys()):
            pages = sorted(list(idx_data[term]))
            pg_str = ", ".join([str(p) for p in pages])
            html += f'<div class="index-entry"><span class="index-term">{term}</span> <span class="index-pages">{pg_str}</span></div>'
        html += '</div>'
        return html

    def format_master_idx(idx_data, title):
        html = f'<div class="index-section"><h2>{title}</h2>'
        for term in sorted(idx_data.keys()):
            refs = sorted(list(idx_data[term]), key=lambda x: (x[0], x[1]))
            ref_str = ", ".join([f"{v}: {p}" for v, p in refs])
            html += f'<div class="index-entry"><span class="index-term">{term}</span> <span class="index-pages">{ref_str}</span></div>'
        html += '</div>'
        return html

    # Encyclopedic Formatter for Vol III
    def format_encyclopedia(data_dict, title):
        if not data_dict: return ""
        html = f'<div class="glossary-section"><h2>{title}</h2>'
        for term, body in data_dict.items():
            html += f'<div class="encyclo-entry"><span class="encyclo-term">{term}</span><div class="encyclo-body">{body}</div></div>'
        html += '</div>'
        return html
    
    # Removed nested format_synopticon - using global version instead

    final_output = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{title}</title><style>{css}</style>
    {paged_script}
</head><body>
    {hud_html}
    <div class="container">
        <div class="title-page">
            <h1>{title}</h1>
            <div style="text-align:center; margin-top:20px; font-weight:bold; font-size:14pt;">{vol_label}</div>
            <div style="text-align:center; margin-top:50px; font-style:italic;">{translator}</div>
        </div>
        
        {volume_specific_preface}
        {AI_DISCLOSURE}
        
        {toc_html}
        
        <div class="content">
            {"".join(content_paras)}
        </div>
    """
    
    # Removed duplicate nested format_synopticon



    
    if is_master:
        # Generate TOC
        toc_html = """
        <div class="toc-container" style="background: #f9f9f9; padding: 20px; border-bottom: 2px solid #ddd; margin-bottom: 30px;">
            <h2 style="margin-top:0;">Table of Contents</h2>
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="margin-bottom: 8px;"><a href="#part-1" style="text-decoration: none; color: #8b2222; font-weight: bold;">Part I: Encyclopedic Glossary of Neo-Calvinist Concepts</a></li>
                <li style="margin-bottom: 8px;"><a href="#part-2" style="text-decoration: none; color: #8b2222; font-weight: bold;">Part II: Biographical Register of Key Figures</a></li>
                <li style="margin-bottom: 8px;"><a href="#part-3" style="text-decoration: none; color: #8b2222; font-weight: bold;">Part III: Master General Index (Vol I & II)</a></li>
                <li style="margin-bottom: 8px;"><a href="#part-4" style="text-decoration: none; color: #8b2222; font-weight: bold;">Part IV: The Synopticon (Great Ideas)</a></li>
                <li style="margin-bottom: 8px;"><a href="#part-5" style="text-decoration: none; color: #8b2222; font-weight: bold;">Part V: Master Scripture Index</a></li>
            </ul>
        </div>
        """
        final_output += toc_html
        
        # VOLUME III CONTENT
        final_output += '<div id="part-1"></div>'
        final_output += format_encyclopedia(ENCYCLOPEDIC_CONCEPTS, "Part I: Encyclopedic Glossary of Neo-Calvinist Concepts")
        
        final_output += '<div id="part-2"></div>'
        final_output += format_encyclopedia(BIOGRAPHICAL_REGISTER, "Part II: Biographical Register of Key Figures")
        
        final_output += '<div style="page-break-before:always;"></div>'
        
        final_output += '<div id="part-3"></div>'
        final_output += format_master_idx(general_idx, "Part III: Master General Index (Vol I & II)")
        # Use new Synopticon formatter
        final_output += '<div id="part-4"></div>'
        final_output += format_synopticon(ideas_idx, "Part IV: The Synopticon (Great Ideas)")
        
        final_output += '<div id="part-5"></div>'
        final_output += format_master_idx(bible_idx, "Part V: Master Scripture Index")
    else:
        # Standard Volumes
        final_output += format_idx(general_idx, "General Index", "general-index")
        final_output += format_idx(ideas_idx, "Great Ideas Index (Syntopicon)", "great-ideas-index")
        final_output += format_idx(bible_idx, "Scripture Index", "scripture-index")

    final_output += "</body></html>"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(final_output)
    print(f"✅ Generated: {filename}")

# Synopticon Formatter - GLOBAL SCOPE
def format_synopticon(idx_data, title):
    import json
    syn_path = 'synopticon_data.json'
    syn_data = {}
    if os.path.exists(syn_path):
        with open(syn_path, 'r', encoding='utf-8') as f:
            syn_data = json.load(f)

    # Load Synthesis Essays from external JSON
    essays_path = 'synthesis_essays.json'
    SYNTHESIS_ESSAYS = {}
    try:
        if os.path.exists(essays_path):
            with open(essays_path, 'r', encoding='utf-8') as f:
                SYNTHESIS_ESSAYS = json.load(f)
        else:
             print(f"Warning: {essays_path} not found.")
    except Exception as e:
        print(f"Error loading synthesis essays: {e}")

    
    html = f'<div class="glossary-section"><h1>{title}</h1><p class="intro-text">This Synopticon maps the 102 Great Ideas of the Western World (Adler) to the text of <em>Antirevolutionary Politics</em>. For key concepts, a synthesis of Kuyper\'s thought is provided.</p>'
    
    # Use keys from the dynamic index (Vol I + II) AND static data
    all_keys = sorted(list(set(list(idx_data.keys()) + list(syn_data.keys()))))
    
    # Sort keys to put our demos first for the user to see, then the rest
    demo_keys = ["STATE", "RELIGION", "LIBERTY"]
    other_keys = [k for k in all_keys if k not in demo_keys]
    sorted_keys = demo_keys + other_keys
    
    for idea in sorted_keys:
          # Skip if no data in idx_data (the merged Vol I+II index)
          if idea not in idx_data: continue

          html += f'<div class="encyclo-entry"><span class="encyclo-term">{idea}</span>'
          
          # Insert Essay if available
          if idea in SYNTHESIS_ESSAYS:
              html += SYNTHESIS_ESSAYS[idea]
          
          html += '<div class="synopticon-list">'
          
          # Reference List from Dynamic Index (Vol I & II) - NO TEXT QUOTATIONS
          # Group by Volume
          vol_refs = defaultdict(list)
          # idx_data[idea] is a set of (Vol, Page) tuples
          for (vol, pg) in idx_data[idea]:
              vol_refs[vol].append(str(pg))
        
          # Create a concise reference string: "Vol I: 12, 15, 100; Vol II: 4, 20"
          ref_strings = []
          for vol in sorted(vol_refs.keys()):
              unique_pages = sorted(list(set(vol_refs[vol])), key=lambda x: int(x) if x.isdigit() else 0)
              ref_strings.append(f"<strong>{vol}</strong>: {', '.join(unique_pages)}")
          
          html += f'<div class="syn-refs"><em>References:</em> {"; ".join(ref_strings)}</div>'
             
          html += '</div></div>'
    html += '</div>'
    return html

def create_master_volume_iii(v1_data, v2_data, translator):
    print("📖 Generating Volume III: Companion & Master Index...")
    
    def merge_indices(d1, d2, label1="I", label2="II"):
        merged = defaultdict(set)
        for term, pages in d1.items():
            for p in pages: merged[term].add((label1, p))
        for term, pages in d2.items():
            for p in pages: merged[term].add((label2, p))
        return merged

    master_gen = merge_indices(v1_data['general'], v2_data['general'])
    master_ideas = merge_indices(v1_data['great_ideas'], v2_data['great_ideas'])
    master_bible = merge_indices(v1_data['scripture'], v2_data['scripture'])
    
    # Ensure output directory exists
    os.makedirs('01_Editions', exist_ok=True)
    
    generate_html_file(
        "01_Editions/Antirevolutionary_Politics_Vol3_Master_Index.html",
        "Antirevolutionary Politics",
        "VOLUME III: COMPANION & MASTER INDEX",
        translator,
        [], 
        [], 
        master_gen, master_ideas, master_bible,
        is_master=True
    )
    
    # --- MARKDOWN EXPORT FOR VOL III ---
    print("   (Generating Full Markdown Master Index...)")
    md_output = "# VOLUME III: COMPANION & MASTER INDEX\n\n"
    md_output += "> Editor: Daniel Metcalf\n\n"
    
    # TOC FOR MARKDOWN
    md_output += "## Table of Contents\n"
    md_output += "- [Part I: Encyclopedic Glossary](#part-i-encyclopedic-glossary-of-neo-calvinist-concepts)\n"
    md_output += "- [Part II: Biographical Register](#part-ii-biographical-register)\n"
    md_output += "- [Part III: Master General Index](#part-iii-master-general-index)\n"
    md_output += "- [Part IV: Synopticon](#part-iv-the-synopticon-great-ideas)\n"
    md_output += "- [Part V: Scripture Index](#part-v-master-scripture-index)\n\n"
    
    # PART I: GLOSSARY
    md_output += "# Part I: Encyclopedic Glossary of Neo-Calvinist Concepts\n\n"
    for term, definition in sorted(ENCYCLOPEDIC_CONCEPTS.items()):
        md_output += f"### {term}\n{definition}\n\n"
        
    # PART II: BIOGRAPHICAL REGISTER
    md_output += "\n# Part II: Biographical Register\n\n"
    for name, bio in sorted(BIOGRAPHICAL_REGISTER.items()):
        md_output += f"### {name}\n{bio}\n\n"
        
    # PART III: GENERAL INDEX
    md_output += "\n# Part III: Master General Index\n\n"
    for term in sorted(master_gen.keys()):
        refs = []
        for (vol, pg) in sorted(list(master_gen[term])):
            refs.append(f"{vol}: {pg}")
        md_output += f"* **{term}**: {', '.join(refs)}\n"

    # PART IV: SYNOPTICON
    md_output += "\n# Part IV: The Synopticon (Great Ideas)\n\n"
    md_output += "> This Synopticon maps the 102 Great Ideas of the Western World (Adler) to the text of *Antirevolutionary Politics*.\n\n"
    
    # Load Essays
    essays_path = 'synthesis_essays.json'
    SYNTHESIS_ESSAYS = {}
    if os.path.exists(essays_path):
        with open(essays_path, 'r', encoding='utf-8') as f:
            SYNTHESIS_ESSAYS = json.load(f)
            
    all_keys = sorted(master_ideas.keys())
    
    for idea in all_keys:
        import re
        # Clean HTML from essay for MD
        essay_html = SYNTHESIS_ESSAYS.get(idea, "")
        essay_md = ""
        if essay_html:
            # Simple regex strip of divs/p, keep bold/italic
            clean = re.sub(r'<[^>]+>', '', essay_html).strip()
            # Better: extract title from h4
            h4_match = re.search(r'<h4>(.*?)</h4>', essay_html)
            title_text = h4_match.group(1) if h4_match else "Synthesis"
            
            body_match = re.search(r'<p>(.*?)</p>', essay_html, re.DOTALL)
            body_text = body_match.group(1) if body_match else ""
            # Remove internal tags
            body_text = re.sub(r'<[^>]+>', '', body_text).replace('\n', ' ').replace('  ', ' ')
            
            essay_md = f"### {title_text}\n\n{body_text}\n\n"
        
        md_output += f"## {idea}\n\n"
        md_output += essay_md
        
        # Refs
        vol_refs = defaultdict(list)
        for (vol_label, pg) in master_ideas[idea]:
             vol_refs[vol_label].append(str(pg))
             
        ref_strings = []
        for vol in sorted(vol_refs.keys()):
             unique_pages = sorted(list(set(vol_refs[vol])), key=lambda x: int(x) if x.isdigit() else 0)
             ref_strings.append(f"**{vol}**: {', '.join(unique_pages)}")
             
        md_output += f"*References*: {'; '.join(ref_strings)}\n\n---\n\n"

    # PART V: SCRIPTURE INDEX
    md_output += "\n# Part V: Master Scripture Index\n\n"
    for ref in sorted(master_bible.keys()):
        locs = []
        for (vol, pg) in sorted(list(master_bible[ref])):
            locs.append(f"{vol}: {pg}")
        md_output += f"* **{ref}**: {', '.join(locs)}\n"


    with open("01_Editions/Antirevolutionary_Politics_Vol3_Master_Index.md", 'w', encoding='utf-8') as f:
        f.write(md_output)
    print("✅ Generated: 01_Editions/Antirevolutionary_Politics_Vol3_Master_Index.md")


if __name__ == "__main__":
    u_name = "Daniel Metcalf"
    # Ensure output directory exists (run from root)
    os.makedirs('01_Editions', exist_ok=True)

    # 1. PRINT CHUNKS (With Paged.js)
    v1_p1 = create_scholarly_edition('02_Source_Materials/Kuyper_Antirevolutionary_Politics_Vol1_FULL.md', '01_Editions/Antirevolutionary_Politics_Vol1_Part1.html', 'Antirevolutionary Politics I (P1)', 'I', u_name, start_chap=1, end_chap=6)
    v1_p2 = create_scholarly_edition('02_Source_Materials/Kuyper_Antirevolutionary_Politics_Vol1_FULL.md', '01_Editions/Antirevolutionary_Politics_Vol1_Part2.html', 'Antirevolutionary Politics I (P2)', 'I', u_name, start_chap=7, end_chap=12)
    
    v2_p1 = create_scholarly_edition('02_Source_Materials/Kuyper_Antirevolutionary_Politics_Vol2_FULL.md', '01_Editions/Antirevolutionary_Politics_Vol2_Part1.html', 'Antirevolutionary Politics II (P1)', 'II', u_name, start_chap=1, end_chap=6)
    v2_p2 = create_scholarly_edition('02_Source_Materials/Kuyper_Antirevolutionary_Politics_Vol2_FULL.md', '01_Editions/Antirevolutionary_Politics_Vol2_Part2.html', 'Antirevolutionary Politics II (P2)', 'II', u_name, start_chap=7, end_chap=12)

    # 2. FULL READING EDITIONS (Fast, No Paged.js)
    v1_full = create_scholarly_edition('02_Source_Materials/Kuyper_Antirevolutionary_Politics_Vol1_FULL.md', '01_Editions/Antirevolutionary_Politics_Vol1_Full_Reading_Edition.html', 'Antirevolutionary Politics I (Full)', 'I', u_name, start_chap=None, paged_js=False)
    v2_full = create_scholarly_edition('02_Source_Materials/Kuyper_Antirevolutionary_Politics_Vol2_FULL.md', '01_Editions/Antirevolutionary_Politics_Vol2_Full_Reading_Edition.html', 'Antirevolutionary Politics II (Full)', 'II', u_name, start_chap=None, paged_js=False)
    
    # 3. VOL III (Companion)
    create_master_volume_iii(v1_full, v2_full, u_name)
