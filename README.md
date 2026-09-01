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
│  │  └─ main.py
│  └─ requirements.txt
├─ frontend/
│  ├─ app/
│  ├─ package.json
│  └─ ...
├─ data/
│  └─ jobs_cache.json
├─ architecture.html
├─ brand.html
├─ logo.svg
├─ remote_job_matching_saas_v1_spec.md
├─ ui-mobile.html
├─ ui-mockups.html
├─ README.md
└─ .gitignore
```

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

### CV analysis

```bash
curl -X POST http://localhost:8000/api/analyze-cv \
  -F "file=@/path/to/your/cv.pdf"
```

## Notes

- CVs are not permanently stored.
- The app currently uses a seeded job cache for the MVP flow.
- The matching algorithm is intentionally simple and deterministic for V1 compatibility.

## Future improvements

- real AI-powered CV extraction
- richer job normalization and source ingestion
- better ranking and explanation scoring
- OAuth/auth flows for future account-based features
- persistent analytics or user history behind a premium tier

## License

This project is currently for internal prototyping and learning purposes.
