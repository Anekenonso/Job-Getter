"use client";

import { useRef, useState } from "react";

const ACCEPTED = [".pdf", ".docx"];
const MAX_MB = 5;

export default function CVUploader({ onSubmit, isLoading }) {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [localError, setLocalError] = useState("");

  function validate(candidate) {
    if (!candidate) return "Please choose a CV file.";
    const lower = candidate.name.toLowerCase();
    if (!ACCEPTED.some((ext) => lower.endsWith(ext))) {
      return "We couldn't read this file. Please upload a PDF or DOCX CV.";
    }
    if (candidate.size > MAX_MB * 1024 * 1024) {
      return `File exceeds the ${MAX_MB} MB limit.`;
    }
    return "";
  }

  function selectFile(candidate) {
    const err = validate(candidate);
    setLocalError(err);
    setFile(err ? null : candidate);
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);
    const dropped = event.dataTransfer.files?.[0];
    if (dropped) selectFile(dropped);
  }

  function handleSubmit() {
    if (!file) {
      setLocalError("Please choose a CV file.");
      return;
    }
    onSubmit(file);
  }

  return (
    <div className="max-w-[520px] mx-auto">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition ${
          dragging ? "border-brand bg-tint2" : "border-dash bg-tint"
        }`}
      >
        <div className="w-[52px] h-[52px] rounded-xl bg-tint2 flex items-center justify-center mx-auto mb-3.5 text-2xl">
          📄
        </div>
        <b className="text-base">
          {file ? file.name : "Drag your CV here, or browse"}
        </b>
        <div className="text-slate-400 text-[13px] mt-1.5">
          PDF or DOCX · max {MAX_MB} MB
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => selectFile(e.target.files?.[0] || null)}
        />
      </div>

      {localError ? (
        <p className="text-red-600 text-sm font-semibold mt-3 text-center">
          {localError}
        </p>
      ) : null}

      <button
        onClick={handleSubmit}
        disabled={isLoading}
        className="mt-4 w-full bg-brand text-white font-bold text-sm rounded-xl py-3.5 disabled:opacity-60"
      >
        {file ? (isLoading ? "Finding your matches…" : "Find my jobs") : "Browse files"}
      </button>

      <div className="flex items-center gap-2 justify-center text-[#16A34A] text-[13px] mt-6">
        <span>🔒</span>
        <span>
          We never store your CV or personal data — it&apos;s processed in memory
          and discarded.
        </span>
      </div>
    </div>
  );
}
