# AI HR Screening Agent (MVP)

An AI-powered, rule-driven HR screening system that evaluates candidates transparently and consistently using explicit hiring logic — without model training or opaque decision-making.

This project demonstrates how AI can **scale human hiring judgment**, not replace it.

---

## 🚩 Problem

HR managers spend ~20–25 hours per week manually reviewing CVs.  
This work is repetitive, attention-heavy, and inconsistent, yet still requires fairness and accountability.

Existing tools either:
- rely on keyword filtering, or
- use black-box AI decisions that are hard to trust or explain.

---

## 💡 Solution

This project implements an **AI HR Screening Agent** that:

- Applies a **fixed, human-defined evaluation framework**
- Scores candidates across transparent dimensions
- Produces **structured explanations** for every decision
- Separates **data preparation** from **candidate evaluation**
- Avoids training or fine-tuning to reduce bias and increase interpretability

The AI does not decide *what matters* — humans do.

---

## 🧠 Core Design Principles

- **Rule-driven, not model-driven**
- **Explainability over optimization**
- **Consistency over creativity**
- **Human-in-the-loop by design**

---

## 🏗️ System Architecture

Raw Candidate Dataset
↓
Dataset Cleaning & Normalization
↓
Dataset Preparation Agent
↓
Evaluation Agent (Rule-Based)
↓
Scores + Explanations


No training. No fine-tuning. Full transparency.

---

## 📊 Evaluation Framework (Summary)

Candidates are evaluated on:

- **Core Competencies (35%)**
- **Experience & Results (25%)**
- **Collaboration Signals (20%)**
- **Cultural & Practical Fit (15%)**
- **Education & Other Signals (5%)**

Each dimension is scored independently and combined into a final score band:
- Strong Fit
- Good Fit
- Borderline
- Reject

---

## 🛡️ Bias & Safety

The system explicitly ignores:
- age, gender, race, ethnicity, religion
- nationality (unless related to work eligibility)
- photos or personal identifiers

Protected attributes are never scored or referenced.

---

## 🚀 How to Run

1. Open `sample.ipynb`
2. Run cells top-to-bottom
3. Review normalized candidate profiles
4. Review evaluation outputs and explanations

---

## 🎯 MVP Scope

This MVP focuses on **one role** (2D Animator) to prove depth over breadth.

Future extensions:
- additional roles
- interview question generation
- human feedback loops
- weight optimization using real outcomes

---

## 🏁 Status

✅ MVP complete  
✅ Dataset validated  
✅ Evaluation logic frozen  
✅ Demo-ready

---

## 👤 Author

Built as part of a startup MVP for **Infomatrix Asia 2026 — Startup Discipline**.