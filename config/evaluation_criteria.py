# Frozen Evaluation Criteria for HR Agent
# DO NOT MODIFY - These are the canonical evaluation rules

from dataclasses import dataclass
from typing import List, Dict

# =============================================================================
# DIMENSION WEIGHTS (Frozen)
# =============================================================================

DIMENSION_WEIGHTS = {
    "core_competencies": 0.35,      # 35% - Primary driver of role execution
    "experience_results": 0.25,     # 25% - Demonstrates applied ability
    "collaboration_signals": 0.20,  # 20% - Important but weakly observable
    "cultural_practical_fit": 0.15, # 15% - Reduces onboarding friction
    "education_other": 0.05,        # 5%  - Supporting signal only
}

# =============================================================================
# SCORE BANDS (Frozen)
# =============================================================================

SCORE_BANDS = {
    "strong_fit": (85, 100),
    "good_fit": (70, 84),
    "borderline": (60, 69),
    "reject": (0, 59),
}

def get_score_band(score: float) -> str:
    """Return the band label for a given score."""
    if score >= 85:
        return "Strong Fit"
    elif score >= 70:
        return "Good Fit"
    elif score >= 60:
        return "Borderline"
    else:
        return "Reject"

# =============================================================================
# REJECTION THRESHOLDS (Frozen)
# =============================================================================

REJECTION_THRESHOLD = 60  # Score below this = reject
CORE_COMPETENCY_ZERO_REJECT = True  # Zero in core competencies = immediate reject

# =============================================================================
# 2D ANIMATOR TECH STACK SIGNALS (Role-Specific)
# =============================================================================

# Required tools - ANY of these qualifies (per job requirements)
REQUIRED_TOOLS = [
    # Job lists these as acceptable
    "toon boom", "toon boom harmony",
    "after effects", "adobe after effects", "ae",
    "adobe animate", "animate cc", "flash",
    "spine", "spine 2d", "esoteric spine",
    # Similar tools also acceptable
    "moho", "anime studio",
    "opentoonz", "krita",
]

PREFERRED_TOOLS = [
    # Nice-to-have tools from job requirements
    "photoshop", "adobe photoshop",
    "unity", "unity3d",
    "dragonbones",
    "illustrator",
    "procreate",
    "tvpaint",
]

ANIMATION_SKILLS = [
    "character animation",
    "rigging", "rig", "skeletal animation",
    "vfx", "visual effects", "effects animation",
    "ui animation", "interface animation",
    "frame-by-frame", "frame by frame",
    "cutout animation", "cut-out",
    "motion graphics",
    "storyboard",
]

DOMAIN_EXPERIENCE = [
    "gamedev", "game dev", "game development",
    "mobile games", "casual games",
    "slot", "casino",
    "cartoon", "animated series",
    "youtube", 
]

# =============================================================================
# COLLABORATION SIGNALS
# =============================================================================

# Collaboration signals from job requirements
COLLABORATION_KEYWORDS = [
    # Feedback and iteration (key requirement)
    "feedback", "iterate", "iteration", "revision",
    # Adaptability and learning (key requirement)  
    "learn", "learning", "adaptable", "flexible", "willing to learn",
    # Independent work with coordination
    "independent", "self-directed", "autonomous",
    # Team coordination
    "team", "teamwork", "collaborate", "collaboration",
    "coordinate", "communication",
    # Work tools
    "jira", "confluence", "slack", "git", "figma",
]

# =============================================================================
# PROTECTED ATTRIBUTES (Bias Guardrails)
# =============================================================================

PROTECTED_ATTRIBUTES = [
    "age", "gender", "race", "ethnicity", "religion",
    "nationality", "marital status", "disability",
    "photo", "picture", "image",
]

# Patterns that suggest personal demographic data
DEMOGRAPHIC_PATTERNS = [
    r"\b(\d{1,2})\s*(years?\s*old|y\.?o\.?)\b",  # Age patterns
    r"\b(male|female|man|woman|boy|girl)\b",      # Gender patterns
    r"\b(married|single|divorced|widow)\b",       # Marital status
]

# =============================================================================
# ENGLISH LEVEL SCORING
# =============================================================================

ENGLISH_LEVEL_SCORES = {
    "Advanced": 10,
    "Intermediate": 7,
    "Basic": 4,
    "Not stated": 5,  # Neutral - no penalty, no bonus
}

# =============================================================================
# EXPERIENCE SCORING (Years -> Score mapping)
# =============================================================================

def score_experience_years(years) -> int:
    """Convert years of experience to a 0-10 score.
    
    Job requirement: 0-3 years (Junior-Mid level)
    Sweet spot is 1-3 years. Very senior may be overqualified.
    """
    if years == "Not stated" or years is None:
        return 5  # Neutral
    try:
        years = float(years)
    except (ValueError, TypeError):
        return 5
    
    # Junior-Mid focus (0-3yr sweet spot per job requirements)
    if 1 <= years <= 3:
        return 10  # Perfect match for role
    elif 0.5 <= years < 1:
        return 8   # Entry-level, trainable
    elif 3 < years <= 5:
        return 8   # Still good fit
    elif years > 5:
        return 6   # May be overqualified for junior-mid role
    elif years < 0.5:
        return 5   # Very limited but acceptable


@dataclass
class EvaluationConfig:
    """Container for all evaluation configuration."""
    dimension_weights: Dict[str, float]
    score_bands: Dict[str, tuple]
    rejection_threshold: int
    required_tools: List[str]
    preferred_tools: List[str]
    animation_skills: List[str]
    collaboration_keywords: List[str]
    
    @classmethod
    def default(cls) -> "EvaluationConfig":
        return cls(
            dimension_weights=DIMENSION_WEIGHTS,
            score_bands=SCORE_BANDS,
            rejection_threshold=REJECTION_THRESHOLD,
            required_tools=REQUIRED_TOOLS,
            preferred_tools=PREFERRED_TOOLS,
            animation_skills=ANIMATION_SKILLS,
            collaboration_keywords=COLLABORATION_KEYWORDS,
        )
