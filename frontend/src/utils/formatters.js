export const currency = (n = 0) => `₹${Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

export const compactCurrency = (n = 0) => {
  const num = Number(n);
  if (num >= 1e7) return `₹${(num / 1e7).toFixed(2)}Cr`;
  if (num >= 1e5) return `₹${(num / 1e5).toFixed(2)}L`;
  return `₹${num.toLocaleString("en-IN")}`;
};

export const percent = (n = 0, decimals = 1) => `${Number(n).toFixed(decimals)}%`;

export const healthStatus = (score) => {
  if (score >= 75) return { label: "Healthy", tone: "success" };
  if (score >= 50) return { label: "Average", tone: "warning" };
  return { label: "Critical", tone: "danger" };
};

export const toneClasses = {
  success: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20",
  warning: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20",
  danger: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-500/10 dark:text-rose-400 dark:border-rose-500/20",
  info: "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20",
};

export const toneDot = {
  success: "bg-emerald-500",
  warning: "bg-amber-500",
  danger: "bg-rose-500",
  info: "bg-blue-500",
};

export const priorityTone = { critical: "danger", high: "warning", medium: "info", low: "success" };
