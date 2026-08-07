import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, ShieldCheck, ShieldAlert, ClipboardList, AlertTriangle, Plus, CheckCircle2 } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { auditService } from "../../services/staffMarketingAuditService";

const severityTone = { critical: "danger", high: "warning", medium: "info", low: "success" };

function ScheduleAuditForm() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ outlet_id: "", scheduled_date: "", auditor_name: "" });

  const scheduleMutation = useMutation({
    mutationFn: () => auditService.schedule({ ...form, outlet_id: Number(form.outlet_id) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audits"] });
      setForm({ outlet_id: "", scheduled_date: "", auditor_name: "" });
    },
  });

  return (
    <GlassCard className="p-5">
      <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Schedule an Audit</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <input placeholder="Outlet ID" value={form.outlet_id} onChange={(e) => setForm({ ...form, outlet_id: e.target.value })}
          className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
        <input type="date" value={form.scheduled_date} onChange={(e) => setForm({ ...form, scheduled_date: e.target.value })}
          className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
        <input placeholder="Auditor name" value={form.auditor_name} onChange={(e) => setForm({ ...form, auditor_name: e.target.value })}
          className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
        <button onClick={() => scheduleMutation.mutate()} disabled={!form.outlet_id || !form.scheduled_date || scheduleMutation.isPending}
          className="flex items-center justify-center gap-1 text-xs font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 disabled:opacity-50">
          <Plus size={12} /> {scheduleMutation.isPending ? "Scheduling..." : "Schedule"}
        </button>
      </div>
      {scheduleMutation.isError && <p className="text-xs text-rose-500 mt-2">{scheduleMutation.error?.response?.data?.message || "Couldn't schedule audit."}</p>}
    </GlassCard>
  );
}

