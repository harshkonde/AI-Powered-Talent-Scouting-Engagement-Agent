"""
ranker.py — Candidate Ranking Engine

Combines Match Score and Interest Score into a Final Score,
then ranks all candidates from best to worst fit.

FORMULA:
    Final Score = (Match Score × 0.7) + (Interest Score × 0.3)

This weighting means:
    - 70% weight on how well the candidate fits the JD (skills, experience, projects)
    - 30% weight on how interested the candidate is in the role

Each ranked candidate also gets a human-readable explanation of:
    - Why they matched (or didn't)
    - Which specific skills matched and which were missing
"""

from typing import List, Dict
from matcher import calculate_match_score, calculate_skill_score, load_candidates
from conversation import simulate_conversation


# ═════════════════════════════════════════════════════════════════════════════
# EXPLANATION GENERATOR
# ═════════════════════════════════════════════════════════════════════════════
# Produces a clear, human-readable explanation for each candidate's ranking.

def generate_explanation(candidate: Dict, jd_skills: List[str],
                         jd_experience: int, match_result: Dict,
                         interest_result: Dict) -> Dict:
    """
    Generate a detailed explanation for why a candidate was ranked this way.

    Includes:
    1. Matched skills — JD skills the candidate has
    2. Missing skills — JD skills the candidate lacks
    3. Experience comparison — candidate's years vs required years
    4. Reasoning summary — a plain-English paragraph explaining the match

    Args:
        candidate: The candidate dict (name, skills, experience, projects, location)
        jd_skills: Skills extracted from the JD
        jd_experience: Required experience from the JD
        match_result: Output from calculate_match_score()
        interest_result: Output from simulate_conversation()

    Returns:
        Dict with matched_skills, missing_skills, and a summary reason string
    """
    # ── Find matched and missing skills ──────────────────────────────────
    # Lowercase both sides for fair comparison
    jd_skills_lower = set(s.lower().strip() for s in jd_skills)
    candidate_skills_lower = set(s.lower().strip() for s in candidate["skills"])

    # Skills the candidate HAS that the JD WANTS
    matched_set = jd_skills_lower.intersection(candidate_skills_lower)

    # Map back to original casing for display
    # (so we show "Python" not "python")
    all_skills = jd_skills + candidate["skills"]
    case_map = {}
    for s in all_skills:
        case_map[s.lower().strip()] = s

    matched_skills = [case_map.get(s, s) for s in matched_set]
    missing_skills = [case_map.get(s, s) for s in (jd_skills_lower - matched_set)]

    # ── Experience comparison ────────────────────────────────────────────
    exp_diff = candidate["experience"] - jd_experience
    if exp_diff == 0:
        exp_note = f"has exactly {jd_experience} years of experience (perfect match)"
    elif exp_diff > 0:
        exp_note = f"has {candidate['experience']} years (more than the required {jd_experience} years)"
    else:
        exp_note = f"has {candidate['experience']} years (less than the required {jd_experience} years)"

    # ── Build the reason summary ─────────────────────────────────────────
    total_jd = len(jd_skills_lower)
    matched_count = len(matched_skills)

    # Skill match sentence
    if matched_count == total_jd:
        skill_reason = f"has all {total_jd} required skills"
    elif matched_count > 0:
        skill_reason = f"matches {matched_count} out of {total_jd} required skills ({', '.join(matched_skills)})"
    else:
        skill_reason = "does not match any of the required skills"

    # Interest sentence
    interest_level = interest_result["interest_level"]
    if interest_level == "Interested":
        interest_reason = "showed strong interest in the role"
    elif interest_level == "Neutral":
        interest_reason = "was open to discussion but not fully committed"
    else:
        interest_reason = "was not interested in this opportunity"

    # Combine into a full explanation paragraph
    reason = (
        f"{candidate['name']} {skill_reason}, "
        f"{exp_note}, and {interest_reason}."
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_comparison": exp_note,
        "reason": reason,
    }


