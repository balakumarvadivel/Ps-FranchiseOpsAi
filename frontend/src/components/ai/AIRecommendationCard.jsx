import { Sparkles } from "lucide-react";
import { StatusBadge } from "../common/StatusBadge";
import { priorityTone } from "../../utils/formatters";

export function AIRecommendationCard({ rec, onStatusChange }) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-800 p-3.5">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-3 min-w-0">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-500/10 dark:to-purple-500/10 flex items-center justify-center shrink-0">
            <Sparkles size={14} className="text-blue-600 dark:text-blue-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{rec.title}</p>
            {rec.description && <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{rec.description}</p>}
          </div>
        </div>
        <StatusBadge label={rec.priority} tone={priorityTone[rec.priority] || "info"} />
      </div>

      {onStatusChange && (
        <div className="flex gap-2 mt-3">
          {rec.status !== "in_progress" && (
            <button onClick={() => onStatusChange(rec.id, "in_progress")}
                    className="text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800">
              Start
            </button>
          )}
          <button onClick={() => onStatusChange(rec.id, "resolved")}
                  className="text-xs font-medium px-3 py-1.5 rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600">
            Mark resolved
          </button>
          <button onClick={() => onStatusChange(rec.id, "dismissed")}
                  className="text-xs font-medium px-3 py-1.5 rounded-lg text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800">
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
}
