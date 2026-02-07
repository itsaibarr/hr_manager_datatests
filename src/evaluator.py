# Core HR Evaluator - Rule-based candidate scoring

import re
from typing import List, Dict, Tuple

from config.evaluation_criteria import (
    DIMENSION_WEIGHTS,
    REJECTION_THRESHOLD,
    CORE_COMPETENCY_ZERO_REJECT,
    get_score_band,
    score_experience_years,
    ENGLISH_LEVEL_SCORES,
    REQUIRED_TOOLS,
    PREFERRED_TOOLS,
    ANIMATION_SKILLS,
    DOMAIN_EXPERIENCE,
    COLLABORATION_KEYWORDS,
)
from .candidate import CandidateProfile, DimensionScore, EvaluationResult
from .bias_guard import bias_guard


class HREvaluator:
    """
    Rule-based HR Evaluator for 2D Animator candidates.
    
    Applies frozen evaluation criteria across 5 dimensions:
    - Core Competencies (35%)
    - Experience & Results (25%)
    - Collaboration Signals (20%)
    - Cultural & Practical Fit (15%)
    - Education & Other (5%)
    """
    
    def __init__(self):
        self.dimension_weights = DIMENSION_WEIGHTS
    
    def evaluate(self, candidate: CandidateProfile) -> EvaluationResult:
        """Evaluate a single candidate and return full result."""
        
        # Check for bias flags first
        is_flagged, bias_issues = bias_guard.check_candidate(
            candidate.cv_text, 
            candidate.additional_info
        )
        
        # Combine all text for analysis
        full_text = self._combine_text(candidate)
        
        # Score each dimension
        dimension_scores = {}
        
        # 1. Core Competencies (35%)
        core_score, core_evidence = self._score_core_competencies(full_text)
        dimension_scores["core_competencies"] = DimensionScore(
            name="Core Competencies",
            score=core_score,
            weight=self.dimension_weights["core_competencies"],
            evidence=core_evidence,
        )
        
        # 2. Experience & Results (25%)
        exp_score, exp_evidence = self._score_experience(candidate, full_text)
        dimension_scores["experience_results"] = DimensionScore(
            name="Experience & Results",
            score=exp_score,
            weight=self.dimension_weights["experience_results"],
            evidence=exp_evidence,
        )
        
        # 3. Collaboration Signals (20%)
        collab_score, collab_evidence = self._score_collaboration(full_text)
        dimension_scores["collaboration_signals"] = DimensionScore(
            name="Collaboration Signals",
            score=collab_score,
            weight=self.dimension_weights["collaboration_signals"],
            evidence=collab_evidence,
        )
        
        # 4. Cultural & Practical Fit (15%)
        fit_score, fit_evidence = self._score_cultural_fit(candidate, full_text)
        dimension_scores["cultural_practical_fit"] = DimensionScore(
            name="Cultural & Practical Fit",
            score=fit_score,
            weight=self.dimension_weights["cultural_practical_fit"],
            evidence=fit_evidence,
        )
        
        # 5. Education & Other (5%)
        edu_score, edu_evidence = self._score_education(full_text)
        dimension_scores["education_other"] = DimensionScore(
            name="Education & Other Signals",
            score=edu_score,
            weight=self.dimension_weights["education_other"],
            evidence=edu_evidence,
        )
        
        # Calculate final score
        final_score = sum(ds.weighted_score for ds in dimension_scores.values())
        band = get_score_band(final_score)
        
        # Determine status
        status, shortlist_reasons, concerns, rejection_reasons = self._determine_status(
            final_score, band, dimension_scores, core_score
        )
        
        # Override status if bias flagged
        if is_flagged:
            status = "Flagged for Review"
        
        return EvaluationResult(
            candidate_id=candidate.id,
            dimension_scores=dimension_scores,
            final_score=final_score,
            band=band,
            status=status,
            shortlist_reasons=shortlist_reasons,
            concerns=concerns,
            rejection_reasons=rejection_reasons,
            bias_flags=bias_issues,
        )
    
    def _combine_text(self, candidate: CandidateProfile) -> str:
        """Combine all candidate text fields for analysis."""
        parts = [
            candidate.cv_text,
            candidate.highlights if candidate.highlights != "Not stated" else "",
            candidate.additional_info if candidate.additional_info else "",
        ]
        return " ".join(parts).lower()
    
    def _score_core_competencies(self, text: str) -> Tuple[float, List[str]]:
        """
        Score technical alignment with role requirements.
        Per job requirements: Must have experience with at least ONE 2D animation tool.
        """
        evidence = []
        score = 0.0
        
        # Check for any required tool (any one qualifies per job requirements)
        required_found = []
        for tool in REQUIRED_TOOLS:
            if tool in text:
                required_found.append(tool)
        
        if required_found:
            score += 4.0  # Has at least one required tool
            unique_tools = list(set(required_found))[:3]
            evidence.append(f"Required tool: {', '.join(unique_tools)}")
        
        # Check preferred/additional tools
        preferred_found = []
        for tool in PREFERRED_TOOLS:
            if tool in text:
                preferred_found.append(tool)
        
        if preferred_found:
            tool_score = min(2.0, len(preferred_found) * 0.5)
            score += tool_score
            unique_preferred = list(set(preferred_found))[:3]
            evidence.append(f"Additional tools: {', '.join(unique_preferred)}")
        
        # Check animation skills (understanding of 2D animation principles)
        skills_found = []
        for skill in ANIMATION_SKILLS:
            if skill in text:
                skills_found.append(skill)
        
        if skills_found:
            skill_score = min(4.0, len(skills_found) * 0.6)
            score += skill_score
            unique_skills = list(set(skills_found))[:4]
            evidence.append(f"Animation skills: {', '.join(unique_skills)}")
        
        # Cap at 10
        score = min(10.0, score)
        
        if not evidence:
            evidence.append("Limited technical signals detected")
        
        return score, evidence
    
    def _score_experience(self, candidate: CandidateProfile, text: str) -> Tuple[float, List[str]]:
        """
        Score practical experience and ownership.
        Uses years + evidence of project work.
        """
        evidence = []
        
        # Base score from years
        years_score = score_experience_years(candidate.years_experience)
        
        if candidate.years_experience != "Not stated":
            evidence.append(f"Experience: {candidate.years_experience} years")
        
        # Look for project evidence
        project_indicators = [
            "project", "released", "launched", "shipped",
            "created", "developed", "built", "worked on",
            "portfolio", "freelance", "client",
        ]
        
        project_count = sum(1 for ind in project_indicators if ind in text)
        if project_count >= 3:
            years_score = min(10, years_score + 1)
            evidence.append("Multiple project references found")
        
        # Look for domain experience
        domain_found = []
        for domain in DOMAIN_EXPERIENCE:
            if domain in text:
                domain_found.append(domain)
        
        if domain_found:
            years_score = min(10, years_score + 0.5)
            evidence.append(f"Domain: {', '.join(domain_found[:3])}")
        
        if not evidence:
            evidence.append("Experience details not clearly stated")
        
        return min(10.0, years_score), evidence
    
    def _score_collaboration(self, text: str) -> Tuple[float, List[str]]:
        """
        Score collaboration signals (weakly observable).
        Looks for team work, tools, feedback mentions.
        """
        evidence = []
        score = 5.0  # Neutral baseline since this is weakly observable
        
        collab_found = []
        for keyword in COLLABORATION_KEYWORDS:
            if keyword in text:
                collab_found.append(keyword)
        
        if collab_found:
            boost = min(3.0, len(collab_found) * 0.4)
            score += boost
            evidence.append(f"Collaboration signals: {', '.join(collab_found[:4])}")
        
        # Look for specific team context
        team_patterns = [
            r"team of \d+",
            r"worked with",
            r"collaborated",
            r"mentored",
            r"supervised",
        ]
        
        for pattern in team_patterns:
            if re.search(pattern, text):
                score = min(10, score + 0.5)
                evidence.append("Direct team experience mentioned")
                break
        
        if not evidence:
            evidence.append("Limited collaboration signals (common for individual contributors)")
        
        return min(10.0, score), evidence
    
    def _score_cultural_fit(self, candidate: CandidateProfile, text: str) -> Tuple[float, List[str]]:
        """
        Score operational compatibility (not personality).
        Looks for: role alignment, availability signals, work preferences.
        """
        evidence = []
        score = 6.0  # Neutral-positive baseline
        
        # Check English level
        english_score = ENGLISH_LEVEL_SCORES.get(candidate.english_level, 5)
        if candidate.english_level != "Not stated":
            evidence.append(f"English: {candidate.english_level}")
            score += (english_score - 5) * 0.3  # Adjust based on English
        
        # Look for remote/flexible work mentions (positive for modern roles)
        remote_keywords = ["remote", "flexible", "work from home", "wfh"]
        if any(kw in text for kw in remote_keywords):
            score = min(10, score + 0.5)
            evidence.append("Remote work experience/preference")
        
        # Look for deadline/pressure handling
        if any(word in text for word in ["deadline", "pressure", "fast-paced"]):
            score = min(10, score + 0.5)
            evidence.append("Deadline awareness mentioned")
        
        # Check "looking for" field for alignment
        if candidate.looking_for != "Not stated":
            evidence.append("Stated job preferences available")
        
        if not evidence:
            evidence.append("Standard fit indicators")
        
        return min(10.0, score), evidence
    
    def _score_education(self, text: str) -> Tuple[float, List[str]]:
        """
        Score education signals (low weight by design).
        Looks for: degrees, courses, certifications.
        """
        evidence = []
        score = 5.0  # Neutral baseline
        
        # Education keywords
        edu_keywords = [
            "degree", "bachelor", "master", "university", "college",
            "course", "certificate", "certification", "diploma",
            "school", "academy", "bootcamp",
        ]
        
        edu_found = []
        for kw in edu_keywords:
            if kw in text:
                edu_found.append(kw)
        
        if edu_found:
            boost = min(3.0, len(edu_found) * 0.5)
            score += boost
            evidence.append(f"Education signals: {', '.join(list(set(edu_found))[:3])}")
        
        # Look for specific animation education
        if any(word in text for word in ["animation course", "artcraft", "motion academy"]):
            score = min(10, score + 1)
            evidence.append("Relevant animation training")
        
        if not evidence:
            evidence.append("No formal education stated (not penalized)")
        
        return min(10.0, score), evidence
    
    def _determine_status(
        self,
        final_score: float,
        band: str,
        dimension_scores: Dict[str, DimensionScore],
        core_score: float,
    ) -> Tuple[str, List[str], List[str], List[str]]:
        """
        Determine candidate status and generate reasoning.
        """
        shortlist_reasons = []
        concerns = []
        rejection_reasons = []
        
        # Check for immediate rejection (zero core competencies)
        if CORE_COMPETENCY_ZERO_REJECT and core_score == 0:
            return (
                "Rejected",
                [],
                [],
                ["Core competencies do not match required role stack (no relevant tools detected)"],
            )
        
        # Check threshold rejection
        if final_score < REJECTION_THRESHOLD:
            rejection_reasons.append(f"Score {final_score:.1f} below threshold ({REJECTION_THRESHOLD})")
            
            # Add specific weak areas
            for name, ds in dimension_scores.items():
                if ds.score < 4:
                    rejection_reasons.append(f"Weak {ds.name}: {ds.score:.1f}/10")
            
            return ("Rejected", [], [], rejection_reasons)
        
        # Generate shortlist reasons for passing candidates
        status = "Shortlisted"
        
        # Top strengths
        sorted_dims = sorted(
            dimension_scores.items(),
            key=lambda x: x[1].score,
            reverse=True
        )
        
        for name, ds in sorted_dims[:3]:
            if ds.score >= 6:
                reason = f"{ds.name} ({int(ds.weight*100)}%): "
                if ds.evidence:
                    reason += ds.evidence[0]
                shortlist_reasons.append(reason)
        
        # Identify concerns
        for name, ds in dimension_scores.items():
            if ds.score < 5:
                concern = f"Limited {ds.name.lower()} signals"
                concerns.append(concern)
        
        return (status, shortlist_reasons, concerns, [])
    
    def evaluate_batch(self, candidates: List[CandidateProfile]) -> List[EvaluationResult]:
        """Evaluate multiple candidates."""
        return [self.evaluate(c) for c in candidates]


# Singleton instance
evaluator = HREvaluator()
