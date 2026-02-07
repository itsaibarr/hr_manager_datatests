# Output formatting for evaluation results

from typing import List
from .candidate import EvaluationResult


def format_evaluation(result: EvaluationResult) -> str:
    """Format a single evaluation result for display."""
    lines = []
    
    # Header
    lines.append(f"{'='*60}")
    lines.append(f"Candidate: {result.candidate_id}")
    lines.append(f"Final Score: {result.final_score:.1f} / 100 ({result.band})")
    lines.append(f"Status: {result.status}")
    lines.append("")
    
    # Dimension breakdown
    lines.append("Dimension Scores:")
    for name, ds in result.dimension_scores.items():
        lines.append(f"  • {ds.name} ({int(ds.weight*100)}%): {ds.score:.1f}/10 → {ds.weighted_score:.1f} pts")
        if ds.evidence:
            for ev in ds.evidence[:2]:
                lines.append(f"      └─ {ev}")
    
    lines.append("")
    
    # Status-specific output
    if result.status == "Shortlisted":
        if result.shortlist_reasons:
            lines.append("Why Shortlisted:")
            for i, reason in enumerate(result.shortlist_reasons, 1):
                lines.append(f"  {i}. {reason}")
        
        if result.concerns:
            lines.append("")
            lines.append("Potential Concerns:")
            for concern in result.concerns:
                lines.append(f"  ⚠ {concern}")
    
    elif result.status == "Rejected":
        lines.append("Rejection Reasons:")
        for reason in result.rejection_reasons:
            lines.append(f"  ✗ {reason}")
    
    elif result.status == "Flagged for Review":
        lines.append("⚠ FLAGGED FOR HUMAN REVIEW")
        lines.append("Issue: Non-job-related personal data detected")
        if result.bias_flags:
            for flag in result.bias_flags:
                lines.append(f"  • {flag}")
    
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)


def format_summary(results: List[EvaluationResult]) -> str:
    """Format summary statistics for a batch of evaluations."""
    total = len(results)
    
    # Count by status
    shortlisted = sum(1 for r in results if r.status == "Shortlisted")
    rejected = sum(1 for r in results if r.status == "Rejected")
    flagged = sum(1 for r in results if r.status == "Flagged for Review")
    
    # Count by band
    strong_fit = sum(1 for r in results if r.band == "Strong Fit")
    good_fit = sum(1 for r in results if r.band == "Good Fit")
    borderline = sum(1 for r in results if r.band == "Borderline")
    reject_band = sum(1 for r in results if r.band == "Reject")
    
    # Score statistics
    scores = [r.final_score for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    lines = [
        "",
        "=" * 60,
        "EVALUATION SUMMARY",
        "=" * 60,
        "",
        f"Total Candidates: {total}",
        "",
        "By Status:",
        f"  ✓ Shortlisted:        {shortlisted:3d} ({shortlisted/total*100:.1f}%)",
        f"  ✗ Rejected:           {rejected:3d} ({rejected/total*100:.1f}%)",
        f"  ⚠ Flagged for Review: {flagged:3d} ({flagged/total*100:.1f}%)",
        "",
        "By Band:",
        f"  Strong Fit (85-100):  {strong_fit:3d}",
        f"  Good Fit (70-84):     {good_fit:3d}",
        f"  Borderline (60-69):   {borderline:3d}",
        f"  Reject (<60):         {reject_band:3d}",
        "",
        "Score Statistics:",
        f"  Average: {avg_score:.1f}",
        f"  Range:   {min_score:.1f} - {max_score:.1f}",
        "",
        "=" * 60,
    ]
    
    return "\n".join(lines)


def format_compact(result: EvaluationResult) -> str:
    """Format a single result in compact single-line format."""
    return (
        f"{result.candidate_id[:8]}... | "
        f"Score: {result.final_score:5.1f} | "
        f"Band: {result.band:12s} | "
        f"Status: {result.status}"
    )
