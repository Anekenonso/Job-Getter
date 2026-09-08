export default function MatchScore({ score }) {
  // Green ring for strong matches, teal for softer ones.
  const strong = score >= 85;
  return (
    <div className="flex-none w-[58px] text-center">
      <div
        className={`w-[52px] h-[52px] rounded-full mx-auto mb-1 flex items-center justify-center font-extrabold text-[15px] text-white ${
          strong ? "bg-brand" : "bg-brand-teal"
        }`}
        style={{ background: strong ? "#059669" : "#0D9488" }}
      >
        {score}%
      </div>
      <div className="text-[10px] text-slate-400 uppercase tracking-wide">
        match
      </div>
    </div>
  );
}
