import { motion } from "framer-motion";

export function PageHeader({ eyebrow, title, subtitle, actions }) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
      className="flex flex-col lg:flex-row lg:items-end justify-between gap-4"
    >
      <div>
        {eyebrow && (
          <div className="flex items-center gap-2 text-xs font-medium text-blue-600 dark:text-blue-400 mb-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /> {eyebrow}
          </div>
        )}
        <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">{title}</h1>
        {subtitle && <p className="text-sm text-slate-500 dark:text-slate-400 mt-1.5 max-w-2xl">{subtitle}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </motion.div>
  );
}
