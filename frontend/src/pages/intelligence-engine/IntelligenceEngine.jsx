import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Brain, TrendingUp, TrendingDown, HeartPulse } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { GlassCard } from "../../components/common/GlassCard";
import { HealthGauge } from "../../components/common/HealthGauge";
import { AISummaryBanner } from "../../components/ai/AIInsightCard";
import { ProgressBar } from "../../components/common/ProgressBar";
import { CardSkeleton, ErrorState } from "../../components/common/States";

import { aiService } from "../../services/aiService";
import { outletService } from "../../services/outletService";
import { compactCurrency } from "../../utils/formatters";

export default function IntelligenceEngine() {
  const [outletId, setOutletId] = useState("");

  const summaryQ = useQuery({ queryKey: ["ai", "executive-summary"], queryFn: aiService.executiveSummary });
  const outletsQ = useQuery({ queryKey: ["outlets", "list"], queryFn: () => outletService.list() });
  const healthQ = useQuery({
    queryKey: ["ai", "health-score", outletId],
    queryFn: () => aiService.outletHealthScore(outletId),
    enabled: !!outletId,
  });

  const breakdownLabels = {
    sales_performance: "Sales Performance", inventory_availability: "Inventory Availability",
    staff_productivity: "Staff Productivity", audit_compliance: "Audit Compliance", profit_margin: "Profit Margin",
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI BRAIN · CROSS-DOMAIN"
        title="Franchise Intelligence Engine"
        subtitle="Combines sales, inventory, staff, marketing, and audit data into one business health score and executive summary."
        actions={
          <button onClick={() => summaryQ.refetch()} className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
            <RefreshCw size={15} />
          </button>
        }
      />

      {summaryQ.isLoading ? <CardSkeleton /> : summaryQ.isError ? (
        <ErrorState message="Couldn't generate the executive summary." onRetry={summaryQ.refetch} />
      ) : (
        <AISummaryBanner
          text={summaryQ.data.summary}
          badges={[
            `Revenue: ${compactCurrency(summaryQ.data.total_revenue)}`,
            `Growth: ${summaryQ.data.revenue_growth_percent}%`,
            `Health: ${summaryQ.data.overall_health_score}/100`,
          ]}
        />
      )}

      {summaryQ.data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <GlassCard className="p-5 flex flex-col items-center">
            <HealthGauge score={summaryQ.data.overall_health_score} label="Overall Business Health" />
          </GlassCard>
          <GlassCard className="p-5 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center shrink-0">
              <TrendingUp size={18} className="text-emerald-500" />
            </div>
            <div>
              <p className="text-[11px] text-slate-400">Best outlet</p>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{summaryQ.data.best_outlet.name}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">Health {summaryQ.data.best_outlet.health_score}/100</p>
            </div>
          </GlassCard>
          <GlassCard className="p-5 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-50 dark:bg-rose-500/10 flex items-center justify-center shrink-0">
              <TrendingDown size={18} className="text-rose-500" />
            </div>
            <div>
              <p className="text-[11px] text-slate-400">Worst outlet</p>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{summaryQ.data.worst_outlet.name}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">Health {summaryQ.data.worst_outlet.health_score}/100</p>
            </div>
          </GlassCard>
        </div>
      )}

      <GlassCard className="p-5">
        <div className="flex items-center gap-2 mb-1">
          <HeartPulse size={16} className="text-blue-500" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Root Cause Analysis — per outlet</h2>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Select an outlet to see its full health score breakdown</p>

        <select value={outletId} onChange={(e) => setOutletId(e.target.value)}
          className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2 mb-4">
          <option value="">Select an outlet...</option>
          {(outletsQ.data || []).map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
        </select>

        {outletId && (
          healthQ.isLoading ? <CardSkeleton /> : healthQ.isError ? (
            <ErrorState message="Couldn't load health breakdown." onRetry={healthQ.refetch} />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3">
              {Object.entries(breakdownLabels).map(([key, label]) => (
                <div key={key}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-slate-500 dark:text-slate-400">{label}</span>
                    <span className="font-medium text-slate-700 dark:text-slate-200">{healthQ.data[key]}%</span>
                  </div>
                  <ProgressBar pct={healthQ.data[key]} colorClass={healthQ.data[key] >= 75 ? "from-emerald-400 to-emerald-500" : healthQ.data[key] >= 50 ? "from-amber-400 to-amber-500" : "from-rose-400 to-rose-500"} />
                </div>
              ))}
            </div>
          )
        )}
      </GlassCard>
    </div>
  );
}
