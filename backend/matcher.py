"""
matcher.py — Match Score Calculator

Calculates how well a candidate matches a given Job Description (JD).

SCORING FORMULA:
    Match Score = (skill_score * 0.5) + (experience_score * 0.3) + (project_score * 0.2)

Components:
    1. Skill Match (50% weight)   → % of JD skills found in candidate's skill set
    2. Experience Match (30%)     → How close candidate's experience is to the required years
    3. Project Relevance (20%)    → Keyword overlap between JD and candidate's project descriptions

All individual scores are 0–100, so the final Match Score is also 0–100%.
"""

import json
import os
from typing import List, Dict


# ── Path to candidate dataset ────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "candidates.json")


def load_candidates() -> List[Dict]:
    """Load all candidate profiles from the JSON file."""
    with open(DATA_PATH, "r") as f:
        return json.load(f)


# ═════════════════════════════════════════════════════════════════════════════
# 1. SKILL MATCH (Weight: 50%)
# ═════════════════════════════════════════════════════════════════════════════
# Logic:
#   - Compare JD required skills against the candidate's skills
#   - Both sides are lowercased for case-insensitive matching
#   - Score = (number of matching skills / total JD skills) * 100
#   - Example: JD wants [Python, Django, AWS], candidate has [Python, AWS]
#              → 2 out of 3 match → skill_score = 66.7%

def calculate_skill_score(jd_skills: List[str], candidate_skills: List[str]) -> float:
    """
    Calculate percentage of JD skills that the candidate possesses.

    Args:
        jd_skills: List of skills extracted from the Job Description
        candidate_skills: List of skills from the candidate's profile

    Returns:
        Score from 0 to 100 representing skill overlap percentage
    """
    if not jd_skills:
        return 0.0  # No skills in JD → can't calculate

    # Normalize to lowercase for fair comparison
    jd_set = set(skill.lower().strip() for skill in jd_skills)
    candidate_set = set(skill.lower().strip() for skill in candidate_skills)

    # Count how many JD skills the candidate has
    matched = jd_set.intersection(candidate_set)

    # Score = (matched / total required) * 100
    score = (len(matched) / len(jd_set)) * 100

    return round(score, 2)


# ═════════════════════════════════════════════════════════════════════════════
# 2. EXPERIENCE MATCH (Weight: 30%)
# ═════════════════════════════════════════════════════════════════════════════
# Logic:
#   - The closer the candidate's experience to the required years, the higher the score
#   - If experience matches exactly → 100%
#   - For every year of difference, we deduct points
#   - Deduction formula: score = max(0, 100 - |difference| * 15)
#     This means ±1 year = 85, ±2 years = 70, ±3 years = 55, etc.
#   - Both under-experienced and over-experienced candidates lose points,
#     but being close still earns a decent score

def calculate_experience_score(required_exp: int, candidate_exp: int) -> float:
    """
    Calculate how closely the candidate's experience matches the requirement.

    Args:
        required_exp: Years of experience mentioned in the JD
        candidate_exp: Years of experience the candidate has

    Returns:
        Score from 0 to 100 — higher means closer match
    """
    # Calculate absolute difference in years
    difference = abs(required_exp - candidate_exp)

    # Deduct 15 points per year of difference, minimum score is 0
    # This gives a smooth curve: exact match=100, ±1yr=85, ±2yr=70, etc.
    score = max(0, 100 - difference * 15)

    return round(score, 2)


# ═════════════════════════════════════════════════════════════════════════════
# 3. PROJECT RELEVANCE (Weight: 20%)
# ═════════════════════════════════════════════════════════════════════════════
# Logic:
#   - Extract meaningful keywords from the JD text (skip common stopwords)
#   - Combine all candidate project descriptions into one text block
#   - Count how many JD keywords appear in the candidate's projects
#   - Score = (matched keywords / total JD keywords) * 100
#   - This measures how relevant the candidate's past work is to the JD

# Common English stopwords to ignore when extracting keywords
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must",
    "and", "or", "but", "if", "for", "with", "on", "at", "to", "from",
    "in", "of", "by", "as", "into", "about", "between", "through",
    "we", "you", "our", "your", "this", "that", "it", "its",
    "not", "no", "so", "up", "out", "all", "also", "very", "just",
    "more", "most", "than", "then", "such", "what", "which", "who",
    "how", "when", "where", "why", "each", "every", "any", "both",
    "looking", "experience", "years", "role", "work", "working",
    "team", "join", "able", "using", "required", "etc", "good",
    "strong", "knowledge", "understanding", "building", "develop",
}


