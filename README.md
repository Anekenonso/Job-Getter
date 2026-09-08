# Job-Getter

Job-Getter is a stateless remote job matching SaaS that lets users upload a CV, extract a candidate profile, and receive the top 10 remote job opportunities that best match their experience.

## Product goal

> Upload your CV. Find 10 remote jobs that actually match your experience.

The MVP is designed around a no-account, no-persistence flow:

- users upload a CV once per search
- the backend extracts key candidate attributes in memory
- a shared job cache is filtered and ranked
- the top 10 matches are returned with direct application links

## Architecture

The project follows the V1 architecture described in the spec and architecture HTML:

- Frontend: Next.js app
- Backend: FastAPI API
- Job source cache: shared JSON file refreshed by scheduled ingestion
- Matching flow: CV parsing -> filter -> match -> rank

## Project structure

```text
Job-Getter/
├─ backend/
│  ├─ app/
│  │  ├─ main.py              # composition root (middleware + routers)
│  │  ├─ config.py            # all tunables (weights, limits, CORS, LLM)
│  │  ├─ pipeline.py          # orchestrates the agents
│  │  ├─ middleware.py        # in-memory rate limiting
│  │  ├─ api/                 # upload.py, jobs.py, schemas, responses
│  │  ├─ agents/              # cv_parser, job_researcher, job_filter,
│  │  │                       #   job_matcher, ranking
│  │  ├─ services/            # cv_processing, search, job_normalizer, llm
│  │  └─ models/              # candidate, job
│  ├─ tests/
│  └─ requirements.txt
├─ frontend/
│  ├─ app/                    # layout, page, globals.css
│  ├─ components/             # CVUploader, ProcessingState, JobCard,
│  │                          #   MatchScore, PrivacyNotice, SocialCTA, Brand
│  ├─ lib/api.js
│  └─ tailwind.config.js
├─ ingestion/
│  └─ refresh_cache.py        # pull sources → normalize → dedupe → write
├─ .github/workflows/
│  └─ refresh-jobs.yml        # scheduled cache refresh (every 8h)
├─ data/
│  └─ jobs_cache.json         # shared normalized job pool
└─ README.md
```

## Matching pipeline

```text
CV text → CV Parser → Research → Filter → Matcher → Ranking → results
```

Each agent is single-purpose. The matcher scores against a configurable weighted
rubric (`config.MATCH_WEIGHTS`): skills 30%, experience 25%, role 20%,
seniority 10%, education/industry/location 5% each. Results below the strong-match
threshold are offered as "possible matches" rather than padding the list.

## AI (optional)

The CV parser, matcher explanations, and query generation use the Groq LLM when
`GROQ_API_KEY` is set (see `backend/.env.example`). With no key, the app falls
back to deterministic heuristics and still works end-to-end at $0.

## Local setup

### 1. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at:

```text
http://localhost:3000
```

### 2. Backend

Use Python 3.12 for compatibility with the pinned dependency stack.

```bash
cd backend
"C:/Users/USER/AppData/Local/Programs/Python/Python312/python.exe" -m pip install -r requirements.txt
"C:/Users/USER/AppData/Local/Programs/Python/Python312/python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API runs at:

```text
http://localhost:8000
```

## API

### Health check

```bash
curl http://localhost:8000/health
```

### CV analysis (upload → parse → match → rank)

```bash
curl -X POST http://localhost:8000/api/analyze-cv \
  -F "file=@/path/to/your/cv.pdf"
```

### Find jobs (from an already-parsed profile)

```bash
curl -X POST http://localhost:8000/api/find-jobs \
  -H "Content-Type: application/json" \
  -d '{"candidate_profile": {"professional_title":"Python Developer","skills":["python","sql"],"job_titles":["Python Developer"]}}'
```

### Search again (varied re-search, excludes seen jobs)

```bash
curl -X POST http://localhost:8000/api/search-again \
  -H "Content-Type: application/json" \
  -d '{"candidate_profile": {...}, "exclude_ids": ["cache-..."], "variation": 1}'
```

## Job ingestion

`ingestion/refresh_cache.py` pulls fresh remote jobs from Jobicy, Remotive, and
Arbeitnow, normalizes them to one schema, dedupes, and writes `data/jobs_cache.json`.
It runs on a GitHub Actions cron (`.github/workflows/refresh-jobs.yml`) every 8
hours, and can be run locally:

```bash
python ingestion/refresh_cache.py
```

## Notes

- CVs are processed in memory and never persisted.
- Uploads: PDF/DOCX, max 5 MB, validated before processing.
- CORS is locked to configured frontend origins; API endpoints are rate limited.
- The app never fabricates jobs, salaries, or application links.

## Future improvements

- live API search per request (currently cache-fed)
- richer geographic-eligibility inference
- OAuth/auth flows for future account-based features
- persistent analytics or user history behind a premium tier

## License

This project is currently for internal prototyping and learning purposes.
