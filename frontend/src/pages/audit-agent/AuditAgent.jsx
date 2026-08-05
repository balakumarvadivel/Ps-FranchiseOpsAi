import { useQuery } from "@tanstack/react-query";
import { RefreshCw, ShieldCheck, ShieldAlert, ClipboardList, AlertTriangle } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { auditService } from "../../services/staffMarketingAuditService";

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

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">All Audits</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Scheduled, pending, and completed</p>
        {auditsQ.isLoading ? <CardSkeleton /> : auditsQ.isError ? (
          <ErrorState message="Couldn't load audits." onRetry={auditsQ.refetch} />
        ) : (
          <DataTable
            searchKeys={[]}
            columns={[
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
