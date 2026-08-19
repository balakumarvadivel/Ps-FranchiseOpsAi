import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Megaphone, TrendingUp, TrendingDown, Users, Wallet } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { marketingService } from "../../services/staffMarketingAuditService";
import { compactCurrency } from "../../utils/formatters";

const SEGMENT_COLORS = { VIP: "#8b5cf6", Regular: "#3b82f6", New: "#10b981", "At-risk": "#f43f5e", Occasional: "#94a3b8" };

export default function MarketingAgent() {
  const campaignsQ = useQuery({ queryKey: ["marketing", "campaigns"], queryFn: () => marketingService.listCampaigns() });
  const bestWorstQ = useQuery({ queryKey: ["marketing", "best-worst"], queryFn: () => marketingService.bestWorst() });
  const segmentsQ = useQuery({ queryKey: ["marketing", "segments"], queryFn: () => marketingService.segments() });
  const budgetQ = useQuery({ queryKey: ["marketing", "budget-optimization"], queryFn: marketingService.budgetOptimization, retry: false });

  const campaigns = campaignsQ.data || [];
  const totalBudget = campaigns.reduce((s, c) => s + c.budget, 0);
  const totalRevenue = campaigns.reduce((s, c) => s + c.revenue_generated, 0);
  const avgRoi = campaigns.length ? (campaigns.reduce((s, c) => s + c.roi_percent, 0) / campaigns.length).toFixed(1) : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI AGENT · MARKETING"
        title="Marketing Agent"
        subtitle="Track campaign ROI, segment customers, and get AI-driven budget optimization recommendations."
        actions={
          <button onClick={() => { campaignsQ.refetch(); bestWorstQ.refetch(); segmentsQ.refetch(); }}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
            <RefreshCw size={15} />
          </button>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Total Campaign Budget" value={compactCurrency(totalBudget)} icon={Wallet} color="#3b82f6" trend="live" />
        <KPICard label="Revenue Generated" value={compactCurrency(totalRevenue)} icon={TrendingUp} color="#10b981" trend="live" />
        <KPICard label="Average ROI" value={`${avgRoi}%`} icon={Megaphone} color="#8b5cf6" trend="across campaigns" />
        <KPICard label="Active Campaigns" value={campaigns.filter((c) => c.status === "active").length} icon={Users} color="#f59e0b" trend="live" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <GlassCard className="p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Best / Poor Campaign (AI)</h2>
          {bestWorstQ.isLoading ? <CardSkeleton /> : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {bestWorstQ.data?.best && (
                <div className="rounded-xl border border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/60 dark:bg-emerald-500/5 p-4">
                  <p className="text-xs font-medium text-emerald-700 dark:text-emerald-400 mb-1 flex items-center gap-1"><TrendingUp size={12} /> Best campaign</p>
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{bestWorstQ.data.best.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{bestWorstQ.data.best.roi_percent}% ROI · {bestWorstQ.data.best.channel}</p>
                </div>
              )}
              {bestWorstQ.data?.worst && (
                <div className="rounded-xl border border-rose-200 dark:border-rose-500/20 bg-rose-50/60 dark:bg-rose-500/5 p-4">
                  <p className="text-xs font-medium text-rose-700 dark:text-rose-400 mb-1 flex items-center gap-1"><TrendingDown size={12} /> Poor campaign</p>
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{bestWorstQ.data.worst.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{bestWorstQ.data.worst.roi_percent}% ROI · {bestWorstQ.data.worst.channel}</p>
                </div>
              )}
            </div>
          )}

          {budgetQ.data && (
            <div className="mt-4 rounded-xl bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-500/10 dark:to-purple-500/10 border border-blue-100 dark:border-blue-500/20 p-4">
              <p className="text-xs font-medium text-blue-700 dark:text-blue-300 mb-1">AI Budget Optimization</p>
              <p className="text-xs text-slate-600 dark:text-slate-300">
                Shift ~{budgetQ.data.suggested_shift_percent}% of budget from <b>{budgetQ.data.move_budget_from}</b> ({budgetQ.data.from_roi_percent}% ROI)
                to <b>{budgetQ.data.move_budget_to}</b> ({budgetQ.data.to_roi_percent}% ROI). {budgetQ.data.reason}
              </p>
            </div>
          )}
        </GlassCard>

        <GlassCard className="p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Customer Segmentation (AI)</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Rule-based RFM segmentation from live customer data</p>
          {segmentsQ.isLoading ? <CardSkeleton /> : segmentsQ.data?.length === 0 ? <EmptyState title="No customer data yet" /> : (
            <div className="flex items-center gap-4">
              <ResponsiveContainer width="50%" height={160}>
                <PieChart>
                  <Tooltip />
                  <Pie data={segmentsQ.data} dataKey="customer_count" nameKey="segment" innerRadius={40} outerRadius={70} paddingAngle={3}>
                    {(segmentsQ.data || []).map((s, i) => <Cell key={i} fill={SEGMENT_COLORS[s.segment] || "#94a3b8"} />)}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 text-xs flex-1">
                {(segmentsQ.data || []).map((s) => (
                  <div key={s.segment} className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full" style={{ background: SEGMENT_COLORS[s.segment] || "#94a3b8" }} />{s.segment}</span>
                    <span className="font-medium text-slate-700 dark:text-slate-200">{s.customer_count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </GlassCard>
      </div>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Campaign Dashboard</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">All campaigns, ranked by ROI</p>
        {campaignsQ.isLoading ? <CardSkeleton /> : campaignsQ.isError ? (
          <ErrorState message="Couldn't load campaigns." onRetry={campaignsQ.refetch} />
        ) : campaigns.length === 0 ? <EmptyState title="No campaigns yet" /> : (
          <DataTable
            searchKeys={["name", "channel"]}
            columns={[
              { key: "name", label: "Campaign", sortable: true },
              { key: "channel", label: "Channel", sortable: true },
              { key: "budget", label: "Budget", sortable: true, render: (r) => compactCurrency(r.budget) },
              { key: "revenue_generated", label: "Revenue", sortable: true, render: (r) => compactCurrency(r.revenue_generated) },
              { key: "leads", label: "Leads", sortable: true },
              { key: "conversion_rate_percent", label: "Conv. Rate", sortable: true, render: (r) => `${r.conversion_rate_percent}%` },
              { key: "roi_percent", label: "ROI %", sortable: true, render: (r) => `${r.roi_percent}%` },
              { key: "status", label: "Status" },
            ]}
            rows={campaigns}
          />
        )}
      </GlassCard>
    </div>
  );
}
