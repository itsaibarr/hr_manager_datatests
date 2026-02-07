#!/usr/bin/env python3
"""
HR Agent Evaluation Runner

Run candidate evaluations on the 2D Animator dataset.

Usage:
    python run_evaluation.py --sample 5     # Evaluate 5 random candidates
    python run_evaluation.py --all          # Evaluate all candidates
    python run_evaluation.py --id <id>      # Evaluate specific candidate
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.loader import load_candidates
from src.evaluator import evaluator
from src.formatter import format_evaluation, format_summary, format_compact


DEFAULT_DATASET = PROJECT_ROOT / "clean_2d_animator_evaluation_dataset.csv"
OUTPUT_DIR = PROJECT_ROOT / "evaluation_results"


def main():
    parser = argparse.ArgumentParser(description="HR Agent Candidate Evaluation")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", type=int, help="Evaluate N random candidates")
    group.add_argument("--all", action="store_true", help="Evaluate all candidates")
    group.add_argument("--id", type=str, help="Evaluate specific candidate by ID")
    
    parser.add_argument(
        "--dataset", 
        type=str, 
        default=str(DEFAULT_DATASET),
        help="Path to candidate dataset CSV"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--compact", 
        action="store_true",
        help="Use compact output format"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Show detailed output for each candidate"
    )
    
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset from: {args.dataset}")
    candidates = load_candidates(args.dataset)
    print(f"Loaded {len(candidates)} candidates")
    print()
    
    # Select candidates to evaluate
    if args.all:
        to_evaluate = candidates
    elif args.sample:
        import random
        to_evaluate = random.sample(candidates, min(args.sample, len(candidates)))
    elif args.id:
        to_evaluate = [c for c in candidates if args.id in c.id]
        if not to_evaluate:
            print(f"No candidate found with ID containing: {args.id}")
            sys.exit(1)
    
    print(f"Evaluating {len(to_evaluate)} candidates...")
    print()
    
    # Run evaluation
    results = evaluator.evaluate_batch(to_evaluate)
    
    # Display results
    if args.compact:
        print("Results (Compact):")
        print("-" * 70)
        for result in results:
            print(format_compact(result))
    elif args.verbose or len(results) <= 5:
        for result in results:
            print(format_evaluation(result))
            print()
    else:
        # Show compact for large sets, then summary
        print("Results (Compact):")
        print("-" * 70)
        for result in results:
            print(format_compact(result))
    
    # Always show summary for batch evaluations
    if len(results) > 1:
        print(format_summary(results))
    
    # Save to JSON if requested
    if args.output:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = Path(args.output)
        
        output_data = {
            "metadata": {
                "dataset": args.dataset,
                "candidates_evaluated": len(results),
            },
            "results": [r.to_dict() for r in results],
            "summary": {
                "shortlisted": sum(1 for r in results if r.status == "Shortlisted"),
                "rejected": sum(1 for r in results if r.status == "Rejected"),
                "flagged": sum(1 for r in results if r.status == "Flagged for Review"),
            }
        }
        
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
