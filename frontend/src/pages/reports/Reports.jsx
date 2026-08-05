import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileDown, FileSpreadsheet, FileText, Download } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { GlassCard } from "../../components/common/GlassCard";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { reportService } from "../../services/aiService";

const REPORT_TYPES = ["sales", "inventory", "staff", "marketing", "audit", "overall"];
const FORMATS = [
  { value: "pdf", label: "PDF", icon: FileText },
  { value: "excel", label: "Excel", icon: FileSpreadsheet },
  { value: "csv", label: "CSV", icon: FileDown },
];

export default function Reports() {
  const [reportType, setReportType] = useState("overall");
  const [format, setFormat] = useState("pdf");
  const queryClient = useQueryClient();

  const reportsQ = useQuery({ queryKey: ["reports", "list"], queryFn: reportService.list });

  const generateMutation = useMutation({
    mutationFn: () => reportService.generate({ report_type: reportType, format }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["reports", "list"] }),
  });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="REPORTING"
        title="Reports"
        subtitle="Generate and download PDF, Excel, or CSV reports for any domain."
      />

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Generate a new report</h2>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 block">Report type</label>
            <select value={reportType} onChange={(e) => setReportType(e.target.value)}
              className="text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 capitalize">
              {REPORT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 block">Format</label>
            <div className="flex bg-slate-100 dark:bg-slate-800/60 rounded-lg p-1">
              {FORMATS.map((f) => (
                <button key={f.value} onClick={() => setFormat(f.value)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    format === f.value ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" : "text-slate-500 dark:text-slate-400"
                  }`}>
                  <f.icon size={12} /> {f.label}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25 disabled:opacity-60"
          >
            {generateMutation.isPending ? "Generating..." : "Generate Report"}
          </button>
        </div>
        {generateMutation.isError && (
          <p className="text-xs text-rose-500 mt-3">Couldn't generate the report — check the backend is reachable.</p>
        )}
        {generateMutation.isSuccess && (
          <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-3">Report generated — find it in the list below.</p>
        )}
      </GlassCard>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Your reports</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Previously generated reports, newest first</p>

        {reportsQ.isLoading ? <CardSkeleton /> : reportsQ.isError ? (
          <ErrorState message="Couldn't load reports." onRetry={reportsQ.refetch} />
        ) : (reportsQ.data || []).length === 0 ? (
          <EmptyState title="No reports generated yet" />
        ) : (
          <div className="space-y-2">
            {reportsQ.data.map((r) => (
              <div key={r.id} className="flex items-center gap-3 rounded-xl border border-slate-100 dark:border-slate-800 p-3">
                <div className="w-9 h-9 rounded-lg bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center shrink-0">
                  <FileText size={15} className="text-blue-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 dark:text-slate-100 capitalize">{r.report_type} report</p>
                  <p className="text-[11px] text-slate-400">{r.format.toUpperCase()} · {new Date(r.created_at).toLocaleString("en-IN")}</p>
                </div>
                <button
                  onClick={() => reportService.download(r.id, `${r.report_type}_report.${r.format === "excel" ? "xlsx" : r.format}`)}
                  className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800"
                >
                  <Download size={12} /> Download
                </button>
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}
