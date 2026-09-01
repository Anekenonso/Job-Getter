# Remote Job Matching SaaS — V1 Feature Specification & Upgrade Instructions

## 1. Product Overview

Build an agent-powered web SaaS that allows a user to upload a CV and receive **10 remote job opportunities that closely match their qualifications**.

### Core promise

> **Upload your CV. Find 10 remote jobs that actually match your experience. No account required.**

The V1 should prioritize:
- Simple user experience
- No user account
- No persistent storage of CVs or extracted personal data
- Intelligent job matching
- Fresh results on every search
- Direct application links
- Low infrastructure cost

The product should be designed so that future features can be added without rebuilding the core architecture.

---

# 2. V1 Scope

## User Flow

```text
Landing Page
     ↓
Upload CV
     ↓
CV Processing
     ↓
Candidate Profile Extraction
     ↓
Web Job Research
     ↓
Job Filtering
     ↓
CV ↔ Job Matching
     ↓
Rank Results
     ↓
Display 10 Best Matches
     ↓
User Applies Directly
```

The user does **not** create an account.

The user does **not** need to provide an email.

The user's CV and extracted candidate information must not be permanently stored.

---

# 3. Landing Page

Create a clean, modern landing page.

## Hero

Headline:

**Find Remote Jobs That Match Your CV**

Subheadline:

**Upload your CV and let AI research the web for 10 remote roles that match your skills and experience.**

Primary CTA:

**Upload Your CV**

Supporting privacy statement:

**No account required. Your CV is not permanently stored.**

## How It Works

Display three simple steps:

### 1. Upload
Upload your CV in PDF or DOCX format.

### 2. AI Searches
The system analyzes your experience and searches for relevant remote opportunities.

### 3. Get 10 Matches
Receive 10 ranked jobs with match explanations and direct application links.

---

# 4. CV Upload

## Supported Formats

V1 should support:

- PDF
- DOCX

Optional future support:
- TXT
- Image/scanned CV

## Upload Constraints

Recommended V1 limits:

- Maximum file size: 5–10 MB
- One CV per search
- Reject unsupported formats
- Validate file before processing

## UX

Show:

```text
Upload your CV

[ Choose File ]

PDF or DOCX
Maximum 10 MB
```

After upload:

```text
✓ CV uploaded

[ Find My Jobs ]
```

---

# 5. CV Parser Agent

The backend should extract useful professional information from the CV.

The parser should identify:

- Name
- Professional title
- Skills
- Technical skills
- Soft skills
- Work experience
- Years of experience
- Job titles
- Industries
- Education
- Certifications
- Tools/software
- Programming languages
- Languages spoken
- Relevant achievements
- Current/most recent role

The parser should also infer:

- Seniority level
- Likely job categories
- Relevant alternative job titles
- Remote-compatible roles

Example structured output:

```json
{
  "candidate": {
    "professional_title": "AI Automation Engineer",
    "seniority": "Junior",
    "years_experience": 2,
    "skills": [
      "Python",
      "Automation",
      "AI",
      "APIs"
    ],
    "tools": [
      "FastAPI",
      "GitHub",
      "OpenAI"
    ],
    "industries": [
      "Technology",
      "Finance"
    ],
    "education": [
      "Bachelor's Degree"
    ],
    "job_titles": [
      "AI Automation Engineer",
      "Automation Engineer",
      "AI Engineer",
      "Python Developer"
    ]
  }
}
```

Do not expose unnecessary extracted personal information to external job-search services.

---

# 6. Job Research Agent

The Job Research Agent is responsible for finding fresh remote opportunities.

## Important

Do not make the final results random.

Instead:

> Search broadly and introduce variation, then intelligently rank the final results.

Example:

```text
Search Web
   ↓
80 potential jobs
   ↓
Remove duplicates
   ↓
Remove expired/unavailable jobs
   ↓
Remove non-remote jobs
   ↓
Eligibility filtering
   ↓
45 jobs
   ↓
CV matching
   ↓
25 qualified matches
   ↓
Ranking
   ↓
Top 10
```

## Search Strategy

The agent should generate multiple search queries based on the candidate profile.

Example:

```text
"remote AI automation engineer"
"remote Python automation jobs"
"remote AI operations jobs"
"remote junior AI engineer"
"remote automation specialist"
```

