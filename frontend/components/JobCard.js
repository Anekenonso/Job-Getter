import MatchScore from "./MatchScore";

export default function JobCard({ job }) {
  const metaParts = [];
  if (job.location) metaParts.push(job.location);
  if (job.salary) metaParts.push(job.salary);
  else metaParts.push("Salary not listed");

  return (
    <div className="flex gap-4 border border-line rounded-2xl p-4 mb-3">
      <MatchScore score={job.match_score} />

      <div className="flex-1 min-w-0">
        <p className="text-base font-bold m-0">{job.title}</p>
        <p className="text-muted text-[13px] mt-0.5 mb-2">
          {job.company} ·{" "}
          <span className="text-[#16A34A] font-semibold">
            {job.remote ? "Remote" : "On-site"}
          </span>
          {job.location_restriction ? ` — ${job.location_restriction}` : ""} ·{" "}
          {job.salary || "Salary not listed"}
        </p>

        {job.matching_skills?.length ? (
          <div className="flex flex-wrap gap-1.5 mb-2">
            {job.matching_skills.slice(0, 5).map((skill) => (
              <span
                key={skill}
                className="bg-tint2 text-[#065F46] text-[11px] px-2.5 py-0.5 rounded-md"
              >
                {skill}
              </span>
            ))}
          </div>
        ) : null}

        <p className="text-[13px] text-slate-700 bg-[#F0FDF9] border-l-[3px] border-brand px-3 py-1.5 rounded-r-lg mb-2.5">
          <b>Why this matches you:</b> {job.match_reason}
        </p>

        {job.gaps?.length ? (
          <ul className="text-[12px] text-amber-700 mb-2.5 list-none p-0 space-y-0.5">
            {job.gaps.map((gap) => (
              <li key={gap}>• {gap}</li>
            ))}
          </ul>
        ) : null}

        <div className="flex items-center justify-between">
          <span className="text-slate-400 text-xs">via {job.source}</span>
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="bg-brand text-white font-bold text-[13px] rounded-lg px-4 py-2 no-underline"
          >
            View &amp; apply →
          </a>
        </div>
      </div>
    </div>
  );
}
