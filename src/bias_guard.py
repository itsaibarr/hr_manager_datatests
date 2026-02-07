# Bias detection and protected attribute filtering

import re
from typing import List, Tuple

from config.evaluation_criteria import PROTECTED_ATTRIBUTES, DEMOGRAPHIC_PATTERNS


class BiasGuard:
    """Detects and flags protected attributes in candidate data."""
    
    def __init__(self):
        self.protected_attributes = PROTECTED_ATTRIBUTES
        self.demographic_patterns = [re.compile(p, re.IGNORECASE) for p in DEMOGRAPHIC_PATTERNS]
    
    def scan_text(self, text: str) -> List[str]:
        """
        Scan text for protected attribute references.
        Returns list of detected issues.
        """
        issues = []
        text_lower = text.lower()
        
        # Check for demographic patterns
        for pattern in self.demographic_patterns:
            matches = pattern.findall(text)
            if matches:
                issues.append(f"Potential demographic data detected: pattern match")
        
        # Check for explicit protected attribute mentions (in context that suggests personal data)
        # Note: We look for patterns that suggest self-identification, not general mentions
        personal_patterns = [
            r"\bi am\s+(a\s+)?(male|female|man|woman)\b",
            r"\bmy (age|gender|religion|ethnicity)\b",
            r"\b(i('m| am)\s+)?\d{2}\s*years?\s*old\b",
        ]
        
        for pattern in personal_patterns:
            if re.search(pattern, text_lower):
                issues.append(f"Personal demographic statement detected")
        
        return issues
    
    def check_candidate(self, cv_text: str, additional_info: str = "") -> Tuple[bool, List[str]]:
        """
        Check a candidate's data for protected attributes.
        
        Returns:
            Tuple of (is_flagged, list_of_issues)
        """
        combined_text = f"{cv_text} {additional_info}"
        issues = self.scan_text(combined_text)
        
        # Remove duplicates
        issues = list(set(issues))
        
        return (len(issues) > 0, issues)
    
    def get_safety_output(self, candidate_id: str, issues: List[str]) -> dict:
        """Generate safety output for flagged candidates."""
        return {
            "candidate_id": candidate_id,
            "status": "Flagged for Review",
            "issue": "Non-job-related personal data detected and excluded from evaluation.",
            "details": issues,
            "action": "Human review recommended to ensure fair evaluation.",
        }


# Singleton instance
bias_guard = BiasGuard()
