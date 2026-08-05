import { motion } from "framer-motion";

export function ProgressBar({ pct = 0, colorClass = "from-blue-500 to-purple-500" }) {
  return (
    <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className={`h-full rounded-full bg-gradient-to-r ${colorClass}`}
      />
    </div>
  );
}
