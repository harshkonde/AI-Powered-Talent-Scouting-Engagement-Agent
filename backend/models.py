"""
models.py — Pydantic models for request/response validation.

Defines the data shapes used by the API:
- JobDescriptionRequest: incoming JD text from the frontend
- ParsedJD: structured output after parsing a JD
- Candidate: a single candidate profile (matches candidates.json schema)
"""

from pydantic import BaseModel, Field
from typing import List


# ─── Request Model ───────────────────────────────────────────────────────────
# This is what the frontend sends when submitting a Job Description.

class JobDescriptionRequest(BaseModel):
    """Payload for POST /analyze-jd and POST /match endpoints."""
    jd_text: str = Field(
        ...,
        min_length=10,
        description="Raw job description text to analyze"
    )


# ─── Parsed JD Response ─────────────────────────────────────────────────────
# Structured data extracted from a raw JD by the parser.

class ParsedJD(BaseModel):
    """Output of the JD parsing step."""
    job_title: str = ""
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    min_experience: int = 0
    max_experience: int = 99
    location: str = ""


# ─── Candidate Model ────────────────────────────────────────────────────────
# Matches the schema in data/candidates.json exactly.

class Candidate(BaseModel):
    """A single candidate profile from the dataset."""
    name: str
    skills: List[str]
    experience: int
    projects: List[str]
    location: str
