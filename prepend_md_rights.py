
import os

DISCLOSURE = """
> [!NOTE] 
> **Rights, Attribution, and Fair Use**
> 
> Copyright (c) 2026 by Daniel Metcalf. All rights reserved.
>
> This scholarly edition is provided for educational, research, and personal use. **Attribution is required** for any public citation or reuse of this material. Commercial reproduction, distribution, or monetization of this text—in whole or in significant part—is strictly prohibited without the express written permission of the Translator (Daniel Metcalf). Fair Dealing/Fair Use for scholarly critique and citation is encouraged.
> 
> *Technical Note & AI Disclosure*: This text was prepared with the assistance of advanced Artificial Intelligence systems. The core text is a human-verified translation. However, AI algorithms were utilized to synthesize the indices and align the parallel text.
"""

MD_FILES = [
    '01_Editions/Kuyper_Antirevolutionary_Politics_Vol1_FULL.md',
    '01_Editions/Kuyper_Antirevolutionary_Politics_Vol2_FULL.md'
]

def prepend_frontmatter():
    for fpath in MD_FILES:
        if not os.path.exists(fpath):
            print(f"Skipping {fpath} (not found)")
            continue
            
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if already present to avoid double stacking
        if "Rights, Attribution, and Fair Use" in content:
            print(f"Front matter already present in {fpath}")
            continue
            
        # Insert after YAML front matter if present, or at top
        if content.startswith('---'):
            # Find second ---
            parts = content.split('---', 2)
            if len(parts) >= 3:
                new_content = f"---{parts[1]}---\n\n{DISCLOSURE}\n\n{parts[2]}"
            else:
                new_content = DISCLOSURE + "\n\n" + content
        else:
            new_content = DISCLOSURE + "\n\n" + content
            
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Prepended Front Matter to {fpath}")

if __name__ == '__main__':
    prepend_frontmatter()