Search queries should adapt to the candidate's actual qualifications.

---

# 7. Job Sources

For V1, prioritize legally accessible sources and APIs.

Potential sources:

- Public company career pages
- Job-search APIs
- Public job boards with appropriate access
- Search engine results
- Remote-specific job platforms where permitted

Do not build aggressive scraping around sites whose Terms of Service prohibit automated access.

The architecture should allow additional job sources to be added later.

Create a normalized internal job format so different sources produce the same structure.

---

# 8. Job Normalization

Every discovered job should be converted into a common schema.

Example:

```json
{
  "title": "AI Operations Associate",
  "company": "Example Company",
  "location": "Remote",
  "remote": true,
  "salary": "$60,000–$80,000",
  "description": "...",
  "requirements": [],
  "source": "Company Careers",
  "application_url": "https://example.com/apply",
  "date_posted": "2026-08-20"
}
```

If salary is unavailable:

```text
salary: null
```

Do not invent salary information.

---

# 9. Job Eligibility Agent

Before scoring a job, determine whether it is realistically applicable.

Check:

- Remote status
- Geographic restrictions
- Required experience
- Required education
- Required technical skills
- Required certifications
- Work authorization requirements where explicitly stated
- Seniority
- Job availability
- Obvious mismatch

A job marked "Remote — US only" should not be presented as a universally remote opportunity to a candidate who cannot work from the US.

If geography is ambiguous, clearly label it rather than assuming eligibility.

---

# 10. Matching Agent

The Matching Agent compares the candidate profile against each job.

Score based on:

### Skills — 30%

How many important required skills does the candidate possess?

### Experience — 25%

Does the candidate have comparable professional experience?

### Role similarity — 20%

Does the candidate's previous work map naturally to the role?

### Seniority — 10%

Is the role appropriate for the candidate's experience level?

### Education/certifications — 5%

Does the candidate meet relevant educational or certification requirements?

### Industry/domain — 5%

Does the candidate have relevant domain exposure?

### Remote/location eligibility — 5%

Can the candidate realistically apply based on the stated location requirements?

Total:

```text
100 points
```

The weighting can be adjusted later through configuration rather than hard-coded throughout the application.

---

# 11. Match Explanation

Every result should explain why the candidate matches.

Example:

```text
91% Match

Why you match:
✓ Python
✓ Automation
✓ API integration
✓ AI tools
✓ Operations experience

Potential gap:
• Job requests 3+ years of experience; your CV shows approximately 2 years.
```

The system must be honest.

Never claim the candidate meets a requirement when the CV does not support it.

---

# 12. Final Results

Display exactly **10 jobs** when enough qualifying jobs are available.

Each job card should contain:

- Job title
- Company
- Match percentage
- Remote status
- Location restrictions
- Salary, if available
- Short reason for match
- Key matching skills
- Potential gaps
- Date posted, if available
- Source
- Direct application button

Example:

```text
──────────────────────────────

AI Operations Associate

Example Company

91% Match

Remote
Salary: $60k–$80k

Why you match:
✓ Python
✓ AI tools
✓ Operations
✓ Automation

Potential gap:
• Requires 3+ years experience

[ Apply for Job ]

──────────────────────────────
```

---

# 13. If Fewer Than 10 Jobs Are Found

Do not invent jobs.

If only 6 strong matches are available:

```text
We found 6 strong matches for your CV.

We didn't fill the remaining results with poor matches.
```

Optionally show weaker matches separately:

```text
6 Strong Matches

2 Possible Matches
```

V1 can simply return the available strong matches.

---

# 14. Fresh Search / Randomization

The user should be able to search again.

Button:

**Find More Jobs**

A new search should introduce variation by:

- Changing search queries
- Searching different sources
- Exploring alternative job titles
- Varying search ordering
- Avoiding jobs already displayed in the current session

However, relevance must remain the primary objective.

The system should never deliberately show a poor job just to make results look different.

---

# 15. Privacy & Data Handling

This is a critical V1 requirement.

## No Account

Do not implement:

- Registration
- Login
- Password
- Email verification

## No Persistent CV Storage

The CV should only exist for the duration necessary to process the request.

After processing:

