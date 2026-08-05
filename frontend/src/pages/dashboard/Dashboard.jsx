import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Wand2, Download, DollarSign, ShoppingCart, TrendingUp, Building2, Users, Boxes, Bell, HeartPulse } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { AISummaryBanner } from "../../components/ai/AIInsightCard";
import { ChartTooltip } from "../../components/charts/ChartTooltip";
import { CardSkeleton, ErrorState } from "../../components/common/States";

import { outletService, salesService } from "../../services/outletService";
import { aiService } from "../../services/aiService";
import { alertService } from "../../services/aiService";
import { compactCurrency } from "../../utils/formatters";

export default function Dashboard() {
  const summaryQ = useQuery({ queryKey: ["ai", "executive-summary"], queryFn: aiService.executiveSummary });
  const rankingQ = useQuery({ queryKey: ["outlets", "ranking"], queryFn: () => outletService.ranking(30) });
  const trendQ = useQuery({ queryKey: ["sales", "trend", "Monthly"], queryFn: () => salesService.trend({ period: "Monthly" }) });
  const alertsQ = useQuery({ queryKey: ["alerts", "all"], queryFn: () => alertService.list({}) });

  const outlets = rankingQ.data || [];
  const totalRevenue = outlets.reduce((s, o) => s + o.revenue, 0);
  const totalOrders = outlets.reduce((s, o) => s + o.orders, 0);
  const avgGrowth = outlets.length ? (outlets.reduce((s, o) => s + o.growth_percent, 0) / outlets.length).toFixed(1) : 0;
  const avgHealth = outlets.length ? Math.round(outlets.reduce((s, o) => s + o.health_score, 0) / outlets.length) : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="EXECUTIVE OVERVIEW · LIVE DATA"
        title="Franchise Executive Dashboard"
        subtitle="Cross-domain view of revenue, outlets, staff, marketing, and audit health across your network."
        actions={
          <>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25">
              <Wand2 size={15} /> AI Analysis
            </button>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
              <Download size={15} /> Export Report
            </button>
            <button onClick={() => { summaryQ.refetch(); rankingQ.refetch(); trendQ.refetch(); }}
              className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
              <RefreshCw size={15} />
            </button>
          </>
        }
      />

      {summaryQ.isLoading && <CardSkeleton />}
      {summaryQ.isError && <ErrorState message="Couldn't load the AI executive summary." onRetry={summaryQ.refetch} />}
      {summaryQ.data && (
        <AISummaryBanner
          text={summaryQ.data.summary}
          badges={[
            `Best: ${summaryQ.data.best_outlet.name}`,
            `Watch: ${summaryQ.data.worst_outlet.name}`,
            `Critical outlets: ${summaryQ.data.critical_outlet_count}`,
          ]}
        />
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <KPICard label="Total Revenue" value={compactCurrency(totalRevenue)} icon={DollarSign} color="#3b82f6" trend={`${avgGrowth}%`} up={avgGrowth >= 0} />
        <KPICard label="Total Sales" value={totalOrders.toLocaleString("en-IN")} icon={ShoppingCart} color="#8b5cf6" trend="30d" />
        <KPICard label="Active Outlets" value={outlets.length} icon={Building2} color="#06b6d4" trend="live" />
        <KPICard label="Avg Monthly Growth" value={`${avgGrowth}%`} icon={TrendingUp} color="#10b981" trend="vs prior 30d" up={avgGrowth >= 0} />
        <KPICard label="Franchise Health Score" value={`${avgHealth}/100`} icon={HeartPulse} color="#ec4899" trend="network avg" />
        <KPICard label="Open Alerts" value={alertsQ.data?.length ?? "—"} icon={Bell} color="#f59e0b" trend="live" />
      </div>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Revenue Trend</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Monthly revenue across all outlets in scope</p>
        {trendQ.isLoading ? (
          <CardSkeleton />
        ) : trendQ.isError ? (
          <ErrorState message="Couldn't load the sales trend." onRetry={trendQ.refetch} />
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trendQ.data} margin={{ left: -10, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" className="text-slate-100 dark:text-slate-800" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => compactCurrency(v)} width={60} />
              <Tooltip content={<ChartTooltip prefix="₹" />} />
              <Line type="monotone" dataKey="revenue" name="Revenue" stroke="#3b82f6" strokeWidth={3} dot={{ r: 3 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </GlassCard>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Outlet Comparison</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Revenue, growth and health score, ranked</p>
        {rankingQ.isLoading ? (
          <CardSkeleton />
        ) : rankingQ.isError ? (
          <ErrorState message="Couldn't load outlet rankings." onRetry={rankingQ.refetch} />
        ) : (
          <div className="overflow-x-auto -mx-1 px-1">
            <table className="w-full text-sm min-w-[600px]">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-wide text-slate-400 border-b border-slate-200 dark:border-slate-800">
                  <th className="py-2.5 pr-4 font-medium">Outlet</th>
                  <th className="py-2.5 pr-4 font-medium">Revenue</th>
                  <th className="py-2.5 pr-4 font-medium">Growth</th>
                  <th className="py-2.5 pr-4 font-medium">Health</th>
                  <th className="py-2.5 pr-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {outlets.slice(0, 8).map((o) => (
                  <tr key={o.outlet_id} className="border-b border-slate-100 dark:border-slate-800/60">
                    <td className="py-2.5 pr-4 font-medium text-slate-800 dark:text-slate-100">{o.name}</td>
                    <td className="py-2.5 pr-4 tabular-nums">{compactCurrency(o.revenue)}</td>
                    <td className={`py-2.5 pr-4 font-medium ${o.growth_percent >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
                      {o.growth_percent >= 0 ? "+" : ""}{o.growth_percent}%
                    </td>
                    <td className="py-2.5 pr-4">{o.health_score}</td>
                    <td className="py-2.5 pr-4 text-slate-500 dark:text-slate-400">{o.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
