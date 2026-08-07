import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  RefreshCw, Users, UserCheck, AlertTriangle, Award, Clock3,
  Wallet, CalendarDays, ClipboardList, Plus, Check, X as XIcon,
} from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { staffService } from "../../services/staffMarketingAuditService";
import { outletService } from "../../services/outletService";
import { compactCurrency } from "../../utils/formatters";

const riskTone = { low: "success", medium: "warning", high: "danger" };
const leaveStatusTone = { pending: "warning", approved: "success", rejected: "danger" };

function PerformanceTab({ outletId }) {
  const perfQ = useQuery({
    queryKey: ["staff", "performance", outletId],
    queryFn: () => staffService.performance(outletId || undefined),
  });
  const shiftOptQ = useQuery({
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
    <div className="space-y-5">
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
          {shiftOptQ.isLoading ? <CardSkeleton /> : shiftOptQ.data?.suggestions?.length ? (
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-300">
              {shiftOptQ.data.suggestions.map((s, i) => (
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

function PayrollTab({ outletId }) {
  const queryClient = useQueryClient();
  const payrollQ = useQuery({
    queryKey: ["staff", "payroll", outletId],
    queryFn: () => staffService.listPayroll(outletId ? { outlet_id: outletId } : {}),
  });
  const [form, setForm] = useState({ employee_id: "", month: "", base_salary: "", overtime_pay: "0", deductions: "0" });

  const recordMutation = useMutation({
    mutationFn: () => staffService.recordPayroll({
      employee_id: Number(form.employee_id), month: form.month,
      base_salary: Number(form.base_salary), overtime_pay: Number(form.overtime_pay), deductions: Number(form.deductions),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff", "payroll"] });
      setForm({ employee_id: "", month: "", base_salary: "", overtime_pay: "0", deductions: "0" });
    },
  });

  return (
    <div className="space-y-5">
      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Record Payroll</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <input placeholder="Employee ID" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input type="date" placeholder="Month" value={form.month} onChange={(e) => setForm({ ...form, month: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input type="number" placeholder="Base salary" value={form.base_salary} onChange={(e) => setForm({ ...form, base_salary: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input type="number" placeholder="Overtime" value={form.overtime_pay} onChange={(e) => setForm({ ...form, overtime_pay: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <button onClick={() => recordMutation.mutate()} disabled={!form.employee_id || !form.month || !form.base_salary || recordMutation.isPending}
            className="text-xs font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 disabled:opacity-50">
            {recordMutation.isPending ? "Saving..." : "Record"}
          </button>
        </div>
        {recordMutation.isError && <p className="text-xs text-rose-500 mt-2">{recordMutation.error?.response?.data?.message || "Couldn't record payroll."}</p>}
      </GlassCard>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Payroll Records</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Base salary, overtime, deductions, and net pay</p>
        {payrollQ.isLoading ? <CardSkeleton /> : payrollQ.isError ? (
          <ErrorState message="Couldn't load payroll." onRetry={payrollQ.refetch} />
        ) : payrollQ.data.length === 0 ? <EmptyState title="No payroll records yet" /> : (
          <DataTable
            searchKeys={["employee_name"]}
            columns={[
              { key: "employee_name", label: "Employee", sortable: true },
              { key: "month", label: "Month", sortable: true },
              { key: "base_salary", label: "Base Salary", sortable: true, render: (r) => compactCurrency(r.base_salary) },
              { key: "overtime_pay", label: "Overtime", render: (r) => compactCurrency(r.overtime_pay) },
              { key: "deductions", label: "Deductions", render: (r) => compactCurrency(r.deductions) },
              { key: "net_pay", label: "Net Pay", sortable: true, render: (r) => <span className="font-semibold">{compactCurrency(r.net_pay)}</span> },
            ]}
            rows={payrollQ.data}
          />
        )}
      </GlassCard>
    </div>
  );
}

function ShiftsTab({ outletId }) {
  const queryClient = useQueryClient();
  const shiftsQ = useQuery({
    queryKey: ["staff", "shifts", outletId],
    queryFn: () => staffService.listShifts(outletId ? { outlet_id: outletId } : {}),
  });
  const [form, setForm] = useState({ employee_id: "", shift_date: "", start_time: "09:00", end_time: "17:00" });

  const scheduleMutation = useMutation({
    mutationFn: () => staffService.scheduleShift({ ...form, employee_id: Number(form.employee_id) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff", "shifts"] });
      setForm({ employee_id: "", shift_date: "", start_time: "09:00", end_time: "17:00" });
    },
  });

  return (
    <div className="space-y-5">
      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Schedule a Shift</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <input placeholder="Employee ID" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input type="date" value={form.shift_date} onChange={(e) => setForm({ ...form, shift_date: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <button onClick={() => scheduleMutation.mutate()} disabled={!form.employee_id || !form.shift_date || scheduleMutation.isPending}
            className="flex items-center justify-center gap-1 text-xs font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 disabled:opacity-50">
            <Plus size={12} /> {scheduleMutation.isPending ? "Saving..." : "Schedule"}
          </button>
        </div>
      </GlassCard>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Shift Schedule</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Most recent 200 shifts</p>
        {shiftsQ.isLoading ? <CardSkeleton /> : shiftsQ.isError ? (
          <ErrorState message="Couldn't load shifts." onRetry={shiftsQ.refetch} />
        ) : shiftsQ.data.length === 0 ? <EmptyState title="No shifts scheduled yet" /> : (
          <DataTable
            searchKeys={["employee_name"]}
            columns={[
              { key: "employee_name", label: "Employee", sortable: true },
              { key: "shift_date", label: "Date", sortable: true },
              { key: "start_time", label: "Start" },
              { key: "end_time", label: "End" },
              { key: "status", label: "Status", render: (r) => <StatusBadge label={r.status} tone={r.status === "completed" ? "success" : r.status === "missed" ? "danger" : "info"} /> },
            ]}
            rows={shiftsQ.data}
          />
        )}
      </GlassCard>
    </div>
  );
}

function LeaveTab({ outletId }) {
  const queryClient = useQueryClient();
  const leaveQ = useQuery({
    queryKey: ["staff", "leave", outletId],
    queryFn: () => staffService.listLeave(outletId ? { outlet_id: outletId } : {}),
  });
  const [form, setForm] = useState({ employee_id: "", leave_type: "casual", start_date: "", end_date: "", reason: "" });

  const requestMutation = useMutation({
    mutationFn: () => staffService.requestLeave({ ...form, employee_id: Number(form.employee_id) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["staff", "leave"] });
      setForm({ employee_id: "", leave_type: "casual", start_date: "", end_date: "", reason: "" });
    },
  });

  const decisionMutation = useMutation({
    mutationFn: ({ id, status }) => staffService.decideLeave(id, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["staff", "leave"] }),
  });

  const pending = (leaveQ.data || []).filter((l) => l.status === "pending");

  return (
    <div className="space-y-5">
      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Request Leave</h2>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <input placeholder="Employee ID" value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <select value={form.leave_type} onChange={(e) => setForm({ ...form, leave_type: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2">
            <option value="casual">Casual</option>
            <option value="sick">Sick</option>
            <option value="earned">Earned</option>
            <option value="unpaid">Unpaid</option>
          </select>
          <input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input placeholder="Reason" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <button onClick={() => requestMutation.mutate()} disabled={!form.employee_id || !form.start_date || !form.end_date || requestMutation.isPending}
            className="text-xs font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 disabled:opacity-50">
            {requestMutation.isPending ? "Submitting..." : "Submit"}
          </button>
        </div>
        {requestMutation.isError && <p className="text-xs text-rose-500 mt-2">{requestMutation.error?.response?.data?.message || "Couldn't submit leave request."}</p>}
      </GlassCard>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Leave Requests</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">{pending.length} pending decision</p>
        {leaveQ.isLoading ? <CardSkeleton /> : leaveQ.isError ? (
          <ErrorState message="Couldn't load leave requests." onRetry={leaveQ.refetch} />
        ) : leaveQ.data.length === 0 ? <EmptyState title="No leave requests yet" /> : (
          <div className="space-y-2">
            {leaveQ.data.map((l) => (
              <div key={l.id} className="flex items-center gap-3 rounded-xl border border-slate-100 dark:border-slate-800 p-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{l.employee_name}</p>
                    <span className="text-[11px] text-slate-400 capitalize">{l.leave_type}</span>
                    <StatusBadge label={l.status} tone={leaveStatusTone[l.status]} />
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">{l.start_date} → {l.end_date} {l.reason ? `· ${l.reason}` : ""}</p>
                </div>
                {l.status === "pending" && (
                  <div className="flex gap-1.5 shrink-0">
                    <button onClick={() => decisionMutation.mutate({ id: l.id, status: "approved" })}
                      className="p-1.5 rounded-lg border border-emerald-200 dark:border-emerald-500/30 text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-500/10">
                      <Check size={13} />
                    </button>
                    <button onClick={() => decisionMutation.mutate({ id: l.id, status: "rejected" })}
                      className="p-1.5 rounded-lg border border-rose-200 dark:border-rose-500/30 text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-500/10">
                      <XIcon size={13} />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}

const TABS = [
  { key: "performance", label: "Performance", icon: Award },
  { key: "payroll", label: "Payroll", icon: Wallet },
  { key: "shifts", label: "Shifts", icon: CalendarDays },
  { key: "leave", label: "Leave", icon: ClipboardList },
];

export default function StaffAgent() {
  const [outletId, setOutletId] = useState("");
  const [tab, setTab] = useState("performance");
  const outletsQ = useQuery({ queryKey: ["outlets", "list"], queryFn: () => outletService.list() });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI AGENT · STAFF"
        title="Staff Agent"
        subtitle="Track attendance, payroll, shifts, and leave — with AI-driven performance scores and attrition risk."
        actions={
          <>
            <select value={outletId} onChange={(e) => setOutletId(e.target.value)}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2">
              <option value="">All outlets</option>
              {(outletsQ.data || []).map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
            </select>
            <button className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
              <RefreshCw size={15} />
            </button>
          </>
        }
      />

      <div className="flex bg-slate-100 dark:bg-slate-800/60 rounded-lg p-1 w-fit">
        {TABS.map((t) => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-xs font-medium transition-all ${tab === t.key ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" : "text-slate-500 dark:text-slate-400"}`}>
            <t.icon size={13} /> {t.label}
          </button>
        ))}
      </div>

      {tab === "performance" && <PerformanceTab outletId={outletId} />}
      {tab === "payroll" && <PayrollTab outletId={outletId} />}
      {tab === "shifts" && <ShiftsTab outletId={outletId} />}
      {tab === "leave" && <LeaveTab outletId={outletId} />}
    </div>
  );
}