```text
CV uploaded
   ↓
Temporary processing
   ↓
Extract information
   ↓
Search/match
   ↓
Return results
   ↓
Delete temporary CV
```

Do not permanently store:

- CV files
- Extracted CV profiles
- Personal information
- Search history
- Job history

## Database

V1 does not require a database.

If infrastructure requires temporary state, use short-lived in-memory/session data and automatically expire it.

---

# 16. Privacy Messaging

Clearly communicate:

> **No account required. Your CV is processed temporarily and is not permanently stored.**

Do not make stronger privacy claims than the actual implementation supports.

If third-party AI or search APIs receive CV-derived information, the implementation must account for those providers' data handling policies.

Minimize the amount of personal information sent to external services.

---

# 17. Error Handling

The system should gracefully handle:

### Invalid CV

```text
We couldn't read this file.
Please upload a PDF or DOCX CV.
```

### Empty/poor CV

```text
We couldn't extract enough professional information from this CV to find reliable matches.

Try uploading a more detailed CV.
```

### Search failure

```text
We couldn't complete the job search right now.

Please try again.
```

### No strong matches

```text
We couldn't find 10 strong remote matches right now.

We found 4 roles that appear relevant.
```

Never fabricate job listings.

---

# 18. Recommended V1 Tech Stack

## Frontend

- Next.js
- React
- Tailwind CSS

## Backend

- Python
- FastAPI

## AI

Use an LLM API for:

- CV extraction
- Job classification
- Matching
- Match explanations
- Search query generation

## CV Processing

Use appropriate PDF/DOCX parsing libraries.

Optional OCR can be added later.

## Web Research

Use search APIs and permitted job APIs/public pages.

## Database

**None required for V1.**

## Authentication

**None required for V1.**

## File Storage

**None required for persistent storage.**

## Hosting

Recommended:

```text
Frontend → Vercel
Backend → Render / Railway
```

The exact hosting provider can change without affecting the application architecture.

---

# 19. Backend Architecture

Recommended structure:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── upload.py
│   │   └── jobs.py
│   │
│   ├── agents/
│   │   ├── cv_parser.py
│   │   ├── job_researcher.py
│   │   ├── job_filter.py
│   │   ├── job_matcher.py
│   │   └── ranking.py
│   │
│   ├── services/
│   │   ├── cv_processing.py
│   │   ├── search.py
│   │   └── job_normalizer.py
│   │
│   ├── models/
│   │   ├── candidate.py
│   │   └── job.py
│   │
│   └── config.py
│
├── tests/
│
├── requirements.txt
└── README.md
```

Keep agents modular.

A new job source should not require rewriting the matching system.

---

# 20. Frontend Architecture

Recommended:

```text
frontend/
│
├── app/
│   ├── page.tsx
│   ├── results/
│   │   └── page.tsx
│   └── api/
│
├── components/
│   ├── CVUploader.tsx
│   ├── ProcessingState.tsx
│   ├── JobCard.tsx
│   ├── MatchScore.tsx
│   └── PrivacyNotice.tsx
│
└── lib/
    └── api.ts
```

Keep the UI simple.

The core product is the quality of the job matches, not a complicated dashboard.

---

# 21. API Design

## POST /api/analyze-cv

Accepts:

```text
multipart/form-data
CV file
```

Returns a temporary candidate profile or processing identifier.

## POST /api/find-jobs

Input:

```json
{
  "candidate_profile": {},
  "search_preferences": {
    "remote_only": true
  }
}
```

Returns:

```json
{
  "jobs": []
}
```

## Optional

## POST /api/search-again

Runs another varied search for the same temporary session.

No persistent user record should be created.

---

# 22. Agent Workflow

The complete agent workflow should look like:

```text
                USER
                  │
                  ▼
              Upload CV
                  │
                  ▼
        ┌──────────────────┐
        │ CV Parser Agent  │
        └────────┬─────────┘
                 │
                 ▼
        Candidate Profile
                 │
                 ▼
        ┌──────────────────┐
        │ Search Agent     │
        └────────┬─────────┘
                 │
                 ▼
        Potential Jobs
                 │
                 ▼
        ┌──────────────────┐
        │ Filter Agent     │
        └────────┬─────────┘
                 │
                 ▼
        Eligible Jobs
                 │
                 ▼
        ┌──────────────────┐
        │ Matching Agent   │
        └────────┬─────────┘
                 │
                 ▼
          Match Scores
                 │
                 ▼
        ┌──────────────────┐
        │ Ranking Agent    │
        └────────┬─────────┘
                 │
                 ▼
            Top 10 Jobs
                 │
                 ▼
              USER
