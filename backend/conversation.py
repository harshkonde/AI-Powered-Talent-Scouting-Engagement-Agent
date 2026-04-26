"""
conversation.py — Simulated Candidate Conversation & Interest Scoring

Simulates a rule-based conversation between an AI recruiter and a candidate.
No external API needed — uses match score + candidate profile to determine response.

INTEREST LEVELS & SCORE RANGES:
    - Interested      → 80–100 (candidate is excited and wants to proceed)
    - Neutral          → 40–70  (candidate is open but not fully convinced)
    - Not Interested   → 0–30   (candidate declines the opportunity)

DECISION LOGIC:
    The candidate's interest is determined by their match score:
    - High match score (≥ 60%)   → likely "Interested"
    - Medium match score (35-59%) → likely "Neutral"
    - Low match score (< 35%)    → likely "Not Interested"

    Additional factors that can boost interest:
    - Candidate's location matches JD location
    - Candidate has very relevant project experience
"""

import random
import hashlib
from typing import Dict, List


# ═════════════════════════════════════════════════════════════════════════════
# SIMULATED CONVERSATION TEMPLATES
# ═════════════════════════════════════════════════════════════════════════════
# Each interest level has a set of realistic recruiter messages and
# candidate responses to create a natural-feeling conversation thread.

# Recruiter opening messages (same for all candidates)
RECRUITER_MESSAGES = [
    "Hi {name}, I found your profile very interesting! We have a {title} role that seems like a great match for your skills in {skill}. Would you be open to discussing this opportunity?",
    "Hello {name}! I'm reaching out about an exciting {title} position. Your experience with {skill} really stood out to us. Can we chat?",
    "Hey {name}, hope you're doing well! We're hiring for a {title} role and your background looks like a strong fit. Interested in learning more?",
]

# Candidate responses based on interest level
INTERESTED_RESPONSES = [
    "Thanks for reaching out! I'm definitely interested. The role sounds like a great fit for my skills. I'd love to schedule a call to learn more about the team and projects.",
    "Hi! This sounds exciting — I've been looking for exactly this kind of opportunity. I'm available for a discussion this week. Let's connect!",
    "Absolutely! I've been wanting to work on something like this. My experience in {skill} would be very relevant here. When can we talk?",
]

NEUTRAL_RESPONSES = [
    "Thanks for the message. I'm not actively looking right now, but I'm open to hearing more. Could you share details about the compensation and work culture?",
    "Interesting opportunity. I'd need to know more before committing — what's the tech stack and team size? I might consider it if the fit is right.",
    "I appreciate you reaching out. I'm somewhat interested but would need more information about growth opportunities before making a decision.",
]

NOT_INTERESTED_RESPONSES = [
    "Thank you for thinking of me, but I'm happy in my current role and not looking for a change at this time. Best of luck with the search!",
    "I appreciate the offer, but this doesn't align with my current career goals. I'll pass for now, but feel free to reach out in the future.",
    "Thanks, but I recently committed to a new project and won't be available. Wishing you the best in finding the right candidate!",
]


# ═════════════════════════════════════════════════════════════════════════════
# INTEREST LEVEL DETERMINATION
# ═════════════════════════════════════════════════════════════════════════════

def determine_interest_level(match_score: float, candidate: Dict, jd_location: str = "") -> str:
    """
    Determine if a candidate would be interested, neutral, or not interested.

    Logic:
    1. Start with match_score as the primary factor:
       - match_score >= 60  → Interested
       - match_score 35-59  → Neutral
       - match_score < 35   → Not Interested

    2. Apply bonus modifiers:
       - Location match gives +1 level boost (Neutral → Interested)
       - Very low skill overlap keeps level low regardless

    Args:
        match_score: The calculated match score (0-100) from matcher.py
        candidate: Candidate dict with name, skills, experience, projects, location
        jd_location: Location mentioned in the JD (optional)

    Returns:
        One of: "Interested", "Neutral", "Not Interested"
    """
    # Primary decision based on match score
    if match_score >= 60:
        level = "Interested"
    elif match_score >= 35:
        level = "Neutral"
    else:
        level = "Not Interested"

    # Bonus: If candidate's location matches JD location, bump up one level
    # (People are more interested when they don't have to relocate)
    if jd_location:
        candidate_loc = candidate.get("location", "").lower()
        jd_loc = jd_location.lower()
        if jd_loc in candidate_loc or candidate_loc in jd_loc:
            if level == "Neutral":
                level = "Interested"
            elif level == "Not Interested":
                level = "Neutral"

    return level


