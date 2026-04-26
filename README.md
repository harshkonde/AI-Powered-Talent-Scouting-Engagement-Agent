# 🎯 AI-Powered Talent Scouting & Engagement Agent

An intelligent, rule-based recruitment tool that parses job descriptions, matches candidates from a dataset, simulates engagement conversations, and ranks candidates — all without any external AI APIs.

---

## 📌 Problem Statement

Hiring the right candidate is time-consuming. Recruiters manually read through job descriptions, scan hundreds of resumes, and reach out to candidates one by one — often with no guarantee of interest.

**This project solves that by automating the entire initial screening pipeline:**

1. **Parsing** — Extracts key requirements (skills, experience, location) from a raw job description
2. **Matching** — Scores every candidate against the JD based on skills, experience, and project relevance
3. **Engagement** — Simulates a recruiter-candidate conversation to gauge interest
4. **Ranking** — Combines match quality and interest into a final score, then ranks candidates from best to worst

The result? A recruiter gets a **ranked shortlist with explanations** in seconds instead of hours.

---

## ✨ Features

- **📝 JD Parsing** — Paste any job description and the system extracts job title, required skills, preferred skills, experience range, and location automatically using regex-based NLP
- **📊 Match Scoring** — Each candidate is scored using a weighted formula:
  ```
  Match Score = (Skill Match × 0.5) + (Experience Match × 0.3) + (Project Relevance × 0.2)
  ```
- **💬 Conversation Simulation** — Simulates realistic recruiter-candidate conversations. Candidates respond as Interested (80–100), Neutral (40–70), or Not Interested (0–30) based on how well the JD fits their profile
- **🏆 Smart Ranking** — Combines match and interest into a final score:
  ```
  Final Score = (Match Score × 0.7) + (Interest Score × 0.3)
  ```
- **💡 Explanations** — Every candidate gets a plain-English explanation: which skills matched, which are missing, and why they were ranked this way
- **🎨 Clean UI** — Dark-themed, responsive web interface with expandable candidate cards, score bars, and chat bubbles
- **📋 Sample JD** — One-click "Load Sample JD" button for instant testing

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.10+ | Core language |
| **Framework** | FastAPI | REST API server |
| **Data Validation** | Pydantic | Request/response models |
| **Server** | Uvicorn | ASGI server to run FastAPI |
| **Frontend** | HTML5 + CSS3 + JavaScript | User interface (no frameworks) |
| **Database** | JSON file | Simple candidate storage (no DB setup needed) |

---

## 📁 Project Structure

```
agentjdparsing/
│
├── backend/
│   ├── main.py              # FastAPI app — API endpoints & routing
│   ├── models.py            # Pydantic data models for validation
│   ├── jd_parser.py         # JD parsing engine (regex + heuristics)
│   ├── matcher.py           # Match Score calculator (skills, exp, projects)
│   ├── conversation.py      # Conversation simulator & Interest Score
│   ├── ranker.py            # Final Score calculator & candidate ranking
│   ├── requirements.txt     # Python dependencies
│   └── data/
│       └── candidates.json  # Dataset of 15 candidate profiles
│
├── frontend/
│   ├── index.html           # Main UI page
│   ├── style.css            # Dark-themed responsive styles
│   └── script.js            # API calls & dynamic rendering
│
└── README.md                # This file
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10 or higher installed
- pip (Python package manager)

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd agentjdparsing
```

### Step 2: Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Start the server

```bash
uvicorn main:app --reload --port 8000
```

### Step 4: Open the app

Visit **http://localhost:8000** in your browser.

That's it! No database setup, no API keys, no environment variables needed.

---

## ⚙️ How It Works

### Data Flow