```

---

# 23. Agent Responsibilities

## CV Parser Agent

Responsible only for understanding the CV.

It should not search for jobs.

## Search Agent

Responsible only for discovering potential jobs.

It should not determine the final match score.

## Filter Agent

Responsible for removing clearly unsuitable jobs.

## Matching Agent

Responsible for comparing candidate qualifications against job requirements.

## Ranking Agent

Responsible for ordering qualified jobs and selecting the final results.

This separation makes the system easier to debug and upgrade.

---

# 24. Anti-Hallucination Requirements

The system must never:

- Invent companies
- Invent jobs
- Invent salaries
- Invent application links
- Invent requirements
- Claim a job is remote without evidence
- Claim a candidate has a skill not supported by their CV

Every job should retain its original source URL.

Where possible, the system should preserve the job's original title, company, location, salary, requirements, and posting date.

---

# 25. Performance Targets

Aim for:

- CV upload: <5 seconds
- CV parsing: <10 seconds
- Job search + matching: ideally <60–90 seconds
- Results page: responsive and mobile-friendly

Because web research can be slow, display progress states.

Example:

```text
✓ CV analyzed

✓ Identified your key skills

⟳ Searching remote jobs...

○ Comparing jobs with your CV

○ Ranking your best matches
```

---

# 26. Cost-Control Strategy

The V1 should be lightweight.

Avoid:

- Large servers
- Kubernetes
- Complex databases
- Long-running workers
- Persistent file storage
- Unnecessary AI calls

Use a pipeline that minimizes LLM calls.

For example:

```text
CV
 ↓
1 AI extraction call
 ↓
Search
 ↓
Basic programmatic filtering
 ↓
AI matching only for shortlisted jobs
 ↓
Ranking
```

Do not send 100 full job descriptions to an LLM if 60 can be removed through basic rules first.

---

# 27. Security Requirements

Implement:

- File type validation
- File size limits
- Input sanitization
- Request rate limiting
- Temporary file cleanup
- API key protection
- Server-side API calls
- HTTPS
- CORS restrictions
- Timeout limits

Do not expose AI/search API keys in the frontend.

---

# 28. V1 Acceptance Criteria

V1 is complete when:

- [ ] User can open the website without an account
- [ ] User can upload a PDF CV
- [ ] User can upload a DOCX CV
- [ ] CV can be parsed
- [ ] Candidate profile can be generated
- [ ] System can generate relevant search queries
- [ ] System can research remote jobs
- [ ] Jobs can be normalized
- [ ] Non-remote jobs can be filtered
- [ ] Obviously unsuitable jobs can be filtered
- [ ] Jobs can be matched against CV
- [ ] Jobs receive match scores
- [ ] System provides match explanations
- [ ] Top 10 results are displayed
- [ ] Every result has an application URL
- [ ] No account is required
- [ ] CV is not permanently stored
- [ ] No user database is required
- [ ] Invalid uploads are handled
- [ ] Search failures are handled
- [ ] No fake jobs/results are generated
- [ ] User can perform another search
- [ ] UI works on mobile

---

# 29. V1 → V2 Feature Upgrade Roadmap

Do not implement these features in V1 unless required.

The architecture should simply leave room for them.

## V2 — Personal Job Search

Add:

### User Accounts

- Sign up
- Login
- Profile
- Saved preferences

### Saved CV

Allow users to securely save their CV.

### Job Preferences

Users can specify:

- Preferred roles
- Salary
- Countries
- Time zones
- Industries
- Experience level

### Saved Jobs

Users can save interesting opportunities.

### Application Tracker

Example:

```text
Saved
   ↓
Applied
   ↓
Interview
   ↓
Offer
   ↓
