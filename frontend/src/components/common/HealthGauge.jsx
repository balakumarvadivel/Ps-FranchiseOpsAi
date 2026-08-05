import { motion } from "framer-motion";

function colorFor(score) {
  if (score >= 75) return "#10b981";
  if (score >= 50) return "#f59e0b";
  return "#f43f5e";
}

export function HealthGauge({ score = 0, size = 140, label = "Health Score" }) {
  const radius = (size - 24) / 2;
  const circumference = 2 * Math.PI * radius;
  const color = colorFor(score);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={radius} stroke="currentColor" strokeWidth="12" fill="none"
                  className="text-slate-100 dark:text-slate-800" />
          <motion.circle
            cx={size / 2} cy={size / 2} r={radius} stroke={color} strokeWidth="12" fill="none" strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - (score / 100) * circumference }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold" style={{ color }}>{Math.round(score)}</span>
          <span className="text-[10px] text-slate-400">/ 100</span>
        </div>
      </div>
      {label && <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">{label}</p>}
    </div>
  );
}
