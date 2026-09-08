"use client";

import { useState } from "react";

import { Logo, Wordmark, XIcon, X_URL } from "../components/Brand";
import CVUploader from "../components/CVUploader";
import ProcessingState from "../components/ProcessingState";
import JobCard from "../components/JobCard";
import PrivacyNotice from "../components/PrivacyNotice";
import SocialCTA from "../components/SocialCTA";
import { analyzeCV, searchAgain } from "../lib/api";

const STAGE = { UPLOAD: "upload", PROCESSING: "processing", RESULTS: "results" };

export default function HomePage() {
  const [stage, setStage] = useState(STAGE.UPLOAD);
  const [candidate, setCandidate] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [possible, setPossible] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loadingMore, setLoadingMore] = useState(false);
  const [seenIds, setSeenIds] = useState([]);
  const [variation, setVariation] = useState(0);

  async function handleUpload(file) {
    setStage(STAGE.PROCESSING);
    setError("");
    try {
      const data = await analyzeCV(file);
      setCandidate(data.candidate);
      setJobs(data.jobs || []);
      setPossible(data.possible_matches || []);
      setMessage(data.message || "");
      setSeenIds((data.jobs || []).map((j) => j.id));
      setStage(STAGE.RESULTS);
    } catch (err) {
      setError(err.message || "Something went wrong.");
      setStage(STAGE.UPLOAD);
    }
  }

  async function handleSearchAgain() {
    if (!candidate) return;
    setLoadingMore(true);
    setError("");
    try {
      const nextVariation = variation + 1;
      const data = await searchAgain({
        candidateProfile: candidate,
        excludeIds: seenIds,
        variation: nextVariation,
      });
      const fresh = data.jobs || [];
      setVariation(nextVariation);
      if (fresh.length === 0) {
        setMessage("That's every strong match we have for now. Try again later for fresh roles.");
      } else {
        setJobs(fresh);
        setPossible(data.possible_matches || []);
        setMessage(data.message || "");
        setSeenIds((prev) => [...prev, ...fresh.map((j) => j.id)]);
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoadingMore(false);
    }
  }

  function reset() {
    setStage(STAGE.UPLOAD);
    setCandidate(null);
    setJobs([]);
    setPossible([]);
    setMessage("");
    setSeenIds([]);
    setVariation(0);
    setError("");
  }

  return (
    <main className="min-h-screen py-8 px-5 pb-20">
      <div className="max-w-[1000px] mx-auto bg-white rounded-2xl overflow-hidden shadow-[0_10px_34px_rgba(15,23,42,.12)]">
        {/* Nav */}
        <div className="flex items-center justify-between px-7 py-4 border-b border-line">
          <button
            onClick={reset}
            className="flex items-center gap-2.5 bg-transparent border-none cursor-pointer"
          >
            <Logo />
            <Wordmark />
          </button>
          <div className="flex items-center gap-4">
            <span className="text-muted text-sm hidden sm:inline">How it works</span>
            <a
              className="flex items-center justify-center w-8 h-8 rounded-lg bg-ink text-white no-underline"
              href={X_URL}
              target="_blank"
              rel="noopener noreferrer"
              title="Reach us on X"
            >
              <XIcon className="w-[15px] h-[15px]" />
            </a>
          </div>
        </div>

        {stage === STAGE.UPLOAD ? (
          <UploadScreen onUpload={handleUpload} error={error} />
        ) : null}

        {stage === STAGE.PROCESSING ? (
          <div className="px-7 py-14">
            <ProcessingState />
          </div>
        ) : null}

        {stage === STAGE.RESULTS ? (
          <ResultsScreen
            candidate={candidate}
            jobs={jobs}
            possible={possible}
            message={message}
            error={error}
            loadingMore={loadingMore}
            onSearchAgain={handleSearchAgain}
          />
        ) : null}

        <PrivacyNotice />
      </div>
    </main>
  );
}

