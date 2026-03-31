
import os
import re
import pdfplumber

# Files
VOL1_MD = 'Kuyper_Antirevolutionary_Politics_Vol1_FULL.md'
VOL2_MD = 'Kuyper_Antirevolutionary_Politics_Vol2_FULL.md'
VOL1_PDF = 'antirevolutionai01kuyp.pdf'
VOL2_PDF = 'antirevolutiona02kuyp.pdf'

VOL1_DUTCH_OUT = 'Kuyper_Antirevolutionary_Politics_Vol1_Dutch.md'
VOL2_DUTCH_OUT = 'Kuyper_Antirevolutionary_Politics_Vol2_Dutch.md'

def extract_pdf_pages(pdf_path):
    print(f"Extracting PDF with pdfplumber: {pdf_path}")
    pages = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                pages[i + 1] = text if text else "[Empty]"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return pages

def get_page_numbers_from_md(md_path):
    print(f"Scanning pages in: {md_path}")
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ids = re.findall(r'—- Page (\d+) —-', content)
    return [int(pid) for pid in ids]

def generate_dutch_md(pdf_pages, page_ids, title, output_file):
    content = f"""---
title: "{title} (Dutch Parallel Text)"
author: "Abraham Kuyper"
date: "1916"
subject: "Original Dutch Text from PDF Extraction (Improved Layout)"
---

# {title} - ORIGINAL DUTCH TEXT

"""
    for pid in page_ids:
        text = pdf_pages.get(pid, "[Page not found in PDF]")
        
        content += f"\n\n—- Page {pid} —-\n\n"
        content += text.strip() + "\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Generated {output_file}")

if __name__ == "__main__":
    # Vol 1
    pdf_p_1 = extract_pdf_pages(VOL1_PDF)
    pids_1 = get_page_numbers_from_md(VOL1_MD)
    generate_dutch_md(pdf_p_1, pids_1, "Antirevolutionary Politics Vol I", VOL1_DUTCH_OUT)
    
    # Vol 2
    pdf_p_2 = extract_pdf_pages(VOL2_PDF)
    pids_2 = get_page_numbers_from_md(VOL2_MD)
    generate_dutch_md(pdf_p_2, pids_2, "Antirevolutionary Politics Vol II", VOL2_DUTCH_OUT)
