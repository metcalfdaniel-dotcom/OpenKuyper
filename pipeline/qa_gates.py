#!/usr/bin/env python3
"""
OpenKuyper QA Gate Suite

Quality assurance gates:
1. Back-translation check: English -> Dutch -> compare
2. Logic sweep: Detect anachronisms, contradictions, omissions
3. Terminology drift detection: Check against termbase lockfile
4. Style metrics: Sentence length, periodic sentence ratio, connective usage
5. Biblical citation format check
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import google.generativeai as genai

from termbase import Termbase


@dataclass
class QAResult:
    """Results from all QA gates."""
    passed: bool
    score: float  # 0-100
    gate_results: dict
    flags: list[str]
    recommendations: list[str]


class QAGates:
    """Runs all quality assurance checks on a translation."""
    
    # Style targets from Phase 1 analysis
    TARGET_AVG_SENTENCE_LENGTH = 28.16
    TARGET_PERIODIC_RATIO = 0.35
    MIN_SENTENCE_LENGTH = 15  # Warn if average below this
    
    def __init__(self, api_key: Optional[str] = None):
        self.termbase = Termbase()
        if api_key:
            genai.configure(api_key=api_key)
            self.backtranslate_model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config={"temperature": 0.1, "max_output_tokens": 4096},
            )
        else:
            self.backtranslate_model = None
    
    def run_all(self, english_text: str, dutch_source: str = "") -> QAResult:
        """Run all QA gates and return composite result."""
        gate_results = {}
        flags = []
        recommendations = []
        
        # Gate 1: Style metrics
        print("  QA Gate 1: Style metrics...", end=" ", flush=True)
        gate_results["style_metrics"] = self.check_style_metrics(english_text)
        if gate_results["style_metrics"]["avg_sentence_length"] < self.MIN_SENTENCE_LENGTH:
            flags.append(f"Sentences too short: {gate_results['style_metrics']['avg_sentence_length']:.1f} words (target: {self.TARGET_AVG_SENTENCE_LENGTH})")
            recommendations.append("Lengthen sentences; preserve Kuyper's periodic structure")
        print("OK")
        
        # Gate 2: Terminology drift
        print("  QA Gate 2: Terminology drift...", end=" ", flush=True)
        gate_results["terminology"] = self.check_terminology(english_text)
        if gate_results["terminology"]["drift_alerts"]:
            flags.append(f"Terminology drift detected: {len(gate_results['terminology']['drift_alerts'])} alerts")
            recommendations.append("Review termbase lockfile and ensure consistent translations")
        print("OK")
        
        # Gate 3: Biblical citation format
        print("  QA Gate 3: Biblical citations...", end=" ", flush=True)
        gate_results["biblical_citations"] = self.check_biblical_citations(english_text)
        if gate_results["biblical_citations"]["modern_format_count"] > 0:
            flags.append(f"Modern biblical citations found: {gate_results['biblical_citations']['modern_format_count']}")
            recommendations.append("Use traditional format: Rom. viii. 28, not Romans 8:28")
        print("OK")
        
        # Gate 4: Anachronism detection
        print("  QA Gate 4: Anachronism check...", end=" ", flush=True)
        gate_results["anachronisms"] = self.check_anachronisms(english_text)
        if gate_results["anachronisms"]["suspected"]:
            flags.append(f"Potential anachronisms: {gate_results['anachronisms']['suspected']}")
        print("OK")
        
        # Gate 5: Back-translation (if model available)
        if self.backtranslate_model and dutch_source:
            print("  QA Gate 5: Back-translation...", end=" ", flush=True)
            gate_results["backtranslation"] = self.check_backtranslation(english_text, dutch_source)
            if gate_results["backtranslation"]["similarity_score"] < 0.6:
                flags.append(f"Back-translation divergence: {gate_results['backtranslation']['similarity_score']:.2f} similarity")
                recommendations.append("Verify translation accuracy against source")
            print("OK")
        else:
            gate_results["backtranslation"] = {"skipped": True}
        
        # Calculate composite score
        score = self._calculate_score(gate_results)
        passed = score >= 70 and len(flags) <= 3
        
        return QAResult(
            passed=passed,
            score=score,
            gate_results=gate_results,
            flags=flags,
            recommendations=recommendations,
        )
    
    def check_style_metrics(self, text: str) -> dict:
        """Analyze sentence length, periodicity, connectives."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if not sentences:
            return {"avg_sentence_length": 0, "sentence_count": 0, "periodic_ratio": 0}
        
        word_counts = [len(s.split()) for s in sentences]
        avg_length = sum(word_counts) / len(word_counts)
        
        # Detect periodic sentences (main clause after ~60% of sentence)
        periodic_count = 0
        for sent in sentences:
            words = sent.split()
            if len(words) > 20:
                # Look for main clause indicators in second half
                second_half = " ".join(words[len(words)//2:]).lower()
                if any(w in second_half for w in ["must", "confess", "maintain", "stands", "follows", "is"]):
                    periodic_count += 1
        
        periodic_ratio = periodic_count / len(sentences) if sentences else 0
        
        # Count archaic connectives
        connectives = ["hence", "whereby", "wherein", "therein", "thereby", "thereof", "nevertheless", "notwithstanding"]
        connective_count = sum(text.lower().count(c) for c in connectives)
        
        return {
            "avg_sentence_length": avg_length,
            "sentence_count": len(sentences),
            "periodic_ratio": periodic_ratio,
            "periodic_count": periodic_count,
            "connective_count": connective_count,
            "connectives_per_1000": (connective_count / len(text.split())) * 1000 if text else 0,
        }
    
    def check_terminology(self, text: str) -> dict:
        """Check for terminology drift using termbase."""
        alerts = self.termbase.detect_drift(text)
        
        # Also check for inconsistent rendering of known terms
        # e.g., "sphere sovereignty" vs "sovereignty in its own circle"
        inconsistent_pairs = [
            ("sphere sovereignty", ["sovereignty in its own circle", "sovereignty in own sphere"]),
            ("common grace", ["general grace", "universal grace"]),
            ("covenant of grace", ["grace covenant"]),
        ]
        
        for correct, incorrects in inconsistent_pairs:
            for wrong in incorrects:
                if wrong.lower() in text.lower() and correct.lower() not in text.lower():
                    alerts.append({
                        "term": wrong,
                        "expected": correct,
                        "found": wrong,
                        "context": "global",
                        "severity": "high"
                    })
        
        return {
            "drift_alerts": alerts,
            "alert_count": len(alerts),
            "high_severity": sum(1 for a in alerts if a.get("severity") == "high"),
        }
    
    def check_biblical_citations(self, text: str) -> dict:
        """Detect modern vs traditional biblical citation formats."""
        # Modern format: "Romans 8:28", "John 3:16"
        modern_pattern = re.compile(r'\b(?:Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Peter|John|Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms|Proverbs|Ecclesiastes|Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation)\s+\d+:\d+')
        
        # Traditional format: "Rom. viii. 28", "John iii. 16"
        traditional_pattern = re.compile(r'\b(?:Rom|Cor|Gal|Eph|Phil|Col|Thess|Tim|Pet|Gen|Ex|Lev|Num|Deut|Josh|Judg|Ruth|Sam|Kgs|Chr|Ezra|Neh|Est|Job|Ps|Prov|Eccles|Song|Isa|Jer|Lam|Ezek|Dan|Hos|Joel|Amos|Obad|Jonah|Mic|Nah|Hab|Zeph|Hag|Zech|Mal|Matt|Mk|Lk|Jn|Acts|Rom|Cor|Gal|Eph|Phil|Col|Thess|Tim|Tit|Phlm|Heb|Jas|Pet|Jude|Rev)\.\s*[ivxlcIVXLC]+\.\s*\d+')
        
        modern_matches = modern_pattern.findall(text)
        traditional_matches = traditional_pattern.findall(text)
        
        return {
            "modern_format_count": len(modern_matches),
            "traditional_format_count": len(traditional_matches),
            "modern_examples": modern_matches[:3],
            "traditional_examples": traditional_matches[:3],
        }
    
    def check_anachronisms(self, text: str) -> dict:
        """Flag words or phrases that sound too modern for Kuyper."""
        modern_words = [
            "lifestyle", "mindset", "paradigm", "holistic", "empowerment",
            "stakeholder", "proactive", "synergy", "wellness", "inclusive",
            "diversity", "sustainability", "impactful", "going forward",
            "at the end of the day", "moving forward", "circle back",
            "touch base", "best practice", "key takeaway", "action item",
            "deep dive", "value add", "deliverables", " bandwidth",
            "optics", "narrative", "space",
            "journey", "authentic", "intentional", "lit",
            "woke", "problematic", "toxic", "privilege",
        ]
        
        suspected = []
        text_lower = text.lower()
        for word in modern_words:
            if word.lower() in text_lower:
                suspected.append(word)
        
        return {"suspected": suspected, "count": len(suspected)}
    
    def check_backtranslation(self, english_text: str, dutch_source: str) -> dict:
        """Back-translate English to Dutch and compare with source."""
        if not self.backtranslate_model:
            return {"skipped": True}
        
        prompt = (
            "Translate this English text back into Dutch. "
            "Preserve the original Dutch style and vocabulary as closely as possible:\n\n"
            f"{english_text}"
        )
        
        resp = self.backtranslate_model.generate_content(prompt)
        backtranslation = resp.text
        
        # Simple similarity: shared word ratio
        source_words = set(dutch_source.lower().split())
        back_words = set(backtranslation.lower().split())
        
        if source_words:
            similarity = len(source_words & back_words) / len(source_words)
        else:
            similarity = 0
        
        return {
            "similarity_score": similarity,
            "backtranslation": backtranslation[:500],  # Truncated for report
            "source_word_count": len(source_words),
            "shared_word_count": len(source_words & back_words),
        }
    
    def _calculate_score(self, gate_results: dict) -> float:
        """Calculate composite QA score (0-100)."""
        score = 100
        
        # Deduct for short sentences
        if "style_metrics" in gate_results:
            avg_len = gate_results["style_metrics"]["avg_sentence_length"]
            if avg_len < 20:
                score -= 15
            elif avg_len < 25:
                score -= 5
        
        # Deduct for terminology drift
        if "terminology" in gate_results:
            alerts = gate_results["terminology"]["alert_count"]
            high_sev = gate_results["terminology"]["high_severity"]
            score -= alerts * 3 + high_sev * 5
        
        # Deduct for modern biblical citations
        if "biblical_citations" in gate_results:
            modern = gate_results["biblical_citations"]["modern_format_count"]
            score -= modern * 5
        
        # Deduct for anachronisms
        if "anachronisms" in gate_results:
            score -= gate_results["anachronisms"]["count"] * 3
        
        # Deduct for back-translation divergence
        if "backtranslation" in gate_results and not gate_results["backtranslation"].get("skipped"):
            sim = gate_results["backtranslation"]["similarity_score"]
            if sim < 0.4:
                score -= 20
            elif sim < 0.6:
                score -= 10
        
        return max(0, score)
    
    def print_report(self, result: QAResult):
        """Print human-readable QA report."""
        print("\n" + "=" * 60)
        print("QA REPORT")
        print("=" * 60)
        print(f"Score: {result.score:.1f}/100 | Passed: {'YES' if result.passed else 'NO'}")
        print(f"Flags: {len(result.flags)}")
        for flag in result.flags:
            print(f"  ⚠️  {flag}")
        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  → {rec}")
        print("=" * 60)


if __name__ == "__main__":
    # Test with a sample text
    sample = """That we, standing as we do upon the foundation of Scripture, must nevertheless confess that the covenant of grace extends to all who believe, is a principle which no Christian can deny."""
    
    qa = QAGates()
    result = qa.run_all(sample)
    qa.print_report(result)
