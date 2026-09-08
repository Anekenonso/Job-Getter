<div align="center">

# Job-Getter

### Upload your CV. Get 10 remote jobs that actually fit.

No account. No profile to fill in. No data stored.

<br />

<img src="docs/screenshots/homepage.png" alt="Job-Getter — upload your CV and get 10 matched remote jobs" width="900" />

<br />

**[Follow @JobGetter on X](https://x.com/JobGetter)** · Privacy-first remote-job matching

</div>

---

## The problem

Job seekers waste hours scrolling job boards that were built for recruiters, not candidates. The listings are stale, the "remote" filter lies, the match is guesswork, and every promising site wants an account and a re-typed résumé before it will show you anything.

**Job-Getter flips it.** You drop in the CV you already have, and within a minute you get a short, honest list of remote roles matched to your real experience — each with a plain-English reason and a direct link to the original posting. Nothing to sign up for. Nothing kept afterwards.

---

## How it works

Three steps, under a minute, zero friction.

**1. Upload** — Drop a PDF or DOCX CV. It's read in memory and never written to disk.

**2. Match** — Job-Getter reads your profile, pulls fresh remote roles, and scores each one against your skills, experience, seniority, and how well the role fits.

<div align="center">
  <img src="docs/screenshots/processing.png" alt="Job-Getter analyzing a CV" width="760" />
</div>

**3. Apply** — Get your top matches, sorted by score, each with the skills that lined up, an honest note on any gaps, and a link straight to the source posting.

<div align="center">
  <img src="docs/screenshots/results.png" alt="Ten remote jobs matched and scored against the candidate's profile" width="620" />
</div>

---

## Why it's different

- **Honest matching, never padding.** If only six roles genuinely fit, you get six — not ten stuffed with noise. Weaker matches are shown separately as "possible matches," clearly labelled. The app never invents a job, a salary, or an application link.
- **It tells you *why*.** Every result explains the overlap in plain language ("Strong overlap on Python, SQL, AWS") and flags real gaps ("Role is restricted to US only — confirm you can work from there").
- **Truly no account.** No sign-up, no email, no password, no profile builder. Open the page, upload, done.
- **Private by design.** Your CV is processed in memory and discarded the moment your matches are returned. Nothing is stored, logged, or sold.
- **Genuinely remote.** Roles are checked for remote eligibility and tagged with any geographic restriction up front.

---

## For investors

**Market.** Remote hiring is now permanent, and the candidate side of the market is badly served — incumbents monetize employers and treat seekers as inventory. Job-Getter is a candidate-first wedge into that gap: the fastest path from "I have a CV" to "here are jobs worth applying to."

**Differentiation.** The moat isn't the job data (that's commodity) — it's the *matching quality and the trust that comes from honesty*. Refusing to pad results, explaining every score, and storing nothing are product decisions that compound into a brand candidates actually recommend.

**Capital efficiency.** The entire MVP is engineered to run on free tiers:

| Cost center | Today | Notes |
|---|---|---|
| Job data | **$0** | Free public job sources, cached and refreshed automatically |
| Hosting | **$0** | Free-tier hosting for the app and API |
| Scheduled refresh | **$0** | Free scheduled job to keep the pool fresh |
| Matching intelligence | **~$0** today | The *only* variable cost; roughly $0.05–0.15 per search on a premium model |

That means the product ships and serves real users at essentially **$0 fixed cost**, with a single, legible, per-search variable cost that scales linearly and is trivial to model. Monetization — premium matching depth, saved searches, alerts, employer-side placement — sits on top of a base that costs almost nothing to keep running.

**Roadmap to revenue.** Live search on every request → smarter location eligibility → optional accounts for saved searches and alerts → premium tier → employer-side matching.

---

## Privacy by design

- Your CV is processed **in memory only** and never saved.
- No accounts, no tracking profiles, no CV storage.
- Uploads are limited to PDF or DOCX, up to 5 MB.
- The app never fabricates jobs, salaries, or application links.

---

## Roadmap

- Live search on every request (today the job pool is pre-fetched for speed and $0 cost)
- Smarter location-eligibility matching
- Optional accounts for saved searches, alerts, and history
- Premium matching depth
- Employer-side matching

---

## Contact

Questions, feedback, or a hired shout-out — reach us on X: **[@JobGetter](https://x.com/JobGetter)**.

## License

Currently for prototyping and demonstration purposes.
