#!/usr/bin/env python3
"""
HR Dashboard - Flask Web Application

Provides a web interface for viewing candidate evaluations
with AI-powered advice from Gemini.
"""

import os
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, jsonify, request

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.loader import load_candidates
from src.evaluator import evaluator
from src.gemini_advisor import GeminiAdvisor

app = Flask(__name__)

# Configuration
DATASET_PATH = PROJECT_ROOT / "clean_2d_animator_evaluation_dataset.csv"

# Global state
candidates = []
evaluation_results = {}
gemini = None


def init_app():
    """Initialize application state."""
    global candidates, evaluation_results, gemini
    
    print("Loading candidates...")
    candidates = load_candidates(DATASET_PATH)
    
    print(f"Evaluating {len(candidates)} candidates...")
    for candidate in candidates:
        result = evaluator.evaluate(candidate)
        # Use candidate's ID from the loader (CSV row index)
        evaluation_results[candidate.id] = {
            "candidate": candidate,
            "result": result,
        }
    
    print("Initializing Gemini advisor...")
    gemini = GeminiAdvisor()
    if gemini.is_available:
        print("Gemini AI: ENABLED")
    else:
        print("Gemini AI: DISABLED (no API key)")
    
    print(f"Ready! Loaded {len(candidates)} candidates.")


@app.route("/")
def dashboard():
    """Serve the main dashboard page."""
    return render_template("dashboard.html")


@app.route("/api/candidates")
def get_candidates():
    """Get all candidates with evaluation summaries."""
    results = []
    
    for cid, data in evaluation_results.items():
        result = data["result"]
        candidate = data["candidate"]
        
        results.append({
            "id": cid,
            "position": candidate.position,
            "english_level": candidate.english_level,
            "years_experience": candidate.years_experience,
            "final_score": round(result.final_score, 1),
            "band": result.band,
            "status": result.status,
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Calculate summary stats
    summary = {
        "total": len(results),
        "shortlisted": sum(1 for r in results if r["status"] == "Shortlisted"),
        "rejected": sum(1 for r in results if r["status"] == "Rejected"),
        "flagged": sum(1 for r in results if r["status"] == "Flagged for Review"),
        "avg_score": round(sum(r["final_score"] for r in results) / len(results), 1) if results else 0,
    }
    
    return jsonify({"candidates": results, "summary": summary})


@app.route("/api/candidates/<candidate_id>")
def get_candidate(candidate_id):
    """Get detailed evaluation for a single candidate."""
    if candidate_id not in evaluation_results:
        return jsonify({"error": "Candidate not found"}), 404
    
    data = evaluation_results[candidate_id]
    result = data["result"]
    candidate = data["candidate"]
    
    # Truncate CV text for display but keep reasonable length
    cv_preview = candidate.cv_text
    if len(cv_preview) > 800:
        cv_preview = cv_preview[:800] + "..."
    
    return jsonify({
        "id": candidate_id,
        "candidate": {
            "position": candidate.position,
            "english_level": candidate.english_level,
            "years_experience": candidate.years_experience,
            "cv_text": cv_preview,
            "highlights": candidate.highlights,
            "looking_for": candidate.looking_for,
            "additional_info": candidate.additional_info[:500] if len(candidate.additional_info) > 500 else candidate.additional_info,
        },
        "evaluation": result.to_dict(),
    })


@app.route("/api/advice/<candidate_id>", methods=["POST"])
def get_advice(candidate_id):
    """Generate AI advice for a candidate."""
    if candidate_id not in evaluation_results:
        return jsonify({"error": "Candidate not found"}), 404
    
    if not gemini or not gemini.is_available:
        return jsonify({
            "error": "Gemini API not configured",
            "advice": {
                "interview_focus": ["Configure GEMINI_API_KEY to enable"],
                "skill_gaps": [],
                "hiring_confidence": "N/A",
                "next_steps": "Add your Gemini API key to .env file",
            }
        })
    
    result = evaluation_results[candidate_id]["result"]
    advice = gemini.generate_advice(result.to_dict())
    
    return jsonify({"advice": advice})


if __name__ == "__main__":
    init_app()
    print("\n" + "=" * 50)
    print("HR Dashboard running at: http://localhost:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, port=5000)
