"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function HomePage() {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [candidate, setCandidate] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Please choose a CV file first.");
      return;
    }

    setIsLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE}/api/analyze-cv`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({ detail: "Request failed." }));
        throw new Error(err.detail || "Request failed.");
      }

      const data = await response.json();
      setCandidate(data.candidate);
      setJobs(data.jobs || []);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main style={styles.page}>
      <section style={styles.hero}>
        <div style={styles.content}>
          <p style={styles.eyebrow}>Remote job matching</p>
          <h1 style={styles.title}>Find Remote Jobs That Match Your CV</h1>
          <p style={styles.subtitle}>
            Upload your CV and let AI research the web for 10 remote roles that match your skills and experience.
          </p>

          <form onSubmit={handleSubmit} style={styles.form}>
            <label style={styles.uploadLabel}>
              <span style={styles.uploadText}>Upload your CV</span>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
                style={styles.fileInput}
              />
            </label>

            <div style={styles.meta}>
              <span>PDF or DOCX</span>
              <span>Maximum 10 MB</span>
            </div>

            <button type="submit" style={styles.primaryButton} disabled={isLoading}>
              {isLoading ? "Finding Matches..." : "Find My Jobs"}
            </button>
          </form>

          {error ? <p style={styles.error}>{error}</p> : null}
          <p style={styles.privacy}>No account required. Your CV is not permanently stored.</p>
        </div>
      </section>

      {candidate ? (
        <section style={styles.results}>
          <h2 style={styles.sectionTitle}>Your candidate profile</h2>
          <div style={styles.profileCard}>
            <p><strong>Title:</strong> {candidate.professional_title}</p>
            <p><strong>Seniority:</strong> {candidate.seniority}</p>
            <p><strong>Experience:</strong> {candidate.years_experience} years</p>
            <p><strong>Skills:</strong> {candidate.skills.join(", ") || "N/A"}</p>
          </div>

          <h2 style={styles.sectionTitle}>Top 10 matches</h2>
          <div style={styles.grid}>
            {jobs.map((job) => (
              <article key={job.id} style={styles.jobCard}>
                <div style={styles.jobHeader}>
                  <div>
                    <p style={styles.jobCompany}>{job.company}</p>
                    <h3 style={styles.jobTitle}>{job.title}</h3>
                  </div>
                  <span style={styles.score}>{job.match_score}%</span>
                </div>
                <p style={styles.location}>{job.location} • {job.remote ? "Remote" : "On-site"}</p>
                <p style={styles.jobText}>{job.description}</p>
                <p style={styles.reason}><strong>Why it matches:</strong> {job.match_reason}</p>
                <p style={styles.skills}><strong>Skills:</strong> {(job.required_skills || []).join(", ")}</p>
                <a href={job.url} target="_blank" rel="noreferrer" style={styles.linkButton}>
                  Apply now
                </a>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </main>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f8fafc",
    color: "#0f172a",
    fontFamily: "Arial, sans-serif",
    padding: "48px 20px 80px",
  },
  hero: {
    maxWidth: "1100px",
    margin: "0 auto",
    background: "linear-gradient(135deg, #eff6ff, #f8fafc)",
    border: "1px solid #dbeafe",
    borderRadius: "24px",
    padding: "52px 28px",
    boxShadow: "0 10px 30px rgba(15, 23, 42, 0.06)",
  },
  content: {
    maxWidth: "720px",
    margin: "0 auto",
    textAlign: "center",
  },
  eyebrow: {
    letterSpacing: "0.12em",
    textTransform: "uppercase",
    color: "#2563eb",
    fontWeight: 700,
    margin: "0 0 18px",
    fontSize: "12px",
  },
  title: {
    margin: 0,
    fontSize: "3rem",
    lineHeight: 1.1,
  },
  subtitle: {
    margin: "18px auto 32px",
    maxWidth: "620px",
    color: "#475569",
    fontSize: "1.15rem",
    lineHeight: 1.6,
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "16px",
    maxWidth: "560px",
    margin: "0 auto",
  },
  uploadLabel: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "10px",
    background: "#ffffff",
    border: "1px dashed #7dd3fc",
    borderRadius: "16px",
    padding: "24px 16px",
  },
  uploadText: {
    fontWeight: 700,
    fontSize: "1.1rem",
  },
  fileInput: {
    width: "100%",
    maxWidth: "260px",
  },
  meta: {
    display: "flex",
    justifyContent: "center",
    gap: "20px",
    color: "#475569",
    fontSize: "0.92rem",
  },
  primaryButton: {
    border: "none",
    background: "#2563eb",
    color: "#fff",
    borderRadius: "12px",
    padding: "14px 22px",
    fontSize: "1rem",
    cursor: "pointer",
    fontWeight: 700,
  },
  privacy: {
    marginTop: "16px",
    color: "#475569",
    fontSize: "0.95rem",
  },
  error: {
    marginTop: "18px",
    color: "#dc2626",
    fontWeight: 600,
  },
  results: {
    maxWidth: "1100px",
    margin: "30px auto 0",
  },
  sectionTitle: {
    margin: "0 0 18px",
    fontSize: "1.8rem",
  },
  profileCard: {
    background: "#fff",
    border: "1px solid #e2e8f0",
    borderRadius: "18px",
    padding: "20px 22px",
    marginBottom: "28px",
    boxShadow: "0 4px 20px rgba(15, 23, 42, 0.04)",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "18px",
  },
  jobCard: {
    background: "#fff",
    border: "1px solid #e2e8f0",
    borderRadius: "18px",
    padding: "18px",
    boxShadow: "0 6px 22px rgba(15, 23, 42, 0.04)",
  },
  jobHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "10px",
  },
  jobCompany: {
    margin: 0,
    color: "#475569",
    fontSize: "0.76rem",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  jobTitle: {
    margin: "6px 0 0",
    fontSize: "1.2rem",
  },
  score: {
    background: "#dcfce7",
    color: "#166534",
    fontWeight: 700,
    borderRadius: "999px",
    padding: "8px 10px",
    fontSize: "0.8rem",
  },
  location: {
    margin: "12px 0 10px",
    color: "#475569",
    fontSize: "0.9rem",
  },
  jobText: {
    color: "#334155",
    lineHeight: 1.55,
    margin: "0 0 10px",
  },
  reason: {
    fontSize: "0.9rem",
    margin: "0 0 8px",
    color: "#1e293b",
  },
  skills: {
    color: "#475569",
    fontSize: "0.9rem",
    margin: "0 0 14px",
  },
  linkButton: {
    display: "inline-block",
    padding: "10px 14px",
    borderRadius: "10px",
    background: "#0f172a",
    color: "#fff",
    textDecoration: "none",
    fontWeight: 700,
  },
};