def extract_keywords(text: str) -> set:
    """
    Extract meaningful keywords from text by:
    1. Lowercasing everything
    2. Splitting into words
    3. Keeping only words with 3+ characters
    4. Removing common stopwords
    """
    words = text.lower().split()
    # Clean punctuation from each word
    cleaned = set()
    for word in words:
        w = word.strip(".,;:!?()-/\"'")
        if len(w) >= 3 and w not in STOPWORDS:
            cleaned.add(w)
    return cleaned


def calculate_project_score(jd_text: str, candidate_projects: List[str]) -> float:
    """
    Calculate how relevant the candidate's projects are to the JD.

    Args:
        jd_text: The full job description text
        candidate_projects: List of project description strings

    Returns:
        Score from 0 to 100 — higher means projects are more relevant
    """
    # Extract keywords from the JD
    jd_keywords = extract_keywords(jd_text)

    if not jd_keywords:
        return 0.0  # No meaningful keywords in JD

    # Combine all project descriptions into one text block
    projects_text = " ".join(candidate_projects).lower()

    # Count how many JD keywords appear in the projects
    matched = sum(1 for keyword in jd_keywords if keyword in projects_text)

    # Score = (matched / total keywords) * 100
    score = (matched / len(jd_keywords)) * 100

    # Cap at 100 (shouldn't exceed, but safety check)
    return round(min(score, 100), 2)


# ═════════════════════════════════════════════════════════════════════════════
# FINAL MATCH SCORE CALCULATOR
# ═════════════════════════════════════════════════════════════════════════════
# Formula:
#   Match Score = (skill_score × 0.5) + (experience_score × 0.3) + (project_score × 0.2)
#
# This weighting reflects real-world hiring priorities:
#   - Skills are the most critical factor (50%)
#   - Experience level matters significantly (30%)
#   - Relevant past projects add value (20%)

def calculate_match_score(jd_skills: List[str], jd_experience: int,
                          jd_text: str, candidate: Dict) -> Dict:
    """
    Calculate the overall Match Score for a single candidate against a JD.

    Args:
        jd_skills: List of skills extracted from the JD
        jd_experience: Required years of experience from the JD
        jd_text: Full JD text (used for project keyword matching)
        candidate: Candidate dict with keys: name, skills, experience, projects, location

    Returns:
        Dict with individual scores and the final weighted match score
    """
    # Step 1: Calculate each component score (all are 0-100)
    skill_score = calculate_skill_score(jd_skills, candidate["skills"])
    experience_score = calculate_experience_score(jd_experience, candidate["experience"])
    project_score = calculate_project_score(jd_text, candidate["projects"])

    # Step 2: Apply the weighted formula
    # Match Score = (skills × 0.5) + (experience × 0.3) + (projects × 0.2)
    match_score = (skill_score * 0.5) + (experience_score * 0.3) + (project_score * 0.2)
    match_score = round(match_score, 2)

    # Step 3: Return detailed breakdown so the frontend can display each component
    return {
        "candidate_name": candidate["name"],
        "candidate": candidate,
        "skill_score": skill_score,
        "experience_score": experience_score,
        "project_score": project_score,
        "match_score": match_score,  # Final score in percentage (0-100)
    }


def match_all_candidates(jd_skills: List[str], jd_experience: int,
                         jd_text: str) -> List[Dict]:
    """
    Match ALL candidates against the JD and return results sorted by match score.

    Args:
        jd_skills: Skills extracted from the JD
        jd_experience: Required experience from the JD
        jd_text: Full JD text for project relevance matching

    Returns:
        List of match result dicts, sorted by match_score descending (best first)
    """
    candidates = load_candidates()

    # Calculate match score for every candidate
    results = [
        calculate_match_score(jd_skills, jd_experience, jd_text, candidate)
        for candidate in candidates
    ]

    # Sort by match_score in descending order (highest score first)
    results.sort(key=lambda r: r["match_score"], reverse=True)

    return results