# ═════════════════════════════════════════════════════════════════════════════
# INTEREST SCORE CALCULATION
# ═════════════════════════════════════════════════════════════════════════════

def calculate_interest_score(interest_level: str, candidate_name: str) -> int:
    """
    Assign a numerical Interest Score based on the interest level.

    Ranges (as specified):
        - Interested      → random score between 80 and 100
        - Neutral          → random score between 40 and 70
        - Not Interested   → random score between 0 and 30

    We use a seeded random based on the candidate name so the same
    candidate always gets the same score (deterministic/reproducible).

    Args:
        interest_level: "Interested", "Neutral", or "Not Interested"
        candidate_name: Used as seed for reproducible randomness

    Returns:
        Integer score from 0 to 100
    """
    # Create a deterministic random generator using candidate name as seed
    # This ensures the same candidate always gets the same score
    seed = int(hashlib.md5(candidate_name.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    # Pick a random score within the defined range for each level
    if interest_level == "Interested":
        return rng.randint(80, 100)
    elif interest_level == "Neutral":
        return rng.randint(40, 70)
    else:  # Not Interested
        return rng.randint(0, 30)


# ═════════════════════════════════════════════════════════════════════════════
# CONVERSATION SIMULATION
# ═════════════════════════════════════════════════════════════════════════════

def simulate_conversation(candidate: Dict, match_score: float,
                          jd_title: str = "Software Engineer",
                          jd_skills: List[str] = None,
                          jd_location: str = "") -> Dict:
    """
    Simulate a recruiter-candidate conversation and assign an Interest Score.

    Steps:
    1. Determine interest level from match score + profile factors
    2. Calculate numerical interest score (within the level's range)
    3. Generate a realistic conversation thread (recruiter + candidate messages)

    Args:
        candidate: Candidate dict (name, skills, experience, projects, location)
        match_score: The match score calculated by matcher.py (0-100)
        jd_title: Job title extracted from the JD
        jd_skills: Skills extracted from the JD
        jd_location: Location mentioned in the JD

    Returns:
        Dict with:
            - interest_level: "Interested" / "Neutral" / "Not Interested"
            - interest_score: 0-100
            - conversation: list of {role, message} dicts
    """
    if jd_skills is None:
        jd_skills = []

    # Step 1: Determine interest level
    interest_level = determine_interest_level(match_score, candidate, jd_location)

    # Step 2: Calculate interest score within the appropriate range
    interest_score = calculate_interest_score(interest_level, candidate["name"])

    # Step 3: Generate conversation thread
    # Use deterministic random so conversations are consistent
    seed = int(hashlib.md5(candidate["name"].encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    # Pick a top skill to mention in the conversation
    top_skill = candidate["skills"][0] if candidate["skills"] else "your domain"

    # Template variables for message formatting
    template_vars = {
        "name": candidate["name"].split()[0],  # First name only
        "title": jd_title,
        "skill": top_skill,
    }

    # Build the conversation: recruiter opens, candidate responds
    conversation = []

    # Message 1: Recruiter reaches out
    recruiter_msg = rng.choice(RECRUITER_MESSAGES).format(**template_vars)
    conversation.append({
        "role": "Recruiter",
        "message": recruiter_msg
    })

    # Message 2: Candidate responds based on their interest level
    if interest_level == "Interested":
        candidate_msg = rng.choice(INTERESTED_RESPONSES).format(**template_vars)
    elif interest_level == "Neutral":
        candidate_msg = rng.choice(NEUTRAL_RESPONSES).format(**template_vars)
    else:
        candidate_msg = rng.choice(NOT_INTERESTED_RESPONSES).format(**template_vars)

    conversation.append({
        "role": "Candidate",
        "message": candidate_msg
    })

    # Return the complete simulation result
    return {
        "interest_level": interest_level,
        "interest_score": interest_score,
        "conversation": conversation,
    }
