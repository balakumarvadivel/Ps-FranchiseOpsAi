export function GlassCard({ className = "", children, ...props }) {
  return (
    <div
      className={`rounded-2xl border border-slate-200/70 dark:border-slate-700/60 bg-white/70 dark:bg-slate-900/60 backdrop-blur-xl shadow-[0_8px_30px_-12px_rgba(30,41,59,0.15)] dark:shadow-[0_8px_30px_-12px_rgba(0,0,0,0.4)] ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
