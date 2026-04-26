"""
jd_parser.py - Job Description parsing engine.
Uses keyword heuristics + regex to extract structured requirements from raw JD text.
"""

import re
from typing import List, Tuple
from models import ParsedJD

# Skill taxonomy the parser searches for (case-insensitive)
SKILL_TAXONOMY = [
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
    "Ruby", "PHP", "Swift", "Kotlin", "Dart", "Scala", "R",
    "Django", "Flask", "FastAPI", "Spring Boot", "Express.js", "Node.js",
    "React", "Angular", "Vue.js", "Next.js", "Svelte",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
    "Data Visualization", "Apache Spark", "Airflow", "ETL", "Data Modeling",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQL",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform",
    "Jenkins", "CI/CD", "Ansible", "Linux", "Monitoring",
    "AWS SageMaker", "AWS Glue", "MLOps",
    "REST APIs", "GraphQL", "Microservices", "System Design", "Kafka",
    "Selenium", "Cypress", "Jest", "API Testing", "Postman",
    "Flutter", "React Native", "Firebase",
    "Git", "JIRA", "Agile", "Scrum", "Figma", "UI/UX",
    "Cybersecurity", "OWASP", "Security", "Networking",
    "Leadership", "Celery", "Redux", "Bootstrap", "HTML", "CSS",
]

_SKILL_PATTERNS = [
    (skill, re.compile(r'\b' + re.escape(skill) + r'\b', re.IGNORECASE))
    for skill in SKILL_TAXONOMY
]

# Experience regex patterns
_EXP_RANGE  = re.compile(r'(\d{1,2})\s*[-\u2013to]+\s*(\d{1,2})\s*\+?\s*years?', re.I)
_EXP_PLUS   = re.compile(r'(\d{1,2})\s*\+\s*years?', re.I)
_EXP_MIN    = re.compile(r'(?:minimum|at\s*least|min)\s*(\d{1,2})\s*years?', re.I)
_EXP_SIMPLE = re.compile(r'(\d{1,2})\s*years?\s*(?:of\s+)?experience', re.I)


def _extract_experience(text: str) -> Tuple[int, int]:
    """Return (min_exp, max_exp) from JD text."""
    m = _EXP_RANGE.search(text)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = _EXP_PLUS.search(text)
    if m:
        return int(m.group(1)), 99
    m = _EXP_MIN.search(text)
    if m:
        return int(m.group(1)), 99
    m = _EXP_SIMPLE.search(text)
    if m:
        yrs = int(m.group(1))
        return max(0, yrs - 1), yrs + 2
    return 0, 99


# Title extraction
_TITLE_PATTERNS = [
    re.compile(r'(?:job\s*title|position|role)\s*[:–-]\s*(.+)', re.I),
    re.compile(r'^(?:we\s+are\s+(?:looking|hiring)\s+(?:for\s+)?(?:a|an)\s+)(.+?)(?:\.|$)', re.I | re.M),
]

_COMMON_TITLES = [
    "Tech Lead", "Engineering Manager", "Senior Software Engineer",
    "Software Engineer", "Software Developer", "Backend Developer",
    "Frontend Developer", "Full Stack Developer", "Data Scientist",
    "Data Engineer", "ML Engineer", "DevOps Engineer", "Cloud Architect",
    "QA Engineer", "Mobile Developer", "Product Engineer", "Security Engineer",
]


def _extract_title(text: str) -> str:
    for pat in _TITLE_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip().rstrip('.')
    lower = text.lower()
    for title in _COMMON_TITLES:
        if title.lower() in lower:
            return title
    return "Software Engineer"


# Skill classification (required vs preferred)
_PREFERRED_MARKERS = re.compile(
    r'nice\s*to\s*have|preferred|bonus|good\s*to\s*have|plus|desirable', re.I
)


def _extract_skills(text: str) -> Tuple[List[str], List[str]]:
    """Return (required_skills, preferred_skills)."""
    required, preferred = [], []
    sentences = re.split(r'[.\n]', text)
    preferred_set = set()
    for sentence in sentences:
        if _PREFERRED_MARKERS.search(sentence):
            for skill, pat in _SKILL_PATTERNS:
                if pat.search(sentence):
                    preferred_set.add(skill)
    seen = set()
    for skill, pat in _SKILL_PATTERNS:
        if pat.search(text) and skill not in seen:
            seen.add(skill)
            if skill in preferred_set:
                preferred.append(skill)
            else:
                required.append(skill)
    return required, preferred


# Location extraction
_LOCATION_PAT = re.compile(
    r'(?:location|based\s+in|office\s+in)\s*[:–-]?\s*(.+?)(?:\.|,|\n|$)', re.I
)
_KNOWN_CITIES = [
    "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai", "Pune",
    "Kolkata", "Gurugram", "Noida", "Kochi", "Jaipur", "Chandigarh", "Remote",
]


def _extract_location(text: str) -> str:
    m = _LOCATION_PAT.search(text)
    if m:
        return m.group(1).strip()
    lower = text.lower()
    for city in _KNOWN_CITIES:
        if city.lower() in lower:
            return city
    return ""


# Education extraction
_EDU_PAT = re.compile(
    r"(B\.?Tech|M\.?Tech|B\.?E|M\.?E|B\.?Sc|M\.?Sc|MBA|PhD|Bachelor'?s?|Master'?s?)",
    re.I,
)


def _extract_education(text: str) -> str:
    m = _EDU_PAT.search(text)
    return m.group(0).strip() if m else ""


# Keyword extraction
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must",
    "and", "or", "but", "if", "for", "with", "on", "at", "to", "from",
    "in", "of", "by", "as", "into", "about", "between", "through",
    "we", "you", "our", "your", "this", "that", "it", "its",
    "not", "no", "so", "up", "out", "all", "also", "very", "just",
    "more", "most", "than", "then", "such", "what", "which", "who",
    "how", "when", "where", "why", "each", "every", "any", "both",
    "few", "some", "other", "new", "able", "work", "working",
    "experience", "years", "role", "looking", "join", "team",
}


def _extract_keywords(text: str) -> List[str]:
    words = re.findall(r'[A-Za-z]{3,}', text.lower())
    freq = {}
    for w in words:
        if w not in _STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:15]


# ── Public API ───────────────────────────────────────────────────────────────

def parse_jd(jd_text: str) -> ParsedJD:
    """Main entry: raw JD text -> structured ParsedJD model."""
    required, preferred = _extract_skills(jd_text)
    min_exp, max_exp = _extract_experience(jd_text)
    return ParsedJD(
        job_title=_extract_title(jd_text),
        required_skills=required,
        preferred_skills=preferred,
        min_experience=min_exp,
        max_experience=max_exp,
        education=_extract_education(jd_text),
        location=_extract_location(jd_text),
        keywords=_extract_keywords(jd_text),
    )
