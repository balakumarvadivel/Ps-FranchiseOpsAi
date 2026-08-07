import { useQuery } from "@tanstack/react-query";
import {
  RefreshCw, Wand2, Download, DollarSign, ShoppingCart, TrendingUp, Building2,
  Bell, HeartPulse, Users, Megaphone, ShieldCheck, PieChart as PieIcon,
} from "lucide-react";
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { AISummaryBanner } from "../../components/ai/AIInsightCard";
import { ChartTooltip } from "../../components/charts/ChartTooltip";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { outletService, salesService } from "../../services/outletService";
import { aiService, alertService } from "../../services/aiService";
import { staffService, marketingService, auditService } from "../../services/staffMarketingAuditService";
import { compactCurrency } from "../../utils/formatters";

const REGION_COLORS = { South: "#3b82f6", North: "#8b5cf6", East: "#06b6d4", West: "#f59e0b" };

export default function Dashboard() {
  const summaryQ = useQuery({ queryKey: ["ai", "executive-summary"], queryFn: aiService.executiveSummary });
  const rankingQ = useQuery({ queryKey: ["outlets", "ranking"], queryFn: () => outletService.ranking(30) });
  const outletsQ = useQuery({ queryKey: ["outlets", "list"], queryFn: () => outletService.list() });
  const trendQ = useQuery({ queryKey: ["sales", "trend", "Monthly"], queryFn: () => salesService.trend({ period: "Monthly" }) });
  const alertsQ = useQuery({ queryKey: ["alerts", "all"], queryFn: () => alertService.list({}) });
  const profitTrendQ = useQuery({ queryKey: ["ai", "profit-trend"], queryFn: () => aiService.profitTrend({}) });
  const categoryQ = useQuery({ queryKey: ["sales", "category-performance"], queryFn: () => salesService.categoryPerformance({}) });
  const staffPerfQ = useQuery({ queryKey: ["staff", "performance", "all"], queryFn: () => staffService.performance() });
  const campaignsQ = useQuery({ queryKey: ["marketing", "campaigns", "all"], queryFn: () => marketingService.listCampaigns() });
  const complianceQ = useQuery({ queryKey: ["audits", "compliance-trend"], queryFn: auditService.complianceTrend });

  const outlets = rankingQ.data || [];
  const totalRevenue = outlets.reduce((s, o) => s + o.revenue, 0);
  const totalOrders = outlets.reduce((s, o) => s + o.orders, 0);
  const avgGrowth = outlets.length ? (outlets.reduce((s, o) => s + o.growth_percent, 0) / outlets.length).toFixed(1) : 0;
  const avgHealth = outlets.length ? Math.round(outlets.reduce((s, o) => s + o.health_score, 0) / outlets.length) : 0;

  // Regional performance — merge ranking data (revenue/health) with outlet list (region)
  const regionMap = {};
  (outletsQ.data || []).forEach((o) => {
    const kpi = outlets.find((r) => r.outlet_id === o.id);
    if (!kpi) return;
    if (!regionMap[o.region]) regionMap[o.region] = { region: o.region, revenue: 0, health: 0, count: 0 };
    regionMap[o.region].revenue += kpi.revenue;
    regionMap[o.region].health += kpi.health_score;
    regionMap[o.region].count += 1;
  });
  const regionalPerformance = Object.values(regionMap).map((r) => ({ ...r, health: Math.round(r.health / r.count) }));

  const avgStaffScore = staffPerfQ.data?.length
    ? Math.round(staffPerfQ.data.reduce((s, e) => s + e.performance_score, 0) / staffPerfQ.data.length) : null;
  const avgCampaignRoi = campaignsQ.data?.length
    ? (campaignsQ.data.reduce((s, c) => s + c.roi_percent, 0) / campaignsQ.data.length).toFixed(1) : null;
  const avgCompliance = complianceQ.data?.length
    ? Math.round(complianceQ.data.reduce((s, c) => s + c.compliance_score, 0) / complianceQ.data.length) : null;

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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <GlassCard className="p-5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center shrink-0">
            <Users size={18} className="text-blue-500" />
          </div>
          <div>
            <p className="text-[11px] text-slate-400">Employee Performance (avg)</p>
            <p className="text-lg font-bold text-slate-900 dark:text-white">{avgStaffScore != null ? `${avgStaffScore}/100` : "—"}</p>
          </div>
        </GlassCard>
        <GlassCard className="p-5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-50 dark:bg-purple-500/10 flex items-center justify-center shrink-0">
            <Megaphone size={18} className="text-purple-500" />
          </div>
          <div>
            <p className="text-[11px] text-slate-400">Marketing ROI (avg)</p>
            <p className="text-lg font-bold text-slate-900 dark:text-white">{avgCampaignRoi != null ? `${avgCampaignRoi}%` : "—"}</p>
          </div>
        </GlassCard>
        <GlassCard className="p-5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center shrink-0">
            <ShieldCheck size={18} className="text-emerald-500" />
          </div>
          <div>
            <p className="text-[11px] text-slate-400">Audit Compliance (avg)</p>
            <p className="text-lg font-bold text-slate-900 dark:text-white">{avgCompliance != null ? `${avgCompliance}/100` : "—"}</p>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <GlassCard className="p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Profit Trend</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Revenue, cost, and profit by month</p>
          {profitTrendQ.isLoading ? <CardSkeleton /> : profitTrendQ.isError ? (
            <ErrorState message="Couldn't load profit trend." onRetry={profitTrendQ.refetch} />
          ) : profitTrendQ.data.length === 0 ? <EmptyState title="Not enough sales history yet" /> : (
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={profitTrendQ.data} margin={{ left: -10, right: 10 }}>
                <defs>
                  <linearGradient id="profitFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.35} /><stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="text-slate-100 dark:text-slate-800" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => compactCurrency(v)} width={60} />
                <Tooltip content={<ChartTooltip prefix="₹" />} />
                <Area type="monotone" dataKey="profit" name="Profit" stroke="#10b981" strokeWidth={2} fill="url(#profitFill)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </GlassCard>

        <GlassCard className="p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Category Performance</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Revenue by product category, last 30 days</p>
          {categoryQ.isLoading ? <CardSkeleton /> : categoryQ.isError ? (
            <ErrorState message="Couldn't load category performance." onRetry={categoryQ.refetch} />
          ) : categoryQ.data.length === 0 ? <EmptyState title="No category data yet" /> : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={categoryQ.data} margin={{ left: -10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" className="text-slate-100 dark:text-slate-800" vertical={false} />
                <XAxis dataKey="category" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} tickFormatter={(v) => compactCurrency(v)} width={60} />
                <Tooltip content={<ChartTooltip prefix="₹" />} />
                <Bar dataKey="revenue" name="Revenue" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </GlassCard>
      </div>

      <GlassCard className="p-5">
        <div className="flex items-center gap-2 mb-1">
          <PieIcon size={16} className="text-blue-500" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Regional Performance</h2>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Revenue and average health score by region</p>
        {(!outletsQ.data || !rankingQ.data) ? <CardSkeleton /> : regionalPerformance.length === 0 ? <EmptyState title="No regional data yet" /> : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {regionalPerformance.map((r) => (
              <div key={r.region} className="rounded-xl border border-slate-200 dark:border-slate-800 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: REGION_COLORS[r.region] || "#94a3b8" }} />
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{r.region}</p>
                  <span className="text-[11px] text-slate-400 ml-auto">{r.count} outlets</span>
                </div>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{compactCurrency(r.revenue)}</p>
                <p className="text-[11px] text-slate-400">Health {r.health}/100</p>
              </div>
            ))}
          </div>
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