function UploadScreen({ onUpload, error }) {
  return (
    <>
      <div
        className="px-7 pt-14 pb-10 text-center"
        style={{
          background:
            "radial-gradient(1200px 300px at 50% -40%, #ECFDF5, #ffffff)",
        }}
      >
        <h1 className="text-[34px] leading-tight mx-auto mb-3 max-w-[560px] font-bold tracking-tight">
          Upload your CV.<br />
          Get <span className="brand-text">10 remote jobs</span> that fit.
        </h1>
        <p className="text-muted text-base max-w-[460px] mx-auto mb-8">
          No sign-up. No profiles to fill in. Drop your CV and our agents match
          you against fresh remote roles in under a minute.
        </p>

        <CVUploader onSubmit={onUpload} isLoading={false} />

        {error ? (
          <p className="text-red-600 font-semibold mt-5">{error}</p>
        ) : null}
      </div>

      {/* How it works */}
      <div className="flex gap-4 justify-center px-7 py-7 flex-wrap">
        {[
          { n: 1, t: "Upload", d: "Drop your CV" },
          { n: 2, t: "Match", d: "Agents score fresh remote jobs against your profile" },
          { n: 3, t: "Apply", d: "Get your top 10 with links to the original posting" },
        ].map((step) => (
          <div key={step.n} className="flex-1 min-w-[150px] max-w-[210px] text-center text-muted text-[13px]">
            <div className="w-[30px] h-[30px] rounded-full bg-tint text-brand font-extrabold flex items-center justify-center mx-auto mb-2">
              {step.n}
            </div>
            <b className="block text-ink text-sm mb-1">{step.t}</b>
            {step.d}
          </div>
        ))}
      </div>
    </>
  );
}

function ResultsScreen({
  candidate,
  jobs,
  possible,
  message,
  error,
  loadingMore,
  onSearchAgain,
}) {
  const skills = candidate?.skills || [];
  const shownSkills = skills.slice(0, 4);
  const extra = skills.length - shownSkills.length;

  return (
    <div className="pb-4">
      <div className="px-7 pt-6 pb-2">
        <h3 className="text-[22px] mb-2.5 font-bold">
          {jobs.length > 0
            ? `${jobs.length} remote ${jobs.length === 1 ? "job" : "jobs"} matched to your profile`
            : "No strong matches right now"}
        </h3>
        <div className="flex flex-wrap gap-1.5 mb-1.5">
          <span className="bg-tint2 text-[#047857] text-[12px] font-semibold px-2.5 py-1 rounded-full">
            {candidate?.professional_title}
          </span>
          <span className="bg-tint2 text-[#047857] text-[12px] font-semibold px-2.5 py-1 rounded-full">
            {candidate?.seniority}-level
          </span>
          {candidate?.years_experience ? (
            <span className="bg-tint2 text-[#047857] text-[12px] font-semibold px-2.5 py-1 rounded-full">
              {candidate.years_experience} yrs
            </span>
          ) : null}
          {shownSkills.map((skill) => (
            <span
              key={skill}
              className="bg-slate-100 text-slate-500 text-[12px] px-2.5 py-1 rounded-full"
            >
              {skill}
            </span>
          ))}
          {extra > 0 ? (
            <span className="bg-slate-100 text-slate-500 text-[12px] px-2.5 py-1 rounded-full">
              +{extra} more
            </span>
          ) : null}
        </div>
      </div>

      {message ? (
        <p className="text-muted text-[13px] px-7 pb-3.5">{message}</p>
      ) : (
        <p className="text-muted text-[13px] px-7 pb-3.5">
          Sorted by match score · updated from today&apos;s job pull
        </p>
      )}

      {error ? (
        <p className="text-red-600 font-semibold px-7 pb-3">{error}</p>
      ) : null}

      <div className="px-7">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}

        {possible.length > 0 ? (
          <>
            <h4 className="text-base font-bold mt-6 mb-3">
              {possible.length} possible {possible.length === 1 ? "match" : "matches"}
            </h4>
            {possible.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </>
        ) : null}
      </div>

      <div className="px-7">
        <SocialCTA />
      </div>

      <div className="text-center px-7 pb-4">
        <button
          onClick={onSearchAgain}
          disabled={loadingMore}
          className="bg-white text-brand border border-dash font-bold text-sm rounded-xl px-6 py-3 disabled:opacity-60"
        >
          {loadingMore ? "Finding more…" : "Find more jobs"}
        </button>
      </div>
    </div>
  );
}
