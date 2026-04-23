#!/usr/bin/env python3
"""
OpenKuyper Master Pipeline

Integrated orchestrator combining:
1. Gemini Vision OCR
2. Multi-draft generation (A/B/C)
3. Agentic adjudication
4. Termbase enforcement
5. QA gates
6. Markdown compilation

Usage:
    python master_pipeline.py --pdf path/to/vol1.pdf --start 1 --end 10
    python master_pipeline.py --chapter manuscript/volume_1/ch01-introduction
    python master_pipeline.py --adjudicate-existing --vol 1
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

# Add pipeline dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from termbase import Termbase
from adjudicator import Adjudicator
from qa_gates import QAGates


# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_PDF_V1 = PROJECT_ROOT / "source-materials" / "antirevolutionai01kuyp.pdf"
SOURCE_PDF_V2 = PROJECT_ROOT / "source-materials" / "antirevolutiona02kuyp.pdf"

COST_PER_1M_INPUT_TOKENS = 0.15
COST_PER_1M_OUTPUT_TOKENS = 0.60


@dataclass
class PipelineResult:
    """Result from processing a single unit (page or chapter)."""
    label: str
    dutch_ocr: str
    winner_translation: str
    draft_a: str
    draft_b: str
    draft_c: Optional[str]
    winner: str
    evaluation: dict
    qa_score: float
    qa_passed: bool
    qa_flags: list
    cost_usd: float
    processing_time_sec: float


class MasterPipeline:
    """Orchestrates the full OCR + translation + adjudication + QA pipeline."""
    
    def __init__(self):
        self.termbase = Termbase()
        self.adjudicator = Adjudicator()
        self.qa = QAGates()
        self.total_cost = 0.0
        self.total_pages = 0
    
    def process_page_range(self, pdf_path: Path, start_page: int, end_page: int, 
                          output_dir: Path, dry_run: bool = False) -> list[PipelineResult]:
        """Process a range of pages from a PDF through the full pipeline."""
        from gemini_ocr_pipeline import process_pages, CostTracker, compile_markdown
        
        output_dir.mkdir(parents=True, exist_ok=True)
        tracker = CostTracker()
        results = []
        
        print(f"\n{'='*60}")
        print(f"MASTER PIPELINE: {pdf_path.name} pages {start_page}-{end_page}")
        print(f"{'='*60}\n")
        
        # Step 1: OCR + Draft A generation via Gemini
        print("STEP 1: OCR + Initial Translation")
        ocr_results = process_pages(pdf_path, start_page, end_page, output_dir, tracker, dry_run)
        
        if dry_run:
            print("Dry run complete.")
            return []
        
        for ocr_result in ocr_results:
            self.total_pages += 1
            page_start = time.time()
            
            print(f"\n--- Page {ocr_result.page_number or '?'} ---")
            
            # Step 2: Multi-draft generation and adjudication
            print("STEP 2: Multi-draft Adjudication")
            drafts = self.adjudicator.generate_drafts(
                dutch_text=ocr_result.dutch_ocr,
                existing_haiku=None,  # No Draft C for new OCR
            )
            
            # Inject Draft A from OCR as the faithful draft
            drafts.draft_a = ocr_result.english_translation
            
            # Run adjudication
            drafts = self.adjudicator.adjudicate(drafts)
            
            # Step 3: QA gates
            print("STEP 3: QA Gates")
            qa_result = self.qa.run_all(
                english_text=drafts.winner_text,
                dutch_source=ocr_result.dutch_ocr,
            )
            self.qa.print_report(qa_result)
            
            # If QA fails, optionally re-run Draft A with stricter prompt
            if not qa_result.passed and qa_result.score < 50:
                print("⚠️ QA failed severely. Flagging for human review.")
                qa_result.flags.append("SEVERE_QA_FAILURE: Human review required")
            
            # Compile result
            pipeline_result = PipelineResult(
                label=ocr_result.page_number or f"p{self.total_pages}",
                dutch_ocr=ocr_result.dutch_ocr,
                winner_translation=drafts.winner_text,
                draft_a=drafts.draft_a,
                draft_b=drafts.draft_b,
                draft_c=drafts.draft_c,
                winner=drafts.winner,
                evaluation=drafts.evaluation,
                qa_score=qa_result.score,
                qa_passed=qa_result.passed,
                qa_flags=qa_result.flags,
                cost_usd=ocr_result.cost_usd + 0.001,  # Approximate adjudication cost
                processing_time_sec=time.time() - page_start,
            )
            results.append(pipeline_result)
            
            # Save individual result
            result_file = output_dir / f"page_{pipeline_result.label}_pipeline.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(asdict(pipeline_result), f, indent=2, ensure_ascii=False)
        
        # Step 4: Compile final markdown
        print("\nSTEP 4: Compiling final output...")
        self._compile_final_output(results, output_dir)
        
        # Update totals
        self.total_cost += tracker.total_cost_usd
        
        print(f"\n{'='*60}")
        print("PIPELINE COMPLETE")
        print(f"{'='*60}")
        print(f"Pages: {self.total_pages}")
        print(f"Total cost: ${self.total_cost:.4f} USD")
        print(f"Output: {output_dir}")
        
        return results
    
    def process_existing_chapter(self, chapter_dir: Path, output_dir: Path):
        """Run adjudication + QA on an existing chapter with Haiku Draft C."""
        dutch_file = chapter_dir / "dutch_source.md"
        draft_c_file = chapter_dir / "english_refined.md"
        
        if not dutch_file.exists():
            print(f"No dutch_source.md in {chapter_dir}")
            return
        
        print(f"\n{'='*60}")
        print(f"PROCESSING EXISTING CHAPTER: {chapter_dir.name}")
        print(f"{'='*60}\n")
        
        dutch_text = dutch_file.read_text(encoding="utf-8")
        draft_c = draft_c_file.read_text(encoding="utf-8") if draft_c_file.exists() else None
        
        # Step 1: Generate Drafts A and B, include Draft C
        print("STEP 1: Generating Drafts A + B, loading Draft C...")
        drafts = self.adjudicator.generate_drafts(dutch_text, draft_c)
        
        # Step 2: Adjudicate
        print("STEP 2: Adjudicating A vs B vs C...")
        drafts = self.adjudicator.adjudicate(drafts)
        
        # Step 3: QA
        print("STEP 3: QA Gates...")
        qa_result = self.qa.run_all(drafts.winner_text, dutch_text)
        self.qa.print_report(qa_result)
        
        # Save results
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result = {
            "chapter": chapter_dir.name,
            "winner": drafts.winner,
            "winner_text": drafts.winner_text,
            "evaluation": drafts.evaluation,
            "qa_score": qa_result.score,
            "qa_passed": qa_result.passed,
            "qa_flags": qa_result.flags,
            "drafts": {
                "A": drafts.draft_a,
                "B": drafts.draft_b,
                "C": drafts.draft_c,
            }
        }
        
        result_file = output_dir / f"{chapter_dir.name}_adjudication.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        winner_file = output_dir / f"{chapter_dir.name}_winner.md"
        winner_file.write_text(drafts.winner_text, encoding="utf-8")
        
        print(f"\nSaved to {result_file}")
        print(f"Winner saved to {winner_file}")
        
        return result
    
    def _compile_final_output(self, results: list[PipelineResult], output_dir: Path):
        """Compile all page results into final markdown."""
        lines = [
            "# Antirevolutionaire Staatkunde — Translation Output",
            "",
            f"**Pages:** {len(results)}",
            f"**Pipeline:** OpenKuyper Master v1.0",
            f"**Model:** gemini-2.5-flash",
            f"**Voice Standard:** OpenKuyper Comprehensive Style Database",
            "",
            "---",
            "",
        ]
        
        for result in results:
            lines.extend([
                f"## Page {result.label}",
                "",
                "### Dutch (OCR)",
                result.dutch_ocr,
                "",
                "### English Translation (Winner)",
                result.winner_translation,
                "",
                f"**Winner:** Draft {result.winner} | **QA Score:** {result.qa_score:.1f}/100 | **Passed:** {'Yes' if result.qa_passed else 'No'}",
                "",
            ])
            if result.qa_flags:
                lines.append("**QA Flags:**")
                for flag in result.qa_flags:
                    lines.append(f"- ⚠️ {flag}")
                lines.append("")
            lines.append("---")
            lines.append("")
        
        output_path = output_dir / "FINAL_OUTPUT.md"
        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Final output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="OpenKuyper Master Pipeline")
    parser.add_argument("--pdf", type=Path, default=SOURCE_PDF_V1,
                        help="Source PDF (default: Vol 1)")
    parser.add_argument("--start", type=int, default=1,
                        help="First page (1-indexed)")
    parser.add_argument("--end", type=int, default=5,
                        help="Last page (1-indexed)")
    parser.add_argument("--output-dir", type=Path, 
                        default=PROJECT_ROOT / "manuscript" / "pipeline_output",
                        help="Output directory")
    parser.add_argument("--chapter", type=Path,
                        help="Process existing chapter directory (with Draft C)")
    parser.add_argument("--adjudicate-existing", action="store_true",
                        help="Run adjudication on all existing chapters")
    parser.add_argument("--vol", type=int, choices=[1, 2], default=1,
                        help="Volume for --adjudicate-existing")
    parser.add_argument("--dry-run", action="store_true",
                        help="Skip API calls")
    args = parser.parse_args()
    
    pipeline = MasterPipeline()
    
    if args.chapter:
        # Single chapter mode
        pipeline.process_existing_chapter(args.chapter, args.output_dir)
    elif args.adjudicate_existing:
        # Batch mode: all chapters in volume
        vol_dir = PROJECT_ROOT / "manuscript" / f"volume_{args.vol}"
        if not vol_dir.exists():
            print(f"Volume directory not found: {vol_dir}")
            return
        
        for chapter_dir in sorted(vol_dir.iterdir()):
            if chapter_dir.is_dir():
                try:
                    pipeline.process_existing_chapter(chapter_dir, args.output_dir)
                except Exception as e:
                    print(f"Error processing {chapter_dir.name}: {e}")
    else:
        # Fresh OCR mode
        pipeline.process_page_range(
            pdf_path=args.pdf,
            start_page=args.start,
            end_page=args.end,
            output_dir=args.output_dir,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