# ═════════════════════════════════════════════════════════════════════════════
# FINAL SCORE CALCULATION
# ═════════════════════════════════════════════════════════════════════════════
# Formula: Final Score = (Match Score × 0.7) + (Interest Score × 0.3)

def calculate_final_score(match_score: float, interest_score: int) -> float:
    """
    Combine Match Score and Interest Score into one Final Score.

    Formula:
        Final Score = (Match Score × 0.7) + (Interest Score × 0.3)

    Args:
        match_score: 0-100 from matcher.py (skill + experience + project)
        interest_score: 0-100 from conversation.py (candidate's interest)

    Returns:
        Final score as a float, rounded to 2 decimal places (0-100)
    """
    final = (match_score * 0.7) + (interest_score * 0.3)
    return round(final, 2)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN RANKING FUNCTION
# ═════════════════════════════════════════════════════════════════════════════

def rank_candidates(jd_skills: List[str], jd_experience: int,
                    jd_text: str, jd_title: str = "Software Engineer",
                    jd_location: str = "") -> List[Dict]:
    """
    Full ranking pipeline:
    1. Load all candidates
    2. Calculate Match Score for each (from matcher.py)
    3. Simulate conversation & get Interest Score for each (from conversation.py)
    4. Calculate Final Score = (Match × 0.7) + (Interest × 0.3)
    5. Generate explanation for each candidate
    6. Sort by Final Score descending (best candidates first)

    Args:
        jd_skills: List of skills extracted from the JD
        jd_experience: Required years of experience
        jd_text: Full JD text (used for project keyword matching)
        jd_title: Job title from the JD (used in conversation simulation)
        jd_location: Location from the JD (affects interest level)

    Returns:
        List of ranked candidate dicts, each containing:
            - candidate info (name, skills, experience, projects, location)
            - match_score, interest_score, final_score
            - interest_level, conversation thread
            - explanation (matched_skills, missing_skills, reason)
    """
    candidates = load_candidates()
    ranked_results = []

    for candidate in candidates:
        # Step 1: Calculate Match Score (skills × 0.5 + experience × 0.3 + projects × 0.2)
        match_result = calculate_match_score(
            jd_skills, jd_experience, jd_text, candidate
        )

        # Step 2: Simulate conversation and get Interest Score
        interest_result = simulate_conversation(
            candidate=candidate,
            match_score=match_result["match_score"],
            jd_title=jd_title,
            jd_skills=jd_skills,
            jd_location=jd_location,
        )

        # Step 3: Calculate Final Score
        final_score = calculate_final_score(
            match_result["match_score"],
            interest_result["interest_score"]
        )

        # Step 4: Generate human-readable explanation
        explanation = generate_explanation(
            candidate, jd_skills, jd_experience,
            match_result, interest_result
        )

        # Combine everything into one result dict
        ranked_results.append({
            # Candidate info
            "name": candidate["name"],
            "skills": candidate["skills"],
            "experience": candidate["experience"],
            "projects": candidate["projects"],
            "location": candidate["location"],

            # Scores breakdown
            "skill_score": match_result["skill_score"],
            "experience_score": match_result["experience_score"],
            "project_score": match_result["project_score"],
            "match_score": match_result["match_score"],
            "interest_score": interest_result["interest_score"],
            "final_score": final_score,

            # Conversation & interest
            "interest_level": interest_result["interest_level"],
            "conversation": interest_result["conversation"],

            # Explanation
            "matched_skills": explanation["matched_skills"],
            "missing_skills": explanation["missing_skills"],
            "reason": explanation["reason"],
        })

    # Step 5: Sort by final_score, highest first
    ranked_results.sort(key=lambda r: r["final_score"], reverse=True)

    # Step 6: Add rank number (1 = best)
    for i, result in enumerate(ranked_results):
        result["rank"] = i + 1

    return ranked_results
