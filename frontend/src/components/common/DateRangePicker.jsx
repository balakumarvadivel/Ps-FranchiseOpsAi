import { useState } from "react";
import { CalendarDays } from "lucide-react";

/**
 * Simple, self-contained date range picker (no external deps).
 * value: { from: "YYYY-MM-DD"|null, to: "YYYY-MM-DD"|null }
 */
export function DateRangePicker({ value, onChange }) {
  const [open, setOpen] = useState(false);
  const { from, to } = value || {};

  const label = from && to ? `${from} → ${to}` : "Date Range";

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-xs rounded-lg border border-slate-200 dark:border-slate-700 px-2.5 py-2 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 bg-white dark:bg-slate-900"
      >
        <CalendarDays size={13} /> {label}
      </button>

      {open && (
        <div className="absolute right-0 z-20 mt-2 w-64 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-xl p-3 space-y-2">
          <div>
            <label className="text-[11px] text-slate-400 block mb-1">From</label>
            <input type="date" value={from || ""} onChange={(e) => onChange({ from: e.target.value, to })}
              className="w-full text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2 py-1.5" />
          </div>
          <div>
            <label className="text-[11px] text-slate-400 block mb-1">To</label>
            <input type="date" value={to || ""} onChange={(e) => onChange({ from, to: e.target.value })}
              className="w-full text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-2 py-1.5" />
          </div>
          <div className="flex justify-between pt-1">
            <button onClick={() => { onChange({ from: null, to: null }); setOpen(false); }}
              className="text-[11px] text-slate-400 hover:text-slate-600">Clear</button>
            <button onClick={() => setOpen(false)}
              className="text-[11px] font-medium text-blue-600 dark:text-blue-400 hover:underline">Apply</button>
          </div>
        </div>
      )}
    </div>
  );
}
