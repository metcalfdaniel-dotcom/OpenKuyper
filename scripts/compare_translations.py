#!/usr/bin/env python3
"""
OpenKuyper Translation Comparator

Renders two markdown translations side-by-side in HTML.
Useful for reviewing Dutch source against English translation paragraph-by-paragraph.

Usage:
    python scripts/compare_translations.py \
        volume-01/foreword.nl.md \
        volume-01/foreword.en.md \
        --output foreword_comparison.html

    open foreword_comparison.html
"""

import argparse
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Paragraph:
    text: str
    ptype: str  # 'text', 'heading', 'footnote', 'blockquote', 'empty'


def parse_markdown(path: Path) -> list:
    """Split markdown into paragraph-aligned blocks."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings
    content = content.replace("\r\n", "\n")

    # Split into blocks (double newline = paragraph break)
    raw_blocks = re.split(r"\n\n+", content.strip())

    paragraphs = []
    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        # Detect type
        if block.startswith("#"):
            ptype = "heading"
        elif block.startswith(">"):
            ptype = "blockquote"
        elif block.startswith("[") and "^" in block:
            ptype = "footnote"
        elif block.startswith("---"):
            ptype = "separator"
        elif block.startswith("!") or block.startswith("[") and "](" in block:
            ptype = "figure"
        else:
            ptype = "text"

        paragraphs.append(Paragraph(text=block, ptype=ptype))

    return paragraphs


def escape_html(text: str) -> str:
    """Minimal HTML escape, preserving markdown formatting for rendering."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def markdown_to_html(text: str) -> str:
    """Convert markdown to basic HTML for display."""
    text = escape_html(text)

    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)

    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)

    # Headings
    text = re.sub(r"^###### (.+)$", r"<h6>\1</h6>", text, flags=re.MULTILINE)
    text = re.sub(r"^##### (.+)$", r"<h5>\1</h5>", text, flags=re.MULTILINE)
    text = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", text, flags=re.MULTILINE)
    text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)

    # Footnote refs [^N]
    text = re.sub(r"\[\^(\d+)\]", r"<sup>[\1]</sup>", text)

    # Footnote defs [^N]: ...
    text = re.sub(r"^\[\^(\d+)\]: (.+)$", r"<p class=\"footnote\"><sup>\1</sup> \2</p>", text, flags=re.MULTILINE)

    # Blockquote
    if text.startswith(">"):
        text = text.replace("> ", "").replace(">", "")
        text = f'<blockquote>{text}</blockquote>'

    # Line breaks within paragraph
    text = text.replace("\n", "<br>")

    return text


def render_row(left: Optional[Paragraph], right: Optional[Paragraph]) -> str:
    """Render a single table row with left and right paragraphs."""
    left_html = ""
    right_html = ""
    left_type = ""
    right_type = ""

    if left:
        left_html = markdown_to_html(left.text)
        left_type = f' data-type="{left.ptype}"'
    if right:
        right_html = markdown_to_html(right.text)
        right_type = f' data-type="{right.ptype}"'

    # Highlight structural mismatches
    mismatch = ""
    if left and right and left.ptype != right.ptype:
        mismatch = ' class="mismatch"'

    return (
        f"<tr{mismatch}>"
        f'<td class="source"{left_type}>{left_html}</td>'
        f'<td class="target"{right_type}>{right_html}</td>'
        f"</tr>\n"
    )


def build_html(left_paras: list[Paragraph], right_paras: list[Paragraph],
               left_title: str, right_title: str) -> str:
    """Build full HTML document."""

    max_len = max(len(left_paras), len(right_paras))

    rows = []
    for i in range(max_len):
        left = left_paras[i] if i < len(left_paras) else None
        right = right_paras[i] if i < len(right_paras) else None
        rows.append(render_row(left, right))

    css = """
    :root {
      --bg: #fafafa;
      --text: #222;
      --border: #ddd;
      --highlight: #fff3cd;
      --heading-bg: #f0f0f0;
      --footnote-bg: #f8f8f8;
    }
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 20px;
      line-height: 1.6;
    }
    h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
    .subtitle { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      font-size: 0.95rem;
    }
    th {
      background: var(--heading-bg);
      padding: 12px;
      text-align: left;
      font-weight: 600;
      border-bottom: 2px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 10;
    }
    td {
      padding: 12px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
      width: 50%;
    }
    .source { border-right: 2px solid var(--border); }
    .target { background: #fff; }
    tr:hover td { background: var(--highlight); }
    tr.mismatch td { border-left: 3px solid #dc3545; }
    h1, h2, h3, h4, h5, h6 { margin: 0.2rem 0; }
    blockquote {
      margin: 0.5rem 0;
      padding-left: 1rem;
      border-left: 3px solid #ccc;
      color: #555;
    }
    .footnote {
      font-size: 0.85rem;
      color: #555;
      background: var(--footnote-bg);
      padding: 4px 8px;
      border-radius: 4px;
    }
    sup { color: #0066cc; }
    @media print {
      body { padding: 0; }
      td { font-size: 0.85rem; padding: 8px; }
    }
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{left_title} ↔ {right_title}</title>
<style>{css}</style>
</head>
<body>
<h1>Side-by-Side Translation</h1>
<p class="subtitle">{left_title} (left) ↔ {right_title} (right) — {max_len} paragraph blocks</p>
<table>
<thead>
  <tr><th>{left_title}</th><th>{right_title}</th></tr>
</thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser(description="Render two translations side-by-side")
    parser.add_argument("source", type=Path, help="Source markdown (e.g., foreword.nl.md)")
    parser.add_argument("target", type=Path, help="Target markdown (e.g., foreword.en.md)")
    parser.add_argument("--output", "-o", type=Path, default=Path("comparison.html"), help="Output HTML file")
    parser.add_argument("--source-label", default="Source", help="Label for left column")
    parser.add_argument("--target-label", default="Target", help="Label for right column")
    args = parser.parse_args()

    if not args.source.exists():
        print(f"ERROR: Source file not found: {args.source}")
        return 1
    if not args.target.exists():
        print(f"ERROR: Target file not found: {args.target}")
        return 1

    left_paras = parse_markdown(args.source)
    right_paras = parse_markdown(args.target)

    html = build_html(left_paras, right_paras, args.source_label, args.target_label)

    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {len(left_paras)} source / {len(right_paras)} target paragraphs to {args.output}")
    print(f"Open: file://{args.output.resolve()}")
    return 0


if __name__ == "__main__":
    exit(main())