Rejected
```

---

# 30. V3 — AI Application Assistant

Once job discovery works reliably, add:

## CV Tailoring

User selects a job.

AI analyzes:

```text
Current CV
+
Job Description
```

Then recommends CV changes.

## Cover Letter

Generate a job-specific cover letter.

## Application Answers

Generate drafts for application questions based on the user's CV.

## Resume Optimization

Identify:

- Missing keywords
- Weak bullet points
- Poorly demonstrated achievements
- Skills to emphasize

---

# 31. V4 — Autonomous Job Agent

The product can eventually become:

> **An AI agent that continuously finds and helps you apply to remote jobs.**

Possible workflow:

```text
User Profile
     ↓
Agent searches daily
     ↓
Finds relevant jobs
     ↓
Scores opportunities
     ↓
Sends notifications
     ↓
User approves
     ↓
Agent tailors CV
     ↓
Agent prepares application
     ↓
User reviews/submits
```

Do not automatically submit applications without explicit user authorization.

---

# 32. Future Monetization

## Free

- Limited searches
- 10 jobs per search
- Basic matching

## Pro

- Unlimited searches
- Daily job discovery
- Saved jobs
- Job alerts
- Multiple CVs
- Advanced matching
- CV tailoring
- Cover letters

## Premium / Agent

- Continuous job monitoring
- Personalized opportunities
- Application preparation
- Application tracking
- Advanced AI assistance

---

# 33. Product Differentiation

Do not position the product as:

> "Another job board."

Position it as:

> **An AI job discovery agent that searches the web for opportunities based on your actual qualifications.**

The key differentiator is:

```text
Traditional Job Board

User → Search → Browse hundreds of jobs → Apply
```

Versus:

```text
This Product

User → Upload CV → AI understands qualifications
     → Searches web → Filters → Matches → Ranks
     → 10 relevant opportunities
```

The product reduces the user's job-search workload.

---

# 34. Recommended Build Order

Build in this exact sequence.

## Phase 1 — Foundation

- [ ] Create frontend
- [ ] Create Python/FastAPI backend
- [ ] Connect frontend and backend
- [ ] Implement CV upload
- [ ] Implement file validation

## Phase 2 — CV Intelligence

- [ ] PDF parser
- [ ] DOCX parser
- [ ] Candidate profile schema
- [ ] CV Parser Agent
- [ ] Test extraction accuracy

## Phase 3 — Job Research

- [ ] Integrate search provider
- [ ] Build search query generator
- [ ] Search multiple query variations
- [ ] Normalize results
- [ ] Remove duplicates

## Phase 4 — Job Intelligence

- [ ] Remote filter
- [ ] Geographic eligibility
- [ ] Experience filter
- [ ] Matching Agent
- [ ] Match scoring
- [ ] Ranking

## Phase 5 — Results UI

- [ ] Job cards
- [ ] Match scores
- [ ] Match explanations
- [ ] Potential gaps
- [ ] Application links
- [ ] Loading/progress states

## Phase 6 — Privacy

- [ ] Temporary CV processing
- [ ] Automatic cleanup
- [ ] No persistent database
- [ ] Privacy notice
- [ ] Third-party data-flow review

## Phase 7 — Quality

- [ ] Test with different CVs
- [ ] Test different industries
- [ ] Test junior/senior candidates
- [ ] Test poor CVs
- [ ] Test no-result searches
- [ ] Test duplicate jobs
- [ ] Test broken application links

---

# 35. Most Important Product Principle

Do not optimize for:

**"10 jobs every time."**

Optimize for:

**"10 useful jobs when possible."**

If the system cannot find 10 legitimate, relevant opportunities, it should tell the user rather than fill the list with low-quality or fabricated results.

The long-term value of the product will depend almost entirely on the quality and trustworthiness of its recommendations.

---

# 36. Final V1 Definition

The first version should be:

> A lightweight, account-free, privacy-conscious AI web application where a user uploads a CV, the system temporarily analyzes it, researches the web for remote job opportunities, filters and scores those opportunities against the candidate's qualifications, and presents the 10 strongest matches with explanations and direct application links.

### V1 deliberately excludes:

- User accounts
- Persistent CV storage
- Saved jobs
- Job alerts
- Application tracking
- CV rewriting
- Cover letters
- Automatic applications
- Complex dashboards

Build the **job-matching engine first**.

If users consistently find the recommendations useful, then add accounts, persistence, alerts, CV tailoring, and autonomous application assistance in later versions.
