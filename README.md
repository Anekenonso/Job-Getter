<div align="center">

# Job-Getter

### AI-powered job discovery and matching from your CV

Upload a CV and get remote job opportunities ranked by how well they match your skills, experience, seniority, and work eligibility.

**[Live Demo](https://ai-jobgetter.vercel.app/)** · **[Follow @AI_jobgetter on X](https://x.com/AI_jobgetter)**

<br />

<img src="docs/screenshots/homepage.png" alt="Job-Getter homepage" width="900" />

</div>

---

## Overview

Job-Getter is an AI-powered job discovery and matching application that turns an existing CV into a structured candidate profile, researches relevant remote opportunities, evaluates them against the candidate's profile, and returns ranked recommendations.

The goal is simple:

> **Spend less time searching through jobs and more time applying to the right ones.**

Job-Getter is designed around three principles:

* **Relevance over quantity** — weaker matches are not presented as strong matches just to fill a list.
* **Explainable results** — each recommendation includes the skills and experience that contributed to the match.
* **Privacy by design** — CVs are processed in memory and are not stored as user profiles.

---

## How It Works

```text
                    ┌─────────────────┐
                    │    CV Upload    │
                    │    PDF / DOCX   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    CV Parser    │
                    │                 │
                    │ Candidate       │
                    │ Profile         │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Job Research    │
                    │ Agent           │
                    │                 │
                    │ Targeted search │
                    │ queries         │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Job Ingestion   │
                    │ & Normalization │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Matching &      │
                    │ Ranking         │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Ranked Job      │
                    │ Recommendations │
                    └─────────────────┘
```

### 1. Upload

The user uploads a PDF or DOCX CV.

The document is parsed in memory and converted into a structured candidate profile containing information such as:

* Skills
* Job titles
* Experience
* Seniority
* Education
* Location/work eligibility information

### 2. Research

The candidate profile is passed to the **Job Research Agent**.

The agent generates targeted search queries based on the candidate's experience and skills and sends them to the job search layer.

If the LLM is unavailable, Job-Getter falls back to deterministic query generation instead of failing the entire workflow.

### 3. Normalize

Job listings from different sources are converted into a common internal representation.

This makes downstream filtering and matching independent of the original job source.

### 4. Match & Rank

Jobs are evaluated against the candidate profile using factors including:

* Skills
* Experience
* Seniority
* Role relevance
* Work-location restrictions
* Other job requirements

The resulting jobs are ranked and separated into stronger and weaker matches.

### 5. Apply

The user receives the highest-quality matches with:

* Match score
* Matching skills
* Relevant experience
* Potential gaps or restrictions
* Original job title and company
* Direct application link

---

## AI Architecture

Job-Getter does not depend on a single LLM call to produce the final result.

The AI layer is used as part of a larger pipeline.

### Job Research Agent

The research agent takes a structured candidate profile and generates focused search queries.

For example:

```text
Candidate:
Python developer
3 years experience
FastAPI
PostgreSQL
AWS

        ↓

Generated search queries:

"remote Python developer FastAPI"
"remote backend engineer Python AWS"
"remote Python PostgreSQL developer"
```

The research layer then handles job retrieval.

### Deterministic Fallback

AI services can fail, time out, or become temporarily unavailable.

Job-Getter therefore includes a deterministic fallback for query generation.

```text
              Candidate Profile
                     │
                     ▼
             ┌───────────────┐
             │ LLM available?│
             └───────┬───────┘
                 Yes │   │ No
                     │   │
                     ▼   ▼
              LLM queries  Deterministic
                           queries
                     │   │
                     └───┘
                       │
                       ▼
                 Job Retrieval
```

This keeps the core application usable even when the AI provider is unavailable.

---

## Engineering Decisions

### Privacy-first CV processing

Job-Getter does not require users to create accounts or build a permanent profile.

CV uploads are processed in memory rather than being persisted as user documents.

### Separation of concerns

The system separates responsibilities across different layers for:

* API handling
* CV parsing
* Candidate modelling
* Job research
* Job ingestion
* Job normalization
* Matching
* Ranking

This allows individual parts of the pipeline to be changed without rewriting the entire application.

### AI with graceful degradation

LLM functionality improves query generation but is not treated as an unavoidable dependency for the complete workflow.

Deterministic fallbacks are used when AI functionality is unavailable.

### Input validation

CV uploads are restricted to supported document formats and a maximum file size.

The API validates incoming requests before processing them.

### Explainable recommendations

Instead of returning a list of job links, the system provides information about why a role matches and identifies relevant gaps or restrictions.

---

## Privacy

Job-Getter is designed to minimize the amount of personal information it retains.

* No account required
* No password or email required
* CVs are processed in memory
* No persistent CV profile
* PDF and DOCX uploads only
* Maximum upload size: 5 MB

The application is designed so a user can upload a CV, receive recommendations, and leave without creating a permanent account.

---

## Tech Stack

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn
* HTTPX

### Document Processing

* PyPDF
* python-docx

### AI

* LLM-powered query generation
* Deterministic fallback logic

### Frontend

* Next.js
* React
* Tailwind CSS

### Infrastructure

* Vercel
* Docker
* REST API

---

## Testing

The project includes automated tests covering important parts of the application.

Tests include:

* API behaviour
* CV upload validation
* Pipeline execution
* Job normalization
* Job restriction detection
* Job processing behaviour

Run the backend tests with:

```bash
cd backend
pytest
```

---

## Project Structure

```text
Job-Getter/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── models/
│   │   ├── services/
│   │   └── ...
│   │
│   └── tests/
│
├── frontend/
│   └── ...
│
├── ingestion/
│   └── ...
│
├── data/
│   └── ...
│
├── docs/
│   └── screenshots/
│
└── docker-compose.yml
```

The backend contains the application and AI pipeline, while the frontend provides the user-facing interface.

---

## Running Locally

### Clone the repository

```bash
git clone https://github.com/Anekenonso/Job-Getter.git
cd Job-Getter
```

### Backend

```bash
cd backend

python -m venv .venv
```

Activate the environment:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

## Screenshots

### Homepage

<img src="docs/screenshots/homepage.png" alt="Job-Getter homepage" width="900" />

### Processing

<img src="docs/screenshots/processing.png" alt="Job-Getter processing a CV" width="760" />

### Results

<img src="docs/screenshots/results.png" alt="Job-Getter job matching results" width="620" />

---

## Current Limitations

Job-Getter is an MVP and has several areas that can be improved.

* Job availability depends on the underlying job sources.
* Location and work-eligibility matching can be improved further.
* Matching quality can be improved through larger evaluation datasets and better ranking strategies.
* User accounts and saved searches are not currently part of the core experience.
* The current system prioritizes a simple, low-friction workflow over long-term personalization.

These are intentional areas for future development rather than hidden limitations.

---

## Roadmap

* Improve location and work-eligibility matching
* Expand job-source coverage
* Improve duplicate detection
* Build a dedicated matching evaluation dataset
* Benchmark ranking quality
* Add optional accounts
* Add saved searches and job alerts
* Improve personalized matching
* Explore premium matching features

---

## Why I Built It

Job searching is often repetitive:

**Find a role → read the requirements → compare them with your CV → decide whether to apply → repeat.**

Job-Getter automates much of that process.

The project was also built as an exploration of how AI can be combined with traditional software engineering to create reliable workflow automation rather than simply generating text.

---

## License

Currently for prototyping and demonstration purposes.
