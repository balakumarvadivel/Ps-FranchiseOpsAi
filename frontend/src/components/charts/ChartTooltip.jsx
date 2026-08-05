export function ChartTooltip({ active, payload, label, prefix = "" }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white/95 dark:bg-slate-900/95 backdrop-blur px-3 py-2 shadow-lg text-xs">
      <p className="font-medium text-slate-500 dark:text-slate-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="flex items-center gap-2" style={{ color: p.color }}>
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-slate-600 dark:text-slate-300">{p.name}:</span>
          <span className="font-semibold">{prefix}{typeof p.value === "number" ? Math.round(p.value).toLocaleString("en-IN") : p.value}</span>
        </p>
      ))}
    </div>
  );
}
