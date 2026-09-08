export function Logo({ size = 26 }) {
  return (
    <svg viewBox="0 0 96 96" width={size} height={size} style={{ display: "block" }}>
      <defs>
        <linearGradient id="jgGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#059669" />
          <stop offset=".5" stopColor="#10B981" />
          <stop offset="1" stopColor="#14B8A6" />
        </linearGradient>
      </defs>
      <rect width="96" height="96" rx="22" fill="url(#jgGrad)" />
      <circle cx="48" cy="48" r="27" fill="none" stroke="#fff" strokeWidth="6" />
      <circle cx="48" cy="48" r="14" fill="none" stroke="#fff" strokeWidth="6" />
      <circle cx="48" cy="48" r="5.5" fill="#fff" />
    </svg>
  );
}

export function Wordmark() {
  return (
    <span className="font-extrabold text-[17px]">
      Job<span className="brand-text">-Getter</span>
    </span>
  );
}

export function XIcon({ className = "w-4 h-4" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );
}

// Placeholder handle — swap before launch.
export const X_HANDLE = "JobGetter";
export const X_URL = `https://x.com/${X_HANDLE}`;
