# Gemini AI Advisor for candidate recommendations

import os
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiAdvisor:
    """Generate AI-powered hiring advice using Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        self._initialized = False
        
        if self.api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                self._initialized = True
            except Exception as e:
                print(f"Gemini initialization failed: {e}")
    
    @property
    def is_available(self) -> bool:
        return self._initialized and self.model is not None
    
    def generate_advice(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate hiring advice for a candidate based on evaluation.
        
        Returns dict with:
        - interview_focus: Areas to probe in interview
        - skill_gaps: Identified gaps with recommendations
        - hiring_confidence: Overall assessment
        - next_steps: Recommended actions
        """
        if not self.is_available:
            return {
                "error": "Gemini API not configured",
                "interview_focus": [],
                "skill_gaps": [],
                "hiring_confidence": "N/A",
                "next_steps": "Configure GEMINI_API_KEY to enable AI advice",
            }
        
        # Build prompt from evaluation data
        prompt = self._build_prompt(evaluation_result)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            return {
                "error": str(e),
                "interview_focus": [],
                "skill_gaps": [],
                "hiring_confidence": "Error",
                "next_steps": f"API error: {e}",
            }
    
    def _build_prompt(self, result: Dict[str, Any]) -> str:
        """Build prompt for Gemini from evaluation result."""
        dims = result.get("dimension_scores", {})
        
        # Format dimension scores
        dim_text = []
        for name, data in dims.items():
            score = data.get("score", 0)
            evidence = data.get("evidence", [])
            dim_text.append(f"- {name}: {score}/10")
            for ev in evidence[:2]:
                dim_text.append(f"    • {ev}")
        
        prompt = f"""You are an HR advisor for a 2D Animator position. Analyze this candidate evaluation and provide actionable hiring advice.

## Candidate Evaluation

**Final Score:** {result.get('final_score', 0):.1f}/100 ({result.get('band', 'Unknown')})
**Status:** {result.get('status', 'Unknown')}

### Dimension Scores:
{chr(10).join(dim_text)}

### Shortlist Reasons:
{chr(10).join(f'- {r}' for r in result.get('shortlist_reasons', [])) or '- None'}

### Concerns:
{chr(10).join(f'- {c}' for c in result.get('concerns', [])) or '- None'}

### Rejection Reasons:
{chr(10).join(f'- {r}' for r in result.get('rejection_reasons', [])) or '- None'}

---

Provide your analysis in this exact JSON format:
{{
    "interview_focus": ["topic 1 to probe", "topic 2 to probe"],
    "skill_gaps": ["gap 1 with brief recommendation", "gap 2"],
    "hiring_confidence": "High/Medium/Low with one-sentence reason",
    "next_steps": "Clear recommended action"
}}

Focus on 2D animation specifics: Spine expertise, After Effects, game/mobile experience, rigging skills.
Be concise and actionable. Return ONLY valid JSON."""

        return prompt
    
    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured advice."""
        import json
        
        # Try to extract JSON from response
        try:
            # Clean up response - find JSON block
            text = text.strip()
            if text.startswith("```"):
                # Remove markdown code block
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "interview_focus": ["Unable to parse AI response"],
                "skill_gaps": [],
                "hiring_confidence": "Review manually",
                "next_steps": text[:200] if text else "No response",
            }


# Singleton instance
gemini_advisor = GeminiAdvisor()