```
User pastes JD
      │
      ▼
┌─────────────┐     POST /match      ┌─────────────┐
│   Frontend   │ ──────────────────▶  │   main.py   │
│  (Browser)   │                      │  (FastAPI)   │
└─────────────┘                      └──────┬──────┘
      ▲                                     │
      │                                     ▼
      │                              ┌─────────────┐
      │                              │ jd_parser.py│ ── Extracts skills, experience,
      │                              └──────┬──────┘    title, location
      │                                     │
      │                                     ▼
      │                              ┌─────────────┐
      │            candidates.json ─▶│ matcher.py  │ ── Calculates Match Score
      │                              └──────┬──────┘
      │                                     │
      │                                     ▼
      │                              ┌──────────────────┐
      │                              │ conversation.py  │ ── Simulates interest
      │                              └──────┬───────────┘
      │                                     │
      │                                     ▼
      │                              ┌─────────────┐
      │     Ranked JSON              │  ranker.py  │ ── Final Score + Rank
      └──────────────────────────────┤             │
                                     └─────────────┘
```

### Scoring Breakdown

| Step | Component | Formula | Weight |
|------|-----------|---------|--------|
| 1 | **Skill Match** | (matched skills / total JD skills) × 100 | 50% of Match Score |
| 2 | **Experience Match** | max(0, 100 − \|difference\| × 15) | 30% of Match Score |
| 3 | **Project Relevance** | (JD keywords in projects / total keywords) × 100 | 20% of Match Score |
| 4 | **Match Score** | (Skill × 0.5) + (Exp × 0.3) + (Project × 0.2) | 70% of Final Score |
| 5 | **Interest Score** | Interested: 80–100, Neutral: 40–70, Not: 0–30 | 30% of Final Score |
| 6 | **Final Score** | (Match × 0.7) + (Interest × 0.3) | Used for ranking |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the frontend UI |
| `GET` | `/health` | Health check |
| `GET` | `/candidates` | Returns all 15 candidates |
| `POST` | `/analyze-jd` | Parses a JD → returns extracted skills & experience |
| `POST` | `/match` | Full pipeline → returns ranked candidates with scores |

---

## 📋 Sample Input / Output

### Sample Input (Job Description)

```
Job Title: Senior Backend Engineer
Location: Bangalore

We are looking for a Senior Backend Engineer with 5+ years of experience.

Required Skills:
- Python
- FastAPI
- PostgreSQL
- Docker
- AWS
- REST APIs
- Git
- CI/CD

Nice to Have:
- Kubernetes
- Redis
- Microservices

Experience: 5-8 years
```

### Sample Output (Top 3 Candidates)

```json
{
  "ranked_candidates": [
    {
      "rank": 1,
      "name": "Aarav Sharma",
      "match_score": 72.5,
      "interest_score": 87,
      "final_score": 76.85,
      "interest_level": "Interested",
      "matched_skills": ["Python", "FastAPI", "Docker", "AWS", "REST APIs", "Git"],
      "missing_skills": ["PostgreSQL", "CI/CD"],
      "reason": "Aarav Sharma matches 6 out of 11 required skills (Python, FastAPI, Docker, AWS, REST APIs, Git), has exactly 6 years of experience (perfect match), and showed strong interest in the role."
    },
    {
      "rank": 2,
      "name": "Siddharth Rao",
      "match_score": 68.3,
      "interest_score": 82,
      "final_score": 72.41,
      "interest_level": "Interested",
      "matched_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
      "missing_skills": ["AWS", "CI/CD", "Git"],
      "reason": "Siddharth Rao matches 5 out of 11 required skills, has 8 years of experience (slightly over), and showed strong interest in the role."
    },
    {
      "rank": 3,
      "name": "Divya Krishnan",
      "match_score": 61.2,
      "interest_score": 85,
      "final_score": 68.34,
      "interest_level": "Interested",
      "matched_skills": ["Python", "Django", "PostgreSQL", "Docker", "REST APIs"],
      "missing_skills": ["FastAPI", "AWS", "CI/CD"],
      "reason": "Divya Krishnan matches 5 out of 11 required skills, has exactly 5 years of experience, and showed strong interest in the role."
    }
  ]
}
```

---

## 📄 License

This project is for educational and demonstration purposes.

---

Built with ❤️ using Python, FastAPI, and vanilla JavaScript.
