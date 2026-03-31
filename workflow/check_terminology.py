#!/usr/bin/env python3
"""
Terminology Consistency Checker for Kuyper Translation

Scans all English translation files for term variants and flags inconsistencies.
Reads required terms from the glossary and checks for common misspellings/variants.

Usage:
    python workflow/check_terminology.py [path_to_editions_dir]
"""

import os
import re
import sys
from pathlib import Path

# Terms that must appear in exact form (case-sensitive)
REQUIRED_TERMS = {
    "Sphere Sovereignty": [
        "sphere sovereignty",
        "Sphere sovereignty",
        "sovereignty of the sphere",
    ],
    "Common Grace": ["common grace", "Common grace"],
    "The Antithesis": ["the antithesis", "Antithesis"],
    "Ordinances of God": [
        "ordinances of god",
        "Ordinances of god",
        "ordinances Of God",
    ],
    "The Magistrate": ["the magistrate", "Magistrate"],
    "De Overheid": [],  # Dutch term - should appear as-is
    "Antirevolutionary": [
        "anti-revolutionary",
        "Anti-revolutionary",
        "anti Revolutionary",
    ],
    "Neo-Calvinist": ["neo-calvinist", "Neo calvinist", "neocalvinist"],
    "Groen van Prinsterer": [
        "groen van prinsterer",
        "Groen Van Prinsterer",
        "groen Van Prinsterer",
    ],
    "Thorbecke": [],
    "Palingenesis": ["palingenesis"],  # Should be capitalized
    "Common Grace": ["common grace"],
}

# Terms that should NOT appear (modern colloquialisms)
FORBIDDEN_TERMS = [
    "values",
    "lifestyle",
    "social construct",
    "worldview",  # Kuyper uses "life-system" or "life-and-world view"
    "mindset",
    "narrative",
    "identity politics",
    "social justice",
]

# Preferred alternatives
PREFERRED = {
    "worldview": "life-system / life-and-world view",
    "government": "Magistrate / Authority (De Overheid)",
    "rules": "ordinances / divine decrees",
    "laws of nature": "ordinances of God",
}


def scan_file(filepath: Path) -> dict:
    """Scan a single file for terminology issues."""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"file": str(filepath), "issues": [f"Could not read file: {e}"]}

    # Check forbidden terms (case-insensitive, word boundaries)
    for term in FORBIDDEN_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        if matches:
            alt = PREFERRED.get(term, "")
            issues.append(
                {
                    "type": "FORBIDDEN",
                    "term": term,
                    "count": len(matches),
                    "suggestion": f"Use '{alt}' instead" if alt else "Review usage",
                }
            )

    # Check required term variants
    for correct, variants in REQUIRED_TERMS.items():
        for variant in variants:
            pattern = r"\b" + re.escape(variant) + r"\b"
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                issues.append(
                    {
                        "type": "VARIANT",
                        "found": variant,
                        "correct": correct,
                        "count": len(matches),
                    }
                )

    return {"file": str(filepath), "issues": issues}


def main():
    editions_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("editions")

    if not editions_dir.exists():
        print(f"Error: {editions_dir} not found")
        sys.exit(1)

    md_files = list(editions_dir.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {editions_dir}")
        sys.exit(0)

    print(f"Scanning {len(md_files)} files for terminology consistency...\n")

    total_issues = 0
    for filepath in sorted(md_files):
        result = scan_file(filepath)
        if result["issues"]:
            print(f"📄 {filepath.name}")
            for issue in result["issues"]:
                total_issues += 1
                if issue["type"] == "FORBIDDEN":
                    print(
                        f"  ⛔ '{issue['term']}' found {issue['count']}x — {issue['suggestion']}"
                    )
                elif issue["type"] == "VARIANT":
                    print(
                        f"  ⚠️  '{issue['found']}' ({issue['count']}x) — should be '{issue['correct']}'"
                    )
            print()

    if total_issues == 0:
        print("✅ No terminology issues found.")
    else:
        print(f"Found {total_issues} issue(s) across {len(md_files)} files.")

    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
