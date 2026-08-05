import { motion } from "framer-motion";
import { ArrowUpRight, ArrowDownRight, Sparkles } from "lucide-react";
import { GlassCard } from "./GlassCard";
import { Sparkline } from "../charts/Sparkline";

export function KPICard({ label, value, icon: Icon, trend, up = true, color = "#3b82f6", spark, aiNote, delay = 0 }) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay }} whileHover={{ y: -4 }}>
      <GlassCard className="p-4 h-full flex flex-col">
        <div className="flex items-center justify-between mb-3">
          {Icon && (
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: `${color}1A` }}>
              <Icon size={16} style={{ color }} />
            </div>
          )}
          {trend && (
            <span className={`flex items-center gap-0.5 text-[11px] font-semibold ${up ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
              {up ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />} {trend}
            </span>
          )}
        </div>
        <p className="text-xl font-bold text-slate-900 dark:text-white tabular-nums">{value}</p>
        <p className="text-[11px] text-slate-500 dark:text-slate-400">{label}</p>
        {spark && (
          <div className="mt-auto pt-2 -mx-1">
            <Sparkline data={spark} color={color} />
          </div>
        )}
        {aiNote && (
          <span className="mt-2 inline-flex items-center gap-1 text-[10px] font-medium px-2 py-1 rounded-full bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 w-fit">
            <Sparkles size={10} /> {aiNote}
          </span>
        )}
      </GlassCard>
    </motion.div>
  );
}
