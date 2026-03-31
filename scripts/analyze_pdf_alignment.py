
import os
import re
from pypdf import PdfReader

PDF_VOL1 = 'antirevolutionai01kuyp.pdf'
PDF_VOL2 = 'antirevolutiona02kuyp.pdf'
MD_VOL1 = 'Kuyper_Antirevolutionary_Politics_Vol1_FULL.md'

def extract_pdf_text_by_page(pdf_path):
    print(f"Extracting text from {pdf_path}...")
    try:
        reader = PdfReader(pdf_path)
        pages = {}
        for i, page in enumerate(reader.pages):
            # i is 0-indexed, likely corresponds to PDF page physical count
            # We need to see if we can align this with "Original Page X"
            text = page.extract_text()
            pages[i + 1] = text # Storing as physical page number for now
        return pages
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return {}

def test_alignment():
    # 1. Extract Dutch Pages
    dutch_pages = extract_pdf_text_by_page(PDF_VOL1)
    
    # 2. Check first few pages to identify "Page 1" of the actual content
    # Often PDF page 1 is cover, page 5 might be "Page 1" of text.
    print("\n--- PDF Page Analysis ---")
    for i in range(1, 15):
        preview = dutch_pages.get(i, "")[:100].replace('\n', ' ')
        print(f"PDF Page {i}: {preview}")

    # 3. Check English Markdown for Page Markers
    with open(MD_VOL1, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Find first page marker
    match = re.search(r'—- Page (\d+) —-', md_content)
    if match:
        print(f"\nFirst English Page Marker: {match.group(0)}")
        # Show context
        start = match.start()
        print(f"Context: {md_content[start:start+200]}...")

if __name__ == "__main__":
    if os.path.exists(PDF_VOL1):
        test_alignment()
    else:
        print(f"PDF {PDF_VOL1} not found.")
