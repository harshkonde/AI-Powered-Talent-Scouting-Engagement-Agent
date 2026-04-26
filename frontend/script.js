/**
 * script.js — AI Talent Scout Frontend Logic
 *
 * Handles:
 *  1. Loading a sample JD into the textarea
 *  2. Calling POST /match to get ranked candidates
 *  3. Rendering parsed JD, summary stats, and candidate cards
 *  4. Expanding/collapsing cards to show explanation + conversation
 */

// ─── Sample JD for quick testing ────────────────────────────────────────────
const SAMPLE_JD = `Job Title: Senior Backend Engineer

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

Experience: 5-8 years of professional software development experience`;


// ─── DOM Elements ───────────────────────────────────────────────────────────
const jdInput       = document.getElementById("jd-input");
const findBtn       = document.getElementById("find-btn");
const sampleBtn     = document.getElementById("sample-btn");
const loading       = document.getElementById("loading");
const errorMsg      = document.getElementById("error-msg");
const parsedSection = document.getElementById("parsed-section");
const parsedGrid    = document.getElementById("parsed-grid");
const summarySection = document.getElementById("summary-section");
const summaryCards  = document.getElementById("summary-cards");
const resultsSection = document.getElementById("results-section");
const resultsList   = document.getElementById("results-list");


// ─── Event Listeners ────────────────────────────────────────────────────────

// Load sample JD button
sampleBtn.addEventListener("click", () => {
  jdInput.value = SAMPLE_JD;
  jdInput.focus();
});

// Find Candidates button
findBtn.addEventListener("click", findCandidates);


// ─── Main Function: Call API and render results ─────────────────────────────

async function findCandidates() {
  const jdText = jdInput.value.trim();

  // Validate: don't submit empty input
  if (!jdText) {
    jdInput.style.borderColor = "#ef4444";
    setTimeout(() => { jdInput.style.borderColor = ""; }, 1500);
    return;
  }

  // Show loading, hide previous results and errors
  findBtn.disabled = true;
  loading.classList.add("active");
  errorMsg.classList.remove("active");
  parsedSection.classList.remove("active");
  summarySection.classList.remove("active");
  resultsSection.classList.remove("active");

  try {
    // Call POST /match endpoint
    const response = await fetch("/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jd_text: jdText }),
    });

    if (!response.ok) {
      throw new Error("Server returned " + response.status);
    }

    const data = await response.json();

    // Render all sections
    renderParsedJD(data.parsed_jd);
    renderSummary(data.summary);
    renderCandidates(data.ranked_candidates);

    // Show results
    parsedSection.classList.add("active");
    summarySection.classList.add("active");
    resultsSection.classList.add("active");

  } catch (err) {
    // Show error message
    errorMsg.textContent = "⚠️ " + err.message + " — Make sure the backend is running (uvicorn main:app --reload)";
    errorMsg.classList.add("active");
  } finally {
    loading.classList.remove("active");
    findBtn.disabled = false;
  }
}


// ─── Render: Parsed JD ─────────────────────────────────────────────────────

function renderParsedJD(jd) {
  // Key-value items
  let html = `
    <div class="parsed-item">
      <div class="parsed-item__label">Job Title</div>
      <div class="parsed-item__value">${jd.job_title || "—"}</div>
    </div>
    <div class="parsed-item">
      <div class="parsed-item__label">Experience</div>
      <div class="parsed-item__value">${jd.min_experience}–${jd.max_experience > 50 ? "∞" : jd.max_experience} years</div>
    </div>
    <div class="parsed-item">
      <div class="parsed-item__label">Location</div>
      <div class="parsed-item__value">${jd.location || "Not specified"}</div>
    </div>
  `;

  // Required skills row
  if (jd.required_skills.length > 0) {
    html += `
      <div class="parsed-item skills-row">
        <div class="parsed-item__label">Required Skills</div>
        <div>${jd.required_skills.map(s => `<span class="skill-pill skill-pill--req">${s}</span>`).join("")}</div>
      </div>`;
  }

  // Preferred skills row
  if (jd.preferred_skills.length > 0) {
    html += `
      <div class="parsed-item skills-row">
        <div class="parsed-item__label">Nice to Have</div>
        <div>${jd.preferred_skills.map(s => `<span class="skill-pill skill-pill--pref">${s}</span>`).join("")}</div>
      </div>`;
  }

  parsedGrid.innerHTML = html;
}


// ─── Render: Summary Stats ──────────────────────────────────────────────────

