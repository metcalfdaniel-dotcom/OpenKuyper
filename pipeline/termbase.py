#!/usr/bin/env python3
"""
OpenKuyper Termbase Manager

Dynamic terminology lockfile with:
- Load/save termbase from JSON
- Automatic enforcement in prompts
- Drift detection across translations
- Confidence scoring and human review flags
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class TermEntry:
    """Single terminology entry with metadata."""
    dutch: str
    english: str
    confidence: str = "medium"  # low, medium, high, locked
    context: str = ""           # Example sentence for disambiguation
    notes: str = ""             # Translator notes
    first_seen: str = ""        # Chapter/page where first encountered
    review_flag: bool = False   # True if human review needed
    alternates: list = field(default_factory=list)  # Other valid translations
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "TermEntry":
        return cls(**data)


class Termbase:
    """Manages the dynamic terminology lockfile."""
    
    def __init__(self, path: Optional[Path] = None):
        self.path = path or Path(__file__).parent.parent / "termbase" / "kuyper_termbase.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.entries: dict[str, TermEntry] = {}  # keyed by dutch term
        self._load()
    
    def _load(self):
        """Load termbase from disk or seed with defaults."""
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key, entry_data in data.items():
                self.entries[key] = TermEntry.from_dict(entry_data)
            print(f"Loaded {len(self.entries)} entries from {self.path}")
        else:
            self._seed_defaults()
            self.save()
            print(f"Seeded {len(self.entries)} default entries to {self.path}")
    
    def _seed_defaults(self):
        """Seed with the verified Phase 1 terminology."""
        defaults = [
            ("geloof", "faith", "high"),
            ("genade", "grace", "high"),
            ("heiligmaking", "sanctification", "high"),
            ("rechtvaardiging", "justification", "high"),
            ("verlossing", "salvation", "high"),
            ("verzoening", "atonement", "high"),
            ("verkiezing", "election", "high"),
            ("voorzienigheid", "providence", "high"),
            ("openbaring", "revelation", "high"),
            ("schrift", "Scripture", "high"),
            ("verbond", "covenant", "high"),
            ("kerk", "church", "high"),
            ("sacrament", "sacrament", "high"),
            ("doop", "baptism", "high"),
            ("zonde", "sin", "high"),
            ("schuld", "guilt", "high"),
            ("sfeer", "sphere", "high"),
            ("soevereiniteit", "sovereignty", "high"),
            ("soevereiniteit in eigen kring", "sphere sovereignty", "high"),
            ("staat", "state", "high"),
            ("overheid", "government", "high"),
            ("revolutie", "revolution", "high"),
            ("antirevolutionair", "antirevolutionary", "high"),
            ("beginsel", "principle", "high"),
            ("grondwet", "constitution", "high"),
            ("recht", "law / right", "medium"),
            ("volk", "people / nation", "medium"),
            ("natie", "nation", "high"),
            ("maatschappij", "society", "high"),
            ("gezin", "family", "high"),
            ("school", "school", "high"),
            ("ziel", "soul", "high"),
            ("geest", "spirit", "high"),
            ("hart", "heart", "high"),
            ("geweten", "conscience", "high"),
            ("bewustzijn", "consciousness", "high"),
            ("vermogen", "faculty / power", "medium"),
            ("wil", "will", "high"),
            ("verstand", "intellect / understanding", "medium"),
            ("natuur", "nature", "high"),
            ("algemeene genade", "common grace", "high"),
            ("bijzondere genade", "particular grace / special grace", "high"),
            ("levenssysteem", "life-system / life and thought system", "high"),
            ("wereldbeschouwing", "worldview / world-and-life view", "high"),
            ("gereformeerd", "Reformed / Calvinistic", "high"),
            ("calvinistisch", "Calvinistic", "high"),
            ("katholiek", "catholic / universal", "medium"),
            ("daarom", "therefore / hence", "high"),
            ("zodat", "so that", "high"),
            ("echter", "however / yet", "high"),
            ("immers", "for / since / indeed", "medium"),
            ("namelijk", "namely / that is to say", "high"),
            ("wel", "indeed / truly / certainly", "medium"),
            ("toch", "yet / still / nevertheless", "medium"),
        ]
        for dutch, english, confidence in defaults:
            self.entries[dutch] = TermEntry(dutch=dutch, english=english, confidence=confidence)
    
    def save(self):
        """Save termbase to disk."""
        data = {k: v.to_dict() for k, v in self.entries.items()}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get(self, dutch: str) -> Optional[TermEntry]:
        """Get entry by Dutch term."""
        return self.entries.get(dutch.lower().strip())
    
    def add(self, entry: TermEntry, overwrite: bool = False):
        """Add or update an entry."""
        key = entry.dutch.lower().strip()
        if key in self.entries and not overwrite:
            return False
        self.entries[key] = entry
        self.save()
        return True
    
    def lock_term(self, dutch: str):
        """Lock a term to prevent drift (highest confidence)."""
        key = dutch.lower().strip()
        if key in self.entries:
            self.entries[key].confidence = "locked"
            self.save()
    
    def detect_drift(self, text: str, context: str = "") -> list[dict]:
        """Scan text for potential terminology drift.
        
        Returns list of alerts: [{term, expected, found, context}]
        """
        alerts = []
        text_lower = text.lower()
        
        for key, entry in self.entries.items():
            # Only check high/locked confidence terms
            if entry.confidence not in ("high", "locked"):
                continue
            
            # Check if Dutch term appears but English translation doesn't
            if key in text_lower:
                expected = entry.english.lower()
                # Split multi-word translations
                expected_parts = expected.split(" / ")[0].split()
                
                # Look within a window around the Dutch term
                idx = text_lower.find(key)
                window_start = max(0, idx - 200)
                window_end = min(len(text_lower), idx + 200)
                window = text_lower[window_start:window_end]
                
                # Check if any expected part is in window
                found = any(part in window for part in expected_parts if len(part) > 3)
                
                if not found:
                    alerts.append({
                        "term": key,
                        "expected": entry.english,
                        "found": "MISSING",
                        "context": context or f"near position {idx}",
                        "severity": "high" if entry.confidence == "locked" else "medium"
                    })
        
        return alerts
    
    def get_prompt_block(self, max_entries: int = 100) -> str:
        """Generate a terminology block for injection into prompts."""
        lines = ["## MANDATORY TERMINOLOGY (do not deviate)", ""]
        
        # Prioritize locked and high-confidence terms
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda e: (0 if e.confidence == "locked" else 1 if e.confidence == "high" else 2),
        )
        
        for entry in sorted_entries[:max_entries]:
            marker = "🔒" if entry.confidence == "locked" else "⭐" if entry.confidence == "high" else ""
            lines.append(f"- {marker} **{entry.dutch}** → {entry.english}")
            if entry.notes:
                lines.append(f"  Note: {entry.notes}")
        
        return "\n".join(lines)
    
    def stats(self) -> dict:
        """Return termbase statistics."""
        total = len(self.entries)
        locked = sum(1 for e in self.entries.values() if e.confidence == "locked")
        high = sum(1 for e in self.entries.values() if e.confidence == "high")
        flagged = sum(1 for e in self.entries.values() if e.review_flag)
        return {
            "total_entries": total,
            "locked": locked,
            "high_confidence": high,
            "review_flags": flagged,
            "path": str(self.path)
        }


if __name__ == "__main__":
    # Test
    tb = Termbase()
    print(tb.stats())
    print("\nPrompt block (first 10 entries):")
    print(tb.get_prompt_block(max_entries=10))
