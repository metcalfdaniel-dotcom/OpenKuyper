
"""
This script synchronizes the generated Scholarly Apparatus back to the Markdown source files.
It ensures that the Markdown files are also "Definitive Editions" containing the Preface, Technical Note, and Appendices.
"""
import os
import re
from scholarly_data_expansion import ANNOTATIONS, ADLER_BRIDGE, EXPANDED_AUTHORS, EXPANDED_CONCEPTS, PREFACE_DRAFT, AI_DISCLOSURE, ENCYCLOPEDIC_CONCEPTS, BIOGRAPHICAL_REGISTER

# We need to strip HTML tags for the Markdown version of the Preface/Disclosure
def html_to_md(html_text):
    text = html_text.replace("<h3>", "### ").replace("</h3>", "")
    text = text.replace("<h2>", "## ").replace("</h2>", "")
    text = text.replace("<ul>", "").replace("</ul>", "")
    text = text.replace("<li>", "- ").replace("</li>", "")
    text = text.replace("<strong>", "**").replace("</strong>", "**")
    text = text.replace("<em>", "*").replace("</em>", "*")
    text = text.replace("<p>", "\n\n").replace("</p>", "")
    text = text.replace("&nbsp;", " ")
    # Simple regex to remove div tags
    text = re.sub(r'<div[^>]*>', '', text)
    text = text.replace('</div>', '')
    return text.strip()

PREFACE_MD = html_to_md(PREFACE_DRAFT)
DISCLOSURE_MD = html_to_md(AI_DISCLOSURE)

VOL1_PATH = '/Users/danielmetcalf/Desktop/1. Projects/Kuyper - Antirevolutionary Politics/Kuyper_Antirevolutionary_Politics_Vol1_FULL.md'
VOL2_PATH = '/Users/danielmetcalf/Desktop/1. Projects/Kuyper - Antirevolutionary Politics/Kuyper_Antirevolutionary_Politics_Vol2_FULL.md'
VOL3_PATH = '/Users/danielmetcalf/Desktop/1. Projects/Kuyper - Antirevolutionary Politics/Kuyper_Antirevolutionary_Politics_Vol3_Companion.md'

def update_volume_frontmatter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if Preface already exists to avoid duplication
    if "Translator’s General Preface" in content:
        print(f"Preface already present in {os.path.basename(file_path)}")
        return

    # Split frontmatter
    parts = content.split('---', 2)
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = parts[2]
        
        # Inject Preface and Disclosure after Frontmatter
        new_content = f"---{frontmatter}---\n\n{PREFACE_MD}\n\n{DISCLOSURE_MD}\n\n---\n{body}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated Front Matter for {os.path.basename(file_path)}")
    else:
        print(f"❌ Could not parse frontmatter for {os.path.basename(file_path)}")

def create_volume_3_md():
    content = f"""---
title: "Antirevolutionary Politics: Volume III - Companion & Master Index"
author: "Abraham Kuyper"
translator: "Daniel Metcalf"
date: "2026"
subject: "Archive: Principles of Antirevolutionary Politics"
---

# VOLUME III: COMPANION & MASTER INDEX

## Part I: Encyclopedic Glossary of Neo-Calvinist Concepts

"""
    for term, definition_html in ENCYCLOPEDIC_CONCEPTS.items():
        # Clean HTML definition to MD
        defn = html_to_md(definition_html)
        content += f"### {term}\n\n{defn}\n\n"

    content += "\n## Part II: Biographical Register of Key Figures\n\n"
    for name, bio_html in BIOGRAPHICAL_REGISTER.items():
        bio = html_to_md(bio_html)
        content += f"### {name}\n\n{bio}\n\n"

    content += "\n## Part III: Master Indices\n\n"
    content += "*(Note: The full interactive indices are best viewed in the Interactive HTML Edition. Below is a summary of the conceptual apparatus used.)*\n\n"
    
    content += "### Concepts Tracked\n" + ", ".join(sorted(EXPANDED_CONCEPTS)) + "\n\n"
    content += "### Authors Tracked\n" + ", ".join(sorted(EXPANDED_AUTHORS)) + "\n\n"
    content += "### Mortimer Adler's 'Great Ideas' Bridge\n"
    for idea, keywords in ADLER_BRIDGE.items():
        content += f"- **{idea}**: {', '.join(keywords)}\n"

    with open(VOL3_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created {os.path.basename(VOL3_PATH)}")

if __name__ == "__main__":
    update_volume_frontmatter(VOL1_PATH)
    update_volume_frontmatter(VOL2_PATH)
    create_volume_3_md()
