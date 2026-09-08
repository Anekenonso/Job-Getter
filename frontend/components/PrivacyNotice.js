import { XIcon, X_URL, X_HANDLE } from "./Brand";

export default function PrivacyNotice() {
  return (
    <div className="flex items-center justify-between gap-3 flex-wrap px-7 py-4 border-t border-line text-muted text-[13px]">
      <span>© 2026 Job-Getter · No accounts · nothing stored.</span>
      <a
        className="inline-flex items-center gap-2 font-bold text-ink no-underline"
        href={X_URL}
        target="_blank"
        rel="noopener noreferrer"
      >
        Questions? Reach out
        <span className="flex items-center justify-center w-[26px] h-[26px] rounded-md bg-ink text-white">
          <XIcon className="w-[13px] h-[13px]" />
        </span>
        @{X_HANDLE}
      </a>
    </div>
  );
}
