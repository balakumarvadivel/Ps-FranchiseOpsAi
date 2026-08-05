import { AlertTriangle, Inbox, RefreshCw } from "lucide-react";

export function LoadingSkeleton({ rows = 3, className = "" }) {
  return (
    <div className={`space-y-3 animate-pulse ${className}`}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-4 rounded-lg bg-slate-100 dark:bg-slate-800" style={{ width: `${85 - i * 10}%` }} />
      ))}
    </div>
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-2xl border border-slate-200/70 dark:border-slate-700/60 bg-white/70 dark:bg-slate-900/60 p-4 animate-pulse">
      <div className="w-9 h-9 rounded-xl bg-slate-100 dark:bg-slate-800 mb-3" />
      <div className="h-5 w-2/3 rounded bg-slate-100 dark:bg-slate-800 mb-2" />
      <div className="h-3 w-1/2 rounded bg-slate-100 dark:bg-slate-800" />
    </div>
  );
}

export function EmptyState({ title = "Nothing here yet", subtitle }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-3">
        <Inbox size={20} className="text-slate-400" />
      </div>
      <p className="text-sm font-medium text-slate-600 dark:text-slate-300">{title}</p>
      {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
    </div>
  );
}

export function ErrorState({ message = "Something went wrong.", onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-12 h-12 rounded-full bg-rose-50 dark:bg-rose-500/10 flex items-center justify-center mb-3">
        <AlertTriangle size={20} className="text-rose-500" />
      </div>
      <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{message}</p>
      <p className="text-xs text-slate-400 mt-1">Check that the backend API is running and reachable.</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-3 flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800">
          <RefreshCw size={12} /> Retry
        </button>
      )}
    </div>
  );
}
