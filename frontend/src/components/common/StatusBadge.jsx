import { toneClasses, toneDot } from "../../utils/formatters";

export function StatusBadge({ label, tone = "info" }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${toneClasses[tone]}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${toneDot[tone]}`} />
      {label}
    </span>
  );
}
