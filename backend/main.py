"""
main.py — FastAPI Backend for AI Talent Scouting Agent

This is the entry point of the backend server.
It defines three API endpoints:

    1. POST /analyze-jd   → Parse a JD and extract skills + experience
    2. GET  /candidates    → Return full list of candidates from the dataset
    3. POST /match         → Full pipeline: parse JD → match → rank candidates

The server also serves the frontend static files (HTML/CSS/JS).
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import our modules
from models import JobDescriptionRequest
from jd_parser import parse_jd
from matcher import load_candidates
from ranker import rank_candidates


# ═════════════════════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="AI Talent Scouting Agent",
    description="Parse job descriptions, match candidates, and simulate engagement",
    version="1.0.0",
)

# Enable CORS so the frontend can call the API from any origin
# (Needed when frontend and backend run on different ports during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],           # Allow all HTTP methods
    allow_headers=["*"],           # Allow all headers
)

# Serve the frontend folder as static files
# This lets us access CSS/JS at /static/style.css, /static/script.js, etc.
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ═════════════════════════════════════════════════════════════════════════════
# SERVE FRONTEND
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def serve_frontend():
    """
    Serve the main HTML page when user visits http://localhost:8000/
    """
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Talent Scouting Agent API is running. Visit /docs for Swagger UI."}


# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINT 1: POST /analyze-jd
# ═════════════════════════════════════════════════════════════════════════════
# Purpose: Parse a raw Job Description and extract structured data
# Input:   { "jd_text": "We are looking for a Python developer with 5+ years..." }
# Output:  { "job_title": "...", "required_skills": [...], "min_experience": 5, ... }

@app.post("/analyze-jd")
async def analyze_jd(request: JobDescriptionRequest):
    """
    Parse a raw job description text and extract:
    - Job title
    - Required skills
    - Preferred skills
    - Experience range (min/max years)
    - Location
    """
    try:
        # Use the JD parser to extract structured data
        parsed = parse_jd(request.jd_text)

        return {
            "status": "success",
            "data": {
                "job_title": parsed.job_title,
                "required_skills": parsed.required_skills,
                "preferred_skills": parsed.preferred_skills,
                "min_experience": parsed.min_experience,
                "max_experience": parsed.max_experience,
                "location": parsed.location,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse JD: {str(e)}")


# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINT 2: GET /candidates
# ═════════════════════════════════════════════════════════════════════════════
# Purpose: Return all candidates from the JSON dataset
# Input:   None (GET request)
# Output:  { "total": 15, "candidates": [...] }

@app.get("/candidates")
async def get_candidates():
    """
    Return the full list of candidates from the dataset.
    Each candidate has: name, skills, experience, projects, location.
    """
    try:
        candidates = load_candidates()

        return {
            "status": "success",
            "total": len(candidates),
            "candidates": candidates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load candidates: {str(e)}")


# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINT 3: POST /match
# ═════════════════════════════════════════════════════════════════════════════
# Purpose: Full pipeline — parse JD, match candidates, simulate conversations, rank
# Input:   { "jd_text": "..." }
# Output:  { "parsed_jd": {...}, "ranked_candidates": [...], "summary": {...} }
#
# This is the main endpoint that the frontend calls. It:
#   1. Parses the JD to extract skills, experience, title, location
#   2. Calculates Match Score for each candidate (skills×0.5 + exp×0.3 + projects×0.2)
#   3. Simulates conversation to get Interest Score (80-100 / 40-70 / 0-30)
#   4. Calculates Final Score = (Match×0.7) + (Interest×0.3)
#   5. Sorts candidates by Final Score (highest first)
#   6. Generates explanation for each candidate (why matched, which skills)

@app.post("/match")
async def match_candidates(request: JobDescriptionRequest):
    """
    Full matching pipeline:
    Parse JD → Score candidates → Simulate conversations → Rank by Final Score.
    Returns ranked candidates with scores, explanations, and conversation threads.
    """
    try:
        # Step 1: Parse the job description
        parsed = parse_jd(request.jd_text)

        # Step 2-6: Run the full ranking pipeline
        # This calls matcher.py + conversation.py + ranker.py internally
        ranked = rank_candidates(
            jd_skills=parsed.required_skills + parsed.preferred_skills,
            jd_experience=parsed.min_experience,
            jd_text=request.jd_text,
            jd_title=parsed.job_title,
            jd_location=parsed.location,
        )

        # Build summary counts
        # Count candidates by interest level for quick stats
        summary = {
            "total_candidates": len(ranked),
            "interested": sum(1 for r in ranked if r["interest_level"] == "Interested"),
            "neutral": sum(1 for r in ranked if r["interest_level"] == "Neutral"),
            "not_interested": sum(1 for r in ranked if r["interest_level"] == "Not Interested"),
        }

        return {
            "status": "success",
            "parsed_jd": {
                "job_title": parsed.job_title,
                "required_skills": parsed.required_skills,
                "preferred_skills": parsed.preferred_skills,
                "min_experience": parsed.min_experience,
                "max_experience": parsed.max_experience,
                "location": parsed.location,
            },
            "ranked_candidates": ranked,
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")


# ═════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Simple health check to verify the server is running."""
    return {"status": "healthy", "service": "AI Talent Scouting Agent"}
