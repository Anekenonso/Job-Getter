"use client";

import { useEffect, useState } from "react";

// Staged progress display. The steps are illustrative of the real pipeline
// (parse → search → match → rank) and advance on a timer while the request runs.
const STEPS = [
  { label: "CV parsed", hint: "reading your skills" },
  { label: "Searched the job pool", hint: "fresh remote roles" },
  { label: "Matching against your profile", hint: "scoring shortlist" },
  { label: "Ranking your top matches", hint: "almost there" },
];

export default function ProcessingState() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setActive((prev) => Math.min(prev + 1, STEPS.length - 1));
    }, 1400);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="max-w-[520px] mx-auto py-4">
      <h3 className="text-[22px] text-center mb-1.5 font-bold">
        Analyzing your CV…
      </h3>
      <p className="text-center text-muted text-sm mb-7">
        Hang tight — this usually takes under a minute.
      </p>

      <ul className="list-none p-0 mb-6 space-y-2.5">
        {STEPS.map((step, i) => {
          const state = i < active ? "done" : i === active ? "active" : "wait";
          return (
            <li
              key={step.label}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl border text-[15px] ${
                state === "active"
                  ? "border-dash bg-tint"
                  : "border-line"
              } ${state === "wait" ? "text-slate-400" : ""}`}
            >
              <span
                className={`w-6 h-6 rounded-full flex items-center justify-center text-[13px] font-extrabold flex-none ${
                  state === "done"
                    ? "bg-[#dcfce7] text-[#16a34a]"
                    : state === "active"
                    ? "bg-brand text-white"
                    : "bg-slate-100 text-slate-300"
                }`}
              >
                {state === "done" ? "✓" : state === "active" ? "⟳" : "○"}
              </span>
              {step.label}
              <small className="ml-auto text-slate-400 text-xs">
                {step.hint}
              </small>
            </li>
          );
        })}
      </ul>

      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div
          className="h-full bg-brand-grad transition-all duration-700"
          style={{ width: `${((active + 1) / STEPS.length) * 100}%` }}
        />
      </div>
      <p className="text-center text-slate-400 text-[13px] mt-3.5">
        skills · experience · seniority · role fit · remote match
      </p>
    </div>
  );
}