function renderSummary(summary) {
  summaryCards.innerHTML = `
    <div class="summary-card">
      <div class="summary-card__num num--interested">${summary.interested}</div>
      <div class="summary-card__label">Interested</div>
    </div>
    <div class="summary-card">
      <div class="summary-card__num num--neutral">${summary.neutral}</div>
      <div class="summary-card__label">Neutral</div>
    </div>
    <div class="summary-card">
      <div class="summary-card__num num--not">${summary.not_interested}</div>
      <div class="summary-card__label">Not Interested</div>
    </div>
  `;
}


// ─── Render: Candidate Cards ────────────────────────────────────────────────

function renderCandidates(candidates) {
  resultsList.innerHTML = candidates.map((c, i) => {
    const delay = i * 0.05;

    return `
    <div class="candidate-card" style="animation-delay:${delay}s" id="card-${i}">

      <!-- Clickable header with rank, name, scores -->
      <div class="card-header" onclick="toggleCard(${i})">
        <div class="card-rank ${i < 3 ? 'card-rank--top' : ''}">${c.rank}</div>
        <div class="card-info">
          <div class="card-name">${c.name}</div>
          <div class="card-meta">${c.experience} yrs exp · ${c.location} · ${c.interest_level}</div>
        </div>
        <div class="card-scores">
          <div class="score-chip">
            <div class="score-chip__val" style="color:${scoreColor(c.match_score)}">${c.match_score}</div>
            <div class="score-chip__label">Match</div>
          </div>
          <div class="score-chip">
            <div class="score-chip__val" style="color:${scoreColor(c.interest_score)}">${c.interest_score}</div>
            <div class="score-chip__label">Interest</div>
          </div>
          <div class="score-chip">
            <div class="score-chip__val" style="color:${scoreColor(c.final_score)}">${c.final_score}</div>
            <div class="score-chip__label">Final</div>
          </div>
        </div>
        <div class="card-toggle">▼</div>
      </div>

      <!-- Expandable details -->
      <div class="card-details">
        <div class="card-body">

          <!-- Score Bars -->
          <div class="score-bars">
            ${scoreBar("Match Score", c.match_score, "match")}
            ${scoreBar("Interest Score", c.interest_score, "interest")}
            ${scoreBar("Final Score", c.final_score, "final")}
          </div>

          <!-- Explanation -->
          <div class="explanation">
            <div class="explanation__title">💡 Why this ranking</div>
            ${c.reason}
          </div>

          <!-- Matched Skills -->
          <div class="explanation" style="margin-top:0.5rem">
            <div class="explanation__title">✅ Matched Skills</div>
            <div class="detail-skills">
              ${c.matched_skills.length > 0
                ? c.matched_skills.map(s => `<span class="skill-pill skill-pill--match">${s}</span>`).join("")
                : '<span style="color:var(--text-muted);font-size:0.8rem">None</span>'}
            </div>
            ${c.missing_skills.length > 0 ? `
              <div class="explanation__title" style="margin-top:0.6rem">❌ Missing Skills</div>
              <div class="detail-skills">
                ${c.missing_skills.map(s => `<span class="skill-pill skill-pill--miss">${s}</span>`).join("")}
              </div>
            ` : ""}
          </div>

          <!-- Simulated Conversation -->
          <div class="convo">
            <div class="convo__title">💬 Simulated Conversation</div>
            ${c.conversation.map(msg => {
              const isR = msg.role === "Recruiter";
              return `
                <div class="convo-msg convo-msg--${isR ? 'recruiter' : 'candidate'}">
                  <div class="convo-avatar convo-avatar--${isR ? 'r' : 'c'}">${isR ? '🤖' : '👤'}</div>
                  <div class="convo-bubble convo-bubble--${isR ? 'r' : 'c'}">${msg.message}</div>
                </div>`;
            }).join("")}
          </div>

        </div>
      </div>

    </div>`;
  }).join("");
}


// ─── Helpers ────────────────────────────────────────────────────────────────

/** Toggle a candidate card open/closed */
function toggleCard(index) {
  document.getElementById("card-" + index).classList.toggle("open");
}

/** Return a color based on score value: green/amber/red */
function scoreColor(score) {
  if (score >= 65) return "#4ade80";
  if (score >= 40) return "#fbbf24";
  return "#f87171";
}

/** Render a single score bar */
function scoreBar(label, value, type) {
  return `
    <div class="score-bar">
      <span class="score-bar__label">${label}</span>
      <div class="score-bar__track">
        <div class="score-bar__fill fill--${type}" style="width:${value}%"></div>
      </div>
      <span class="score-bar__val">${value}</span>
    </div>`;
}
