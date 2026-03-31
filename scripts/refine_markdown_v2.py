
import re
import os

VOL1 = 'Kuyper_Antirevolutionary_Politics_Vol1_FULL.md'
VOL2 = 'Kuyper_Antirevolutionary_Politics_Vol2_FULL.md'

def refine_file(filename):
    print(f"Refining {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)

    # PASS 1: Page Markers
    # Standardize '—-' or '--' or '— ' to '—- '
    # Aim: "—- Page 123 —-"
    # Regex handles variations:
    # (dashes) (space?) Page (space?) (digits) (space?) (dashes)
    pattern_page = re.compile(r'[-—]+ ?Page ?(\d+) ?[-—]+')
    content = pattern_page.sub(r'\n\n—- Page \1 —-\n\n', content)

    # PASS 2: Broken Words (Hyphenation)
    # "re- lationship" -> "relationship"
    # match lowercase-dash-space-lowercase
    content = re.sub(r'([a-z])-\s+([a-z])', r'\1\2', content)

    # PASS 3: Embedded Section Headers
    # "Text text text. §12. Title." -> "Text text text.\n\n§12. Title."
    # We look for § followed by digits, a dot, space, and then Capital looking text
    # occurring at the end of a line or sentence.
    
    # Logic: If § is not at the start of a line (ignoring whitespace), prepend \n\n
    def fix_header(m):
        pre = m.group(1)
        header = m.group(2)
        return f"{pre.strip()}\n\n{header.strip()}"

    # Regex: (Non-newline content)(§\d+\..*)
    # We use multiline mode? No, line by line is safer for this specific pattern to avoid over-matching
    lines = content.split('\n')
    new_lines = []
    
    pat_header_embed = re.compile(r'^(.*?)(\s*§\d+\..*)$')

    for line in lines:
        # Check if line has embedded header
        # But exclude if line starts with § (already correct)
        if '§' in line and not line.strip().startswith('§'):
            m = pat_header_embed.match(line)
            if m:
                # Text | Header
                text_part = m.group(1).strip()
                header_part = m.group(2).strip()
                if text_part:
                    new_lines.append(text_part)
                    new_lines.append("") # blank line
                new_lines.append(header_part)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)

    # PASS 4: Cleanup multiple newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # PASS 5: Smart Quote Hygiene (Basic)
    # Ensure quotes matching. (Too complex for simple regex, skipping risky auto-fix)
    
    # PASS 6: Spacing around punctuation
    # " ." -> "."
    content = re.sub(r' \.', '.', content)
    # " ," -> ","
    content = re.sub(r' ,', ',', content)
    
    # PASS 7: Fix OCR "1" for "I" in Volume headers if present
    # (Risk of hitting intended 1s, limiting to "Vol. 1")
    content = re.sub(r'Vol\. 1\b', 'Vol. I', content)
    content = re.sub(r'Vol\. 2\b', 'Vol. II', content)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Processed {filename}. Size: {original_len} -> {len(content)}")

if __name__ == "__main__":
    refine_file(VOL1)
    refine_file(VOL2)
