# Candidate data models

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class CandidateProfile:
    """Represents a candidate from the dataset."""
    id: str
    position: str
    english_level: str
    years_experience: float | str
    cv_text: str
    highlights: str
    looking_for: str
    additional_info: str
    
    @classmethod
    def from_csv_row(cls, row: Dict) -> "CandidateProfile":
        """Create a CandidateProfile from a CSV row dictionary."""
        # Use row index as ID (1-based for display)
        row_idx = row.get("_row_index", 0)
        candidate_id = str(row_idx + 1)  # 1-based numbering
        
        return cls(
            id=candidate_id,
            position=row.get("Position", "2D Animator"),
            english_level=str(row.get("english_level", "Not stated")),
            years_experience=row.get("years_experience", "Not stated"),
            cv_text=str(row.get("cv_text", row.get("CV", ""))),
            highlights=str(row.get("highlights", row.get("Highlights", "Not stated"))),
            looking_for=str(row.get("looking_for", row.get("Looking For", "Not stated"))),
            additional_info=str(row.get("additional_info", row.get("Moreinfo", ""))),
        )


@dataclass
class DimensionScore:
    """Score for a single evaluation dimension."""
    name: str
    score: float  # 0-10
    weight: float
    evidence: List[str] = field(default_factory=list)
    
    @property
    def weighted_score(self) -> float:
        """Return the weighted contribution to final score."""
        return self.score * self.weight * 10  # Scale to 0-100 contribution


@dataclass
class EvaluationResult:
    """Complete evaluation result for a candidate."""
    candidate_id: str
    dimension_scores: Dict[str, DimensionScore]
    final_score: float
    band: str
    status: str  # "Shortlisted", "Rejected", "Flagged for Review"
    shortlist_reasons: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    rejection_reasons: List[str] = field(default_factory=list)
    bias_flags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "candidate_id": self.candidate_id,
            "final_score": round(self.final_score, 1),
            "band": self.band,
            "status": self.status,
            "dimension_scores": {
                name: {
                    "score": round(ds.score, 1),
                    "weight": ds.weight,
                    "weighted_contribution": round(ds.weighted_score, 1),
                    "evidence": ds.evidence,
                }
                for name, ds in self.dimension_scores.items()
            },
            "shortlist_reasons": self.shortlist_reasons,
            "concerns": self.concerns,
            "rejection_reasons": self.rejection_reasons,
            "bias_flags": self.bias_flags,
        }
