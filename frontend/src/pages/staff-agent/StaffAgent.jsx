import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Users, UserCheck, AlertTriangle, Award, Clock3 } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { staffService } from "../../services/staffMarketingAuditService";
import { outletService } from "../../services/outletService";

const riskTone = { low: "success", medium: "warning", high: "danger" };

export default function StaffAgent() {
  const [outletId, setOutletId] = useState("");

  const outletsQ = useQuery({ queryKey: ["outlets", "list"], queryFn: () => outletService.list() });
  const perfQ = useQuery({
    queryKey: ["staff", "performance", outletId],
    queryFn: () => staffService.performance(outletId || undefined),
  });
  const shiftQ = useQuery({
    queryKey: ["staff", "shift-optimization", outletId],
    queryFn: () => staffService.shiftOptimization(Number(outletId)),
    enabled: !!outletId,
  });

  const rows = perfQ.data || [];
  const avgAttendance = rows.length ? Math.round(rows.reduce((s, r) => s + r.attendance_rate, 0) / rows.length) : 0;
  const avgScore = rows.length ? Math.round(rows.reduce((s, r) => s + r.performance_score, 0) / rows.length) : 0;
  const highRisk = rows.filter((r) => r.attrition_risk === "high").length;
  const best = [...rows].sort((a, b) => b.performance_score - a.performance_score)[0];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI AGENT · STAFF"
        title="Staff Agent"
        subtitle="Track attendance, productivity, and get AI-driven performance scores, attrition risk, and shift optimization."
        actions={
          <>
            <select value={outletId} onChange={(e) => setOutletId(e.target.value)}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2">
              <option value="">All outlets</option>
              {(outletsQ.data || []).map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
            </select>
            <button onClick={() => perfQ.refetch()} className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
              <RefreshCw size={15} />
            </button>
          </>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Active Employees" value={rows.length} icon={Users} color="#3b82f6" trend="live" />
        <KPICard label="Avg Attendance" value={`${avgAttendance}%`} icon={UserCheck} color="#10b981" trend="30d" />
        <KPICard label="Avg Performance Score" value={`${avgScore}/100`} icon={Award} color="#8b5cf6" trend="live" />
        <KPICard label="High Attrition Risk" value={highRisk} icon={AlertTriangle} color="#f43f5e" trend="employees" up={false} />
      </div>

      {best && (
        <GlassCard className="p-5 flex items-center gap-4">
          <div className="w-11 h-11 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold shrink-0">
            {best.full_name.split(" ").map((p) => p[0]).slice(0, 2).join("")}
          </div>
          <div>
            <p className="text-[11px] text-slate-400">AI feature: Best performing employee</p>
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{best.full_name} — score {best.performance_score}/100</p>
          </div>
          <Award size={20} className="text-amber-400 ml-auto shrink-0" />
        </GlassCard>
      )}

      {outletId && (
        <GlassCard className="p-5">
          <div className="flex items-center gap-2 mb-1">
            <Clock3 size={16} className="text-blue-500" />
            <h2 className="font-semibold text-slate-900 dark:text-white">AI Shift Optimization</h2>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Peak sales hours vs. scheduled staff coverage</p>
          {shiftQ.isLoading ? <CardSkeleton /> : shiftQ.data?.suggestions?.length ? (
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-300">
              {shiftQ.data.suggestions.map((s, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" /> {s}
                </li>
              ))}
            </ul>
          ) : <EmptyState title="No staffing gaps detected for this outlet" />}
        </GlassCard>
      )}

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Employee Performance</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">AI-computed performance score and attrition risk</p>
        {perfQ.isLoading ? <CardSkeleton /> : perfQ.isError ? (
          <ErrorState message="Couldn't load staff performance." onRetry={perfQ.refetch} />
        ) : rows.length === 0 ? <EmptyState title="No active employees found" /> : (
          <DataTable
            searchKeys={["full_name"]}
            columns={[
              { key: "full_name", label: "Employee", sortable: true },
              { key: "attendance_rate", label: "Attendance %", sortable: true },
              { key: "shift_completion_rate", label: "Shift Completion %", sortable: true },
              { key: "performance_score", label: "Performance Score", sortable: true },
              { key: "attrition_risk", label: "Attrition Risk", render: (r) => <StatusBadge label={r.attrition_risk} tone={riskTone[r.attrition_risk]} /> },
            ]}
            rows={rows}
          />
        )}
      </GlassCard>
    </div>
  );
}