function FindingsPanel() {
  const queryClient = useQueryClient();
  const [auditId, setAuditId] = useState("");
  const [findingForm, setFindingForm] = useState({ category: "hygiene", finding: "", severity: "low", is_violation: false });

  const reportsQ = useQuery({
    queryKey: ["audits", "reports", auditId],
    queryFn: () => auditService.reportsFor(auditId),
    enabled: !!auditId,
  });

  const addFindingMutation = useMutation({
    mutationFn: () => auditService.addFinding({ ...findingForm, audit_id: Number(auditId) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audits", "reports", auditId] });
      setFindingForm({ category: "hygiene", finding: "", severity: "low", is_violation: false });
    },
  });

  const resolveMutation = useMutation({
    mutationFn: (reportId) => auditService.resolveFinding(reportId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["audits", "reports", auditId] }),
  });

  return (
    <GlassCard className="p-5">
      <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Audit Findings</h2>
      <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Enter an audit ID to view and add findings for it</p>

      <input placeholder="Audit ID" value={auditId} onChange={(e) => setAuditId(e.target.value)}
        className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2 mb-4 w-40" />

      {auditId && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
            <select value={findingForm.category} onChange={(e) => setFindingForm({ ...findingForm, category: e.target.value })}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5">
              <option value="hygiene">Hygiene</option>
              <option value="financial">Financial</option>
              <option value="safety">Safety</option>
              <option value="inventory">Inventory</option>
            </select>
            <select value={findingForm.severity} onChange={(e) => setFindingForm({ ...findingForm, severity: e.target.value })}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
            <input placeholder="Finding description" value={findingForm.finding} onChange={(e) => setFindingForm({ ...findingForm, finding: e.target.value })}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5 col-span-2" />
            <label className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
              <input type="checkbox" checked={findingForm.is_violation} onChange={(e) => setFindingForm({ ...findingForm, is_violation: e.target.checked })} />
              Violation
            </label>
            <button onClick={() => addFindingMutation.mutate()} disabled={!findingForm.finding || addFindingMutation.isPending}
              className="col-span-2 md:col-span-1 text-xs font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 disabled:opacity-50 py-1.5">
              {addFindingMutation.isPending ? "Adding..." : "Add Finding"}
            </button>
          </div>

          {reportsQ.isLoading ? <CardSkeleton /> : reportsQ.isError ? (
            <ErrorState message="Couldn't load findings." onRetry={reportsQ.refetch} />
          ) : reportsQ.data.length === 0 ? <EmptyState title="No findings recorded for this audit yet" /> : (
            <div className="space-y-2">
              {reportsQ.data.map((f) => (
                <div key={f.id} className={`flex items-center gap-3 rounded-xl border p-3 ${f.resolved ? "border-slate-100 dark:border-slate-800 opacity-60" : "border-slate-200 dark:border-slate-700"}`}>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <StatusBadge label={f.severity} tone={severityTone[f.severity]} />
                      <span className="text-[11px] text-slate-400 capitalize">{f.category}</span>
                      {f.is_violation && <StatusBadge label="Violation" tone="danger" />}
                      {f.resolved && <StatusBadge label="Resolved" tone="success" />}
                    </div>
                    <p className="text-sm text-slate-700 dark:text-slate-200 mt-1">{f.finding}</p>
                  </div>
                  {!f.resolved && (
                    <button onClick={() => resolveMutation.mutate(f.id)}
                      className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-emerald-50 hover:text-emerald-600 dark:hover:bg-emerald-500/10 shrink-0">
                      <CheckCircle2 size={12} /> Resolve
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </GlassCard>
  );
}

export default function AuditAgent() {
  const auditsQ = useQuery({ queryKey: ["audits", "list"], queryFn: () => auditService.list({}) });
  const pendingQ = useQuery({ queryKey: ["audits", "pending"], queryFn: auditService.pending });
  const riskQ = useQuery({ queryKey: ["audits", "risk-overview"], queryFn: auditService.riskOverview });

  const audits = auditsQ.data || [];
  const avgCompliance = audits.filter((a) => a.compliance_score != null).length
    ? Math.round(audits.filter((a) => a.compliance_score != null).reduce((s, a) => s + Number(a.compliance_score), 0) /
        audits.filter((a) => a.compliance_score != null).length)
    : 0;
  const fraudFlags = (riskQ.data || []).filter((r) => r.fraud_risk_flag).length;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI AGENT · AUDIT"
        title="Audit Agent"
        subtitle="Track compliance scores, violations, and AI-driven risk and fraud detection across every outlet."
        actions={
          <button onClick={() => { auditsQ.refetch(); pendingQ.refetch(); riskQ.refetch(); }}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
            <RefreshCw size={15} />
          </button>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Total Audits" value={audits.length} icon={ClipboardList} color="#3b82f6" trend="live" />
        <KPICard label="Pending Audits" value={pendingQ.data?.length ?? "—"} icon={AlertTriangle} color="#f59e0b" trend="needs scheduling" />
        <KPICard label="Avg Compliance Score" value={`${avgCompliance}/100`} icon={ShieldCheck} color="#10b981" trend="completed audits" />
        <KPICard label="Fraud Risk Flags" value={fraudFlags} icon={ShieldAlert} color="#f43f5e" trend="AI-detected" up={false} />
      </div>

      <ScheduleAuditForm />

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">AI Risk Overview</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Every completed audit, scored by risk (highest first)</p>
        {riskQ.isLoading ? <CardSkeleton /> : riskQ.isError ? (
          <ErrorState message="Couldn't load risk overview." onRetry={riskQ.refetch} />
        ) : riskQ.data.length === 0 ? <EmptyState title="No completed audits yet" /> : (
          <DataTable
            searchKeys={[]}
            columns={[
              { key: "outlet_id", label: "Outlet ID", sortable: true },
              { key: "compliance_score", label: "Compliance Score", sortable: true },
              { key: "violation_count", label: "Violations", sortable: true },
              { key: "risk_score", label: "Risk Score", sortable: true },
              { key: "fraud_risk_flag", label: "Fraud Risk", render: (r) => r.fraud_risk_flag ? <StatusBadge label="Flagged" tone="danger" /> : <StatusBadge label="Clear" tone="success" /> },
              { key: "recommendation", label: "AI Recommendation" },
            ]}
            rows={riskQ.data}
          />
        )}
      </GlassCard>

      <FindingsPanel />

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">All Audits</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Scheduled, pending, and completed</p>
        {auditsQ.isLoading ? <CardSkeleton /> : auditsQ.isError ? (
          <ErrorState message="Couldn't load audits." onRetry={auditsQ.refetch} />
        ) : (
          <DataTable
            searchKeys={[]}
            columns={[
              { key: "id", label: "ID", sortable: true },
              { key: "outlet_id", label: "Outlet ID", sortable: true },
              { key: "scheduled_date", label: "Scheduled", sortable: true },
              { key: "status", label: "Status", render: (r) => (
                <StatusBadge label={r.status} tone={r.status === "completed" ? "success" : r.status === "overdue" ? "danger" : "warning"} />
              ) },
              { key: "compliance_score", label: "Compliance Score", sortable: true, render: (r) => r.compliance_score ?? "—" },
              { key: "risk_score", label: "Risk Score", sortable: true, render: (r) => r.risk_score ?? "—" },
              { key: "auditor_name", label: "Auditor", render: (r) => r.auditor_name || "—" },
            ]}
            rows={audits}
          />
        )}
      </GlassCard>
    </div>
  );
}
