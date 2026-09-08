const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function handle(response) {
  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: "Something went wrong. Please try again." }));
    throw new Error(err.detail || "Something went wrong. Please try again.");
  }
  return response.json();
}

export async function analyzeCV(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE}/api/analyze-cv`, {
    method: "POST",
    body: formData,
  });
  return handle(response);
}

export async function searchAgain({ candidateProfile, excludeIds, variation }) {
  const response = await fetch(`${API_BASE}/api/search-again`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_profile: candidateProfile,
      exclude_ids: excludeIds || [],
      variation: variation || 1,
    }),
  });
  return handle(response);
}
