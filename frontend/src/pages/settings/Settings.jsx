import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sun, Moon, Bell, ShieldCheck, RefreshCw } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { GlassCard } from "../../components/common/GlassCard";
import { StatusBadge } from "../../components/common/StatusBadge";
import { CardSkeleton, EmptyState, ErrorState } from "../../components/common/States";

import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import { alertService } from "../../services/aiService";

const severityTone = { critical: "danger", high: "warning", medium: "info", low: "success" };

export default function Settings() {
  const { user } = useAuth();
  const { dark, toggleTheme } = useTheme();
  const queryClient = useQueryClient();

  const alertsQ = useQuery({ queryKey: ["alerts", "all"], queryFn: () => alertService.list({}) });

  const scanMutation = useMutation({
    mutationFn: alertService.scan,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const markReadMutation = useMutation({
    mutationFn: alertService.markRead,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="ACCOUNT" title="Settings" subtitle="Manage your profile, theme, and the alerts center." />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <GlassCard className="p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Profile</h2>
          <div className="flex items-center gap-4 mb-4">
            <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-lg font-semibold">
              {(user?.full_name || "U").split(" ").map((p) => p[0]).slice(0, 2).join("")}
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{user?.full_name}</p>
              <p className="text-xs text-slate-400">{user?.email}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <ShieldCheck size={14} className="text-blue-500" />
            <span className="text-slate-500 dark:text-slate-400">Role:</span>
            <span className="font-medium text-slate-700 dark:text-slate-200 capitalize">{user?.role?.replace("_", " ")}</span>
          </div>
        </GlassCard>

        <GlassCard className="p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Appearance</h2>
          <button onClick={toggleTheme}
            className="w-full flex items-center justify-between px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800">
            <span className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-200">
              {dark ? <Moon size={16} /> : <Sun size={16} />} {dark ? "Dark mode" : "Light mode"}
            </span>
            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">Toggle</span>
          </button>
        </GlassCard>
      </div>

      <GlassCard className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Bell size={16} className="text-blue-500" />
            <h2 className="font-semibold text-slate-900 dark:text-white">Alerts Center</h2>
          </div>
          <button
            onClick={() => scanMutation.mutate()}
            disabled={scanMutation.isPending}
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 disabled:opacity-60"
          >
            <RefreshCw size={12} /> {scanMutation.isPending ? "Scanning..." : "Run Alert Scan"}
          </button>
        </div>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
          Low stock, expiring products, poor performance, staff shortages, overdue audits, and ending campaigns
        </p>

        {alertsQ.isLoading ? <CardSkeleton /> : alertsQ.isError ? (
          <ErrorState message="Couldn't load alerts." onRetry={alertsQ.refetch} />
        ) : (alertsQ.data || []).length === 0 ? (
          <EmptyState title="No alerts right now" subtitle="Run an alert scan to check for new issues." />
        ) : (
          <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
            {alertsQ.data.map((a) => (
              <div key={a.id} className={`flex items-center gap-3 rounded-xl border p-3 ${a.is_read ? "border-slate-100 dark:border-slate-800 opacity-60" : "border-slate-200 dark:border-slate-700"}`}>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <StatusBadge label={a.severity} tone={severityTone[a.severity] || "info"} />
                    <span className="text-[11px] text-slate-400 capitalize">{a.type.replace(/_/g, " ")}</span>
                  </div>
                  <p className="text-sm text-slate-700 dark:text-slate-200 mt-1">{a.message}</p>
                </div>
                {!a.is_read && (
                  <button onClick={() => markReadMutation.mutate(a.id)}
                    className="text-xs font-medium px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 shrink-0">
                    Mark read
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}
