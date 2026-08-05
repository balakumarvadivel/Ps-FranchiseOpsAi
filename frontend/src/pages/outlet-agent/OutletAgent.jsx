import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Wand2, GitCompareArrows, Download, Store, TrendingUp, DollarSign, HeartPulse } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Line } from "recharts";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { HealthGauge } from "../../components/common/HealthGauge";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { ChartTooltip } from "../../components/charts/ChartTooltip";
import { CardSkeleton, ErrorState } from "../../components/common/States";

import { outletService, salesService } from "../../services/outletService";
import { aiService } from "../../services/aiService";
import { compactCurrency } from "../../utils/formatters";

const PERIODS = ["Daily", "Weekly", "Monthly", "Yearly"];

export default function OutletAgent() {
  const [period, setPeriod] = useState("Monthly");
  const [forecastRange, setForecastRange] = useState("30D");

  const rankingQ = useQuery({ queryKey: ["outlets", "ranking", 30], queryFn: () => outletService.ranking(30) });
  const trendQ = useQuery({ queryKey: ["sales", "trend", period], queryFn: () => salesService.trend({ period }) });
  const forecastQ = useQuery({
    queryKey: ["ai", "forecast", forecastRange],
    queryFn: () => aiService.forecastRevenue({ range: forecastRange }),
    retry: false,
  });

  const outlets = rankingQ.data || [];
  const totalRevenue = outlets.reduce((s, o) => s + o.revenue, 0);
  const avgGrowth = outlets.length ? (outlets.reduce((s, o) => s + o.growth_percent, 0) / outlets.length).toFixed(1) : 0;
  const avgHealth = outlets.length ? Math.round(outlets.reduce((s, o) => s + o.health_score, 0) / outlets.length) : 0;
  const best = [...outlets].sort((a, b) => b.revenue - a.revenue)[0];
  const worst = [...outlets].sort((a, b) => a.health_score - b.health_score)[0];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI AGENT · OUTLET PERFORMANCE"
        title="Outlet Performance Agent"
        subtitle="Monitor outlet sales, analyze revenue trends, compare franchise locations, and identify underperforming stores."
        actions={
          <>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25">
              <Wand2 size={15} /> AI Analysis
            </button>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
              <GitCompareArrows size={15} /> Compare Outlets
            </button>
            <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
              <Download size={15} /> Export
            </button>
            <button onClick={() => rankingQ.refetch()} className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
              <RefreshCw size={15} />
            </button>
          </>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Total Revenue (30d)" value={compactCurrency(totalRevenue)} icon={DollarSign} color="#3b82f6" trend="live" />
        <KPICard label="Active Outlets" value={outlets.length} icon={Store} color="#8b5cf6" trend="live" />
        <KPICard label="Avg Growth" value={`${avgGrowth}%`} icon={TrendingUp} color="#10b981" trend="vs prior 30d" up={avgGrowth >= 0} />
        <KPICard label="Avg Health Score" value={`${avgHealth}/100`} icon={HeartPulse} color="#ec4899" trend="network" />
      </div>

      <GlassCard className="p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="font-semibold text-slate-900 dark:text-white">Outlet Sales Performance</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Revenue by period, aggregated from live sales data</p>
          </div>
          <div className="flex bg-slate-100 dark:bg-slate-800/60 rounded-lg p-1">
            {PERIODS.map((p) => (
              <button key={p} onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${period === p ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" : "text-slate-500 dark:text-slate-400"}`}>
                {p}
              </button>
            ))}
          </div>
        </div>
        {trendQ.isLoading ? <CardSkeleton /> : trendQ.isError ? (
          <ErrorState message="Couldn't load sales trend." onRetry={trendQ.refetch} />
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={trendQ.data} margin={{ left: -10, right: 10 }}>
              <defs>
                <linearGradient id="revFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="text-slate-100 dark:text-slate-800" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => compactCurrency(v)} width={60} />
              <Tooltip content={<ChartTooltip prefix="₹" />} />
              <Area type="monotone" dataKey="revenue" name="Revenue" stroke="#3b82f6" strokeWidth={2} fill="url(#revFill)" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </GlassCard>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <GlassCard className="p-6 flex flex-col items-center justify-center text-center">
          <h2 className="font-semibold text-slate-900 dark:text-white self-start mb-4">Network Health Score</h2>
          <HealthGauge score={avgHealth} label="Average across outlets" />
        </GlassCard>

        <GlassCard className="xl:col-span-2 p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-1">AI Insights</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Best / worst outlet, computed live from current data</p>
          {rankingQ.isLoading ? <CardSkeleton /> : outlets.length === 0 ? (
            <p className="text-sm text-slate-400">No outlet data yet.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/60 dark:bg-emerald-500/5 p-4">
                <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400 mb-1">Best outlet</p>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{best?.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{compactCurrency(best?.revenue)} revenue · {best?.growth_percent}% growth</p>
              </div>
              <div className="rounded-xl border border-rose-200 dark:border-rose-500/20 bg-rose-50/60 dark:bg-rose-500/5 p-4">
                <p className="text-xs font-medium text-rose-700 dark:text-rose-400 mb-1">Needs attention</p>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{worst?.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Health score {worst?.health_score}/100 · {worst?.status}</p>
              </div>
            </div>
          )}
        </GlassCard>
      </div>

      <GlassCard className="p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="font-semibold text-slate-900 dark:text-white">Revenue Forecast</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Linear regression over recent sales history</p>
          </div>
          <div className="flex bg-slate-100 dark:bg-slate-800/60 rounded-lg p-1">
            {["7D", "30D", "90D"].map((r) => (
              <button key={r} onClick={() => setForecastRange(r)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${forecastRange === r ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" : "text-slate-500 dark:text-slate-400"}`}>
                Next {r}
              </button>
            ))}
          </div>
        </div>
        {forecastQ.isLoading ? <CardSkeleton /> : forecastQ.isError ? (
          <ErrorState message="Not enough sales history to forecast yet." />
        ) : (
          <>
            <div className="flex items-center gap-4 mb-4 text-xs">
              <span className="text-slate-500 dark:text-slate-400">Confidence: <span className="font-semibold text-slate-800 dark:text-slate-100">{forecastQ.data.confidence}%</span></span>
              <span className="text-slate-500 dark:text-slate-400">Projected growth: <span className="font-semibold text-emerald-600 dark:text-emerald-400">{forecastQ.data.growth_percent}%</span></span>
            </div>
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={forecastQ.data.forecast.map((v, i) => ({ label: `+${i + 1}`, forecast: v, low: forecastQ.data.low[i], high: forecastQ.data.high[i] }))} margin={{ left: -10, right: 10 }}>
                <defs>
                  <linearGradient id="fcFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.3} /><stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="text-slate-100 dark:text-slate-800" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => compactCurrency(v)} width={60} />
                <Tooltip content={<ChartTooltip prefix="₹" />} />
                <Area type="monotone" dataKey="high" stroke="none" fill="url(#fcFill)" />
                <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#8b5cf6" strokeWidth={3} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </>
        )}
      </GlassCard>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Compare Franchise Locations</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">All outlets, live from the database</p>
        {rankingQ.isLoading ? <CardSkeleton /> : rankingQ.isError ? (
          <ErrorState message="Couldn't load outlets." onRetry={rankingQ.refetch} />
        ) : (
          <DataTable
            searchKeys={["name"]}
            columns={[
              { key: "name", label: "Outlet", sortable: true },
              { key: "revenue", label: "Revenue", sortable: true, render: (r) => compactCurrency(r.revenue) },
              { key: "orders", label: "Orders", sortable: true },
              {
                key: "growth_percent", label: "Growth %", sortable: true,
                render: (r) => (
                  <span className={r.growth_percent >= 0 ? "text-emerald-600 dark:text-emerald-400 font-medium" : "text-rose-600 dark:text-rose-400 font-medium"}>
                    {r.growth_percent >= 0 ? "+" : ""}{r.growth_percent}%
                  </span>
                ),
              },
              { key: "health_score", label: "Health Score", sortable: true },
              { key: "status", label: "Status", render: (r) => (
                <StatusBadge label={r.status} tone={r.status === "Healthy" ? "success" : r.status === "Average" ? "warning" : "danger"} />
              ) },
            ]}
            rows={outlets}
          />
        )}
      </GlassCard>
    </div>
  );
}
