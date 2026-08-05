import { Sparkles } from "lucide-react";
import { GlassCard } from "../common/GlassCard";
import { toneClasses } from "../../utils/formatters";

export function AIInsightCard({ icon: Icon = Sparkles, tone = "info", title, detail, time }) {
  const dotTone = {
    success: "bg-emerald-500", warning: "bg-amber-500", danger: "bg-rose-500", info: "bg-blue-500",
  }[tone];

  return (
    <div className="relative pl-6">
      <div className={`absolute -left-1.5 top-0.5 w-[18px] h-[18px] rounded-full flex items-center justify-center ring-4 ring-white dark:ring-slate-900 ${dotTone}`}>
        <Icon size={10} className="text-white" />
      </div>
      <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{title}</p>
      {detail && <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{detail}</p>}
      {time && <p className="text-[11px] text-slate-400 mt-1">{time}</p>}
    </div>
  );
}

export function AISummaryBanner({ title = "AI executive summary", text, badges = [] }) {
  return (
    <GlassCard className="p-5 bg-gradient-to-br from-blue-600 via-blue-600 to-purple-700 border-none text-white relative overflow-hidden">
      <div className="absolute -right-10 -top-10 w-40 h-40 rounded-full bg-white/10 blur-2xl" />
      <div className="flex items-start gap-3 relative">
        <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center shrink-0">
          <Sparkles size={18} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="font-semibold">{title}</h2>
            <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-white/15">Auto-generated</span>
          </div>
          <p className="text-sm text-white/90 leading-relaxed">{text}</p>
          {badges.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3 text-[11px]">
              {badges.map((b, i) => (
                <span key={i} className="px-2.5 py-1 rounded-full bg-white/15">{b}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
}
