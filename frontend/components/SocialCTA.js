import { XIcon, X_URL, X_HANDLE } from "./Brand";

// Placed at the peak-goodwill moment: right after results are delivered.
export default function SocialCTA() {
  return (
    <div className="flex items-center justify-between gap-4 flex-wrap bg-tint border border-dash rounded-2xl px-5 py-4 my-6">
      <div>
        <div className="font-extrabold text-[15px]">🎯 Get hired? Tag us on X</div>
        <div className="text-muted text-[13px] mt-0.5 max-w-[430px]">
          Follow <b>@{X_HANDLE}</b> for product updates, and DM us anytime —
          questions, feedback, or a hired shout-out. Our inbox is always open.
        </div>
      </div>
      <a
        className="inline-flex items-center gap-2 bg-ink text-white font-bold text-[13px] no-underline px-4 py-3 rounded-xl whitespace-nowrap"
        href={X_URL}
        target="_blank"
        rel="noopener noreferrer"
      >
        <XIcon className="w-4 h-4" />
        Follow @{X_HANDLE}
      </a>
    </div>
  );
}
