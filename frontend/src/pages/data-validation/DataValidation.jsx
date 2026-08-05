import { useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { UploadCloud, FileCheck2, AlertTriangle, CheckCircle2, Database } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { GlassCard } from "../../components/common/GlassCard";
import { HealthGauge } from "../../components/common/HealthGauge";
import { ErrorState } from "../../components/common/States";

import { dataValidationService } from "../../services/dataValidationService";

const DATASET_TYPES = [
  { value: "sales", label: "Sales", required: ["outlet_id", "product_id", "quantity", "unit_price", "sale_date"] },
  { value: "inventory", label: "Inventory", required: ["outlet_id", "product_id", "quantity"] },
  { value: "employees", label: "Employees", required: ["outlet_id", "full_name", "date_joined"] },
];

export default function DataValidation() {
  const [datasetType, setDatasetType] = useState("sales");
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const uploadMutation = useMutation({
    mutationFn: () => dataValidationService.upload(file, datasetType),
  });

  const commitMutation = useMutation({
    mutationFn: () => dataValidationService.commit(datasetType, uploadMutation.data.cleaned_data),
  });

  const report = uploadMutation.data;
  const activeSchema = DATASET_TYPES.find((d) => d.value === datasetType);

  const handleFileChange = (e) => {
    setFile(e.target.files?.[0] || null);
    uploadMutation.reset();
    commitMutation.reset();
  };

  const issueRows = report
    ? [
        ...Object.entries(report.issues.missing_values).map(([col, n]) => ({ type: "Missing values", column: col, count: n })),
        ...(report.issues.duplicate_entries ? [{ type: "Duplicate entries", column: "—", count: report.issues.duplicate_entries }] : []),
        ...Object.entries(report.issues.invalid_dates).map(([col, n]) => ({ type: "Invalid dates", column: col, count: n })),
        ...Object.entries(report.issues.invalid_prices).map(([col, n]) => ({ type: "Invalid prices", column: col, count: n })),
        ...Object.entries(report.issues.invalid_inventory).map(([col, n]) => ({ type: "Invalid inventory", column: col, count: n })),
      ]
    : [];

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="DATA PIPELINE"
        title="Data Validation & Processing"
        subtitle="Upload CSV/Excel data, run automatic validation and cleaning, and commit the cleaned records to the database."
      />

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4">1. Choose dataset type and file</h2>
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 block">Dataset type</label>
            <select value={datasetType} onChange={(e) => { setDatasetType(e.target.value); uploadMutation.reset(); commitMutation.reset(); }}
              className="text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2">
              {DATASET_TYPES.map((d) => <option key={d.value} value={d.value}>{d.label}</option>)}
            </select>
          </div>

          <div className="flex-1 min-w-[240px]">
            <label className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1 block">File (.csv, .xlsx)</label>
            <button onClick={() => fileInputRef.current?.click()}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg border border-dashed border-slate-300 dark:border-slate-600 text-sm text-slate-500 dark:text-slate-400 hover:border-blue-400 hover:text-blue-600">
              <UploadCloud size={15} /> {file ? file.name : "Choose a file..."}
            </button>
            <input ref={fileInputRef} type="file" accept=".csv,.xlsx,.xls" onChange={handleFileChange} className="hidden" />
          </div>

          <button
            onClick={() => uploadMutation.mutate()}
            disabled={!file || uploadMutation.isPending}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25 disabled:opacity-50"
          >
            <FileCheck2 size={15} /> {uploadMutation.isPending ? "Validating..." : "Validate"}
          </button>
        </div>

        <p className="text-[11px] text-slate-400 mt-3">
          Required columns for {activeSchema.label}: <span className="font-mono">{activeSchema.required.join(", ")}</span>
        </p>

        {uploadMutation.isError && (
          <div className="mt-3">
            <ErrorState message={uploadMutation.error?.response?.data?.message || "Validation failed."} />
          </div>
        )}
      </GlassCard>

      {report && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            <GlassCard className="p-5 flex flex-col items-center justify-center">
              <HealthGauge score={report.data_quality_score} label="Data Quality Score" />
            </GlassCard>
            <GlassCard className="p-5 flex flex-col justify-center">
              <p className="text-[11px] text-slate-400">Total rows</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-white">{report.total_rows}</p>
              <div className="mt-3 flex items-center gap-2 text-xs">
                <CheckCircle2 size={13} className="text-emerald-500" />
                <span className="text-slate-500 dark:text-slate-400">{report.clean_rows} clean rows ready to import</span>
              </div>
            </GlassCard>
            <GlassCard className="p-5 flex flex-col justify-center">
              <p className="text-[11px] text-slate-400">Flagged rows</p>
              <p className="text-2xl font-bold text-rose-500">{report.flagged_rows}</p>
              <div className="mt-3 flex items-center gap-2 text-xs">
                <AlertTriangle size={13} className="text-amber-500" />
                <span className="text-slate-500 dark:text-slate-400">Excluded from the clean dataset below</span>
              </div>
            </GlassCard>
          </div>

          <GlassCard className="p-5">
            <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Validation Report</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Issues detected, by type and column</p>
            {issueRows.length === 0 ? (
              <p className="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-2"><CheckCircle2 size={16} /> No issues detected.</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[11px] uppercase tracking-wide text-slate-400 border-b border-slate-200 dark:border-slate-800">
                    <th className="py-2 pr-4 font-medium">Issue Type</th>
                    <th className="py-2 pr-4 font-medium">Column</th>
                    <th className="py-2 pr-4 font-medium">Rows Affected</th>
                  </tr>
                </thead>
                <tbody>
                  {issueRows.map((row, i) => (
                    <tr key={i} className="border-b border-slate-100 dark:border-slate-800/60">
                      <td className="py-2 pr-4 text-rose-600 dark:text-rose-400 font-medium">{row.type}</td>
                      <td className="py-2 pr-4 font-mono text-xs">{row.column}</td>
                      <td className="py-2 pr-4">{row.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </GlassCard>

          <GlassCard className="p-5">
            <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Cleaning Suggestions</h2>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-300 mt-3">
              {report.cleaning_suggestions.map((s, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" /> {s}
                </li>
              ))}
            </ul>
          </GlassCard>

          <GlassCard className="p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-semibold text-slate-900 dark:text-white">2. Commit cleaned data</h2>
                <p className="text-xs text-slate-500 dark:text-slate-400">Inserts the {report.clean_rows} clean row(s) into the database</p>
              </div>
              <button
                onClick={() => commitMutation.mutate()}
                disabled={commitMutation.isPending || commitMutation.isSuccess}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25 disabled:opacity-50"
              >
                <Database size={15} /> {commitMutation.isPending ? "Importing..." : commitMutation.isSuccess ? "Imported" : "Commit to Database"}
              </button>
            </div>

            {commitMutation.isSuccess && (
              <div className="rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 text-xs px-3 py-2">
                Inserted {commitMutation.data.inserted} row(s), skipped {commitMutation.data.skipped}.
                {commitMutation.data.errors.length > 0 && (
                  <ul className="mt-1 list-disc list-inside">
                    {commitMutation.data.errors.map((e, i) => <li key={i}>{e}</li>)}
                  </ul>
                )}
              </div>
            )}

            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2 mt-4">Preview (first {Math.min(10, report.cleaned_preview.length)} rows)</p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="text-left text-slate-400 border-b border-slate-200 dark:border-slate-800">
                    {report.cleaned_preview[0] && Object.keys(report.cleaned_preview[0]).map((col) => (
                      <th key={col} className="py-2 pr-4 font-medium">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {report.cleaned_preview.slice(0, 10).map((row, i) => (
                    <tr key={i} className="border-b border-slate-100 dark:border-slate-800/60">
                      {Object.values(row).map((val, j) => <td key={j} className="py-2 pr-4">{String(val)}</td>)}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </>
      )}
    </div>
  );
}
