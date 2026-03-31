
import os
import re
import html
import pdfplumber

# Files
VOL1_MD = 'Kuyper_Antirevolutionary_Politics_Vol1_FULL.md'
VOL2_MD = 'Kuyper_Antirevolutionary_Politics_Vol2_FULL.md'
VOL1_PDF = 'antirevolutionai01kuyp.pdf'
VOL2_PDF = 'antirevolutiona02kuyp.pdf'

VOL1_OUT = 'Antirevolutionary_Politics_Parallel_Vol1.html'
VOL2_OUT = 'Antirevolutionary_Politics_Parallel_Vol2.html'

AI_DISCLOSURE_BLOCK = """
<div class="technical-note">
    <h3>Rights, Attribution, and Fair Use</h3>
    <p><strong>Copyright &copy; 2026 by Daniel Metcalf. All rights reserved.</strong></p>
    <p>This scholarly edition is provided for educational, research, and personal use. 
    <strong>Attribution is required</strong> for any public citation or reuse of this material. 
    Commercial reproduction, distribution, or monetization of this text—in whole or in significant part—is strictly prohibited without the express written permission of the Translator (Daniel Metcalf). Fair Dealing/Fair Use for scholarly critique and citation is encouraged.</p>
    
    <h3>Technical Note & AI Disclosure</h3>
    <p>This Parallel Edition was prepared with the assistance of advanced Artificial Intelligence systems. 
    The core English text is a human-verified translation. The Dutch text is an OCR extraction from the original 1916 scans, aligned page-by-page. AI algorithms were utilized to align the segments and clean the extraction.</p>
</div>
"""

STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=Outfit:wght@300;600&display=swap');

    @page {
        size: 8.5in 11in; /* Landscape-ish or wider for parallel? */
        size: landscape;   /* Parallel is best in landscape to fit columns */
        margin: 0.5in;
        @top-center { content: "Antirevolutionary Politics | Parallel Edition"; font-family: 'Outfit'; font-size: 9pt; color: #666; }
        @bottom-center { content: counter(page); font-family: 'Crimson Pro'; font-size: 10pt; }
    }

    body { font-family: 'Crimson Pro', serif; line-height: 1.5; margin: 0; padding: 0; background: white; font-size: 11pt; }
    
    .container { display: table; width: 100%; border-collapse: collapse; page-break-inside: avoid; margin-bottom: 20px; }
    .page-row { break-inside: avoid; border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 10px; }
    
    .header-row { background: #333; color: white; padding: 4px 10px; font-family: 'Outfit', sans-serif; font-size: 0.8em; font-weight: bold; break-after: avoid; }
    
    .content-row { display: flex; flex-direction: row; }
    
    .col-eng { 
        flex: 1; 
        padding: 15px; 
        border-right: 1px solid #eee; 
        text-align: justify;
        hyphens: auto;
    }
    
    .col-dutch { 
        flex: 1; 
        padding: 15px; 
        background: #fdfdfd; 
        color: #444; 
        font-family: 'Crimson Pro', serif; 
        font-size: 0.95em; 
        white-space: pre-wrap; 
        text-align: left;
    }
    
    h1 { font-family: 'Outfit'; font-size: 24pt; text-align: center; text-transform: uppercase; break-before: always; }
    h2 { font-family: 'Outfit'; font-size: 16pt; border-bottom: 2px solid #333; margin-top: 25px; break-before: avoid; text-align: left; }
    h3 { font-family: 'Outfit'; font-size: 12pt; margin-top: 15px; text-align: left; }
    
    .technical-note { margin: 40px; border: 1px solid #ccc; padding: 20px; text-align: left; }
    .technical-note h3 { margin-top: 0; }
    
</style>
<script src="https://unpkg.com/pagedjs/dist/paged.polyfill.js"></script>
"""

def generate_html(md_pages, pdf_pages, title, output_file):
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title} - Parallel Edition</title>
    {STYLE}
</head>
<body>
    <div style="text-align:center; padding-top: 2in; page-break-after:always;">
        <h1>{title}</h1>
        <h2>Parallel Dutch-English Edition</h2>
        <p>Original Text aligned with English Translation</p>
    </div>
    
    {AI_DISCLOSURE_BLOCK}
    
    <div style="page-break-before:always;"></div>
"""
    
    all_pages = sorted(list(set(md_pages.keys()) | set(pdf_pages.keys())))
    
    for pg in all_pages:
        if pg == 0: continue
        
        eng_text = md_pages.get(pg, "")
        dutch_text = pdf_pages.get(pg, "")
        
        # Determine if empty
        if not eng_text.strip() and not dutch_text.strip(): continue

        eng_html = convert_md_to_html(eng_text)
        
        # Clean up Dutch text if it has excessive newlines from extraction
        dutch_text_clean = dutch_text
        
        html_content += f"""
        <div id="p{pg}" class="page-row">
            <div class="header-row">Original Page {pg}</div>
            <div class="content-row">
                <div class="col-eng">{eng_html}</div>
                <div class="col-dutch">{html.escape(dutch_text_clean)}</div>
            </div>
        </div>
        """
        
    html_content += "</body></html>"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {output_file}")

def convert_md_to_html(text):
    text = html.escape(text)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # text = re.sub(r'\n\n+', '</p><p>', text) # This can be too aggressive if we want block structure
    # Just wrap paragraphs
    paras = text.split('\n\n')
    new_paras = []
    for p in paras:
        if p.strip():
            if not p.strip().startswith('<h'):
                new_paras.append(f'<p>{p.strip()}</p>')
            else:
                new_paras.append(p.strip())
    return "\n".join(new_paras)


if __name__ == "__main__":
    # Vol 1
    pdf_p_1 = extract_pdf_pages(VOL1_PDF)
    md_p_1 = parse_md_by_page(VOL1_MD)
    generate_html(md_p_1, pdf_p_1, "Antirevolutionary Politics Vol 1", VOL1_OUT)
    
    # Vol 2
    pdf_p_2 = extract_pdf_pages(VOL2_PDF)
    md_p_2 = parse_md_by_page(VOL2_MD)
    generate_html(md_p_2, pdf_p_2, "Antirevolutionary Politics Vol 2", VOL2_OUT)
