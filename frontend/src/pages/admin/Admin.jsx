import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Users, Store, Plus, UserX, Save, Shield } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { userService } from "../../services/userService";
import { outletService } from "../../services/outletService";
import { permissionService } from "../../services/permissionService";

const ROLES = ["admin", "regional_manager", "outlet_manager"];
const REGIONS = ["North", "South", "East", "West"];

function UsersTab() {
  const queryClient = useQueryClient();
  const usersQ = useQuery({ queryKey: ["users", "list"], queryFn: () => userService.list() });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => userService.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  const deactivateMutation = useMutation({
    mutationFn: (id) => userService.deactivate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  if (usersQ.isLoading) return <CardSkeleton />;
  if (usersQ.isError) return <ErrorState message="Couldn't load users." onRetry={usersQ.refetch} />;
  if (!usersQ.data.length) return <EmptyState title="No users yet" />;

  return (
    <DataTable
      searchKeys={["full_name", "email"]}
      columns={[
        { key: "full_name", label: "Name", sortable: true },
        { key: "email", label: "Email", sortable: true },
        {
          key: "role", label: "Role",
          render: (u) => (
            <select
              defaultValue={u.role}
              onChange={(e) => updateMutation.mutate({ id: u.id, payload: { role: e.target.value } })}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1 capitalize"
            >
              {ROLES.map((r) => <option key={r} value={r}>{r.replace("_", " ")}</option>)}
            </select>
          ),
        },
        { key: "outlet_id", label: "Outlet ID", render: (u) => u.outlet_id ?? "—" },
        {
          key: "is_active", label: "Status",
          render: (u) => <StatusBadge label={u.is_active ? "Active" : "Deactivated"} tone={u.is_active ? "success" : "danger"} />,
        },
        {
          key: "actions", label: "",
          render: (u) => u.is_active && (
            <button onClick={() => deactivateMutation.mutate(u.id)}
              className="flex items-center gap-1 text-[11px] font-medium px-2 py-1 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-500/10">
              <UserX size={11} /> Deactivate
            </button>
          ),
        },
      ]}
      rows={usersQ.data}
    />
  );
}

function OutletsTab() {
  const queryClient = useQueryClient();
  const outletsQ = useQuery({ queryKey: ["outlets", "list"], queryFn: () => outletService.list() });
  const regionsQ = useQuery({ queryKey: ["permissions", "regions"], queryFn: permissionService.regions });
  const [form, setForm] = useState({ name: "", code: "", city: "", state: "", region: "South" });
  const [showForm, setShowForm] = useState(false);

  const createMutation = useMutation({
    mutationFn: () => outletService.create(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["outlets"] });
      setForm({ name: "", code: "", city: "", state: "", region: "South" });
      setShowForm(false);
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }) => outletService.update(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["outlets"] }),
  });

  return (
    <div>
      <div className="flex justify-end mb-4">
        <button onClick={() => setShowForm((s) => !s)}
          className="flex items-center gap-1.5 text-xs font-medium px-3 py-2 rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600">
          <Plus size={13} /> New Outlet
        </button>
      </div>

      {showForm && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-5 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input placeholder="Code (e.g. CHN-002)" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input placeholder="City" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <input placeholder="State" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })}
            className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2" />
          <div className="flex gap-2">
            <select value={form.region} onChange={(e) => setForm({ ...form, region: e.target.value })}
              className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2.5 py-2 flex-1">
              {(regionsQ.data || REGIONS.map((r) => ({ name: r }))).map((r) => <option key={r.name}>{r.name}</option>)}
            </select>
            <button onClick={() => createMutation.mutate()} disabled={!form.name || !form.code || createMutation.isPending}
              className="p-2 rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 disabled:opacity-50">
              <Save size={13} />
            </button>
          </div>
          {createMutation.isError && <p className="col-span-full text-xs text-rose-500">{createMutation.error?.response?.data?.message || "Couldn't create outlet."}</p>}
        </div>
      )}

      {outletsQ.isLoading ? <CardSkeleton /> : outletsQ.isError ? (
        <ErrorState message="Couldn't load outlets." onRetry={outletsQ.refetch} />
      ) : (
        <DataTable
          searchKeys={["name", "city"]}
          columns={[
            { key: "name", label: "Name", sortable: true },
            { key: "code", label: "Code" },
            { key: "city", label: "City", sortable: true },
            { key: "region", label: "Region", sortable: true },
            {
              key: "status", label: "Status",
              render: (o) => (
                <select
                  defaultValue={o.status}
                  onChange={(e) => updateStatusMutation.mutate({ id: o.id, status: e.target.value })}
                  className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1 capitalize"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="closed">Closed</option>
                </select>
              ),
            },
          ]}
          rows={outletsQ.data}
        />
      )}
    </div>
  );
}

function PermissionsTab() {
  const queryClient = useQueryClient();
  const matrixQ = useQuery({ queryKey: ["permissions", "matrix"], queryFn: permissionService.matrix });
  const permsQ = useQuery({ queryKey: ["permissions", "list"], queryFn: permissionService.list });

  const updateMutation = useMutation({
    mutationFn: ({ role, codes }) => permissionService.updateRole(role, codes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["permissions", "matrix"] }),
  });

  const togglePermission = (role, currentCodes, code) => {
    const next = currentCodes.includes(code) ? currentCodes.filter((c) => c !== code) : [...currentCodes, code];
    updateMutation.mutate({ role, codes: next });
  };

  if (matrixQ.isLoading || permsQ.isLoading) return <CardSkeleton />;
  if (matrixQ.isError || permsQ.isError) return <ErrorState message="Couldn't load permissions." onRetry={() => { matrixQ.refetch(); permsQ.refetch(); }} />;
  if (!permsQ.data.length) return <EmptyState title="No permissions defined yet" />;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm min-w-[600px]">
        <thead>
          <tr className="text-left text-[11px] uppercase tracking-wide text-slate-400 border-b border-slate-200 dark:border-slate-800">
            <th className="py-2.5 pr-4 font-medium">Permission</th>
            {matrixQ.data.map((r) => <th key={r.role} className="py-2.5 pr-4 font-medium capitalize">{r.role.replace("_", " ")}</th>)}
          </tr>
        </thead>
        <tbody>
          {permsQ.data.map((p) => (
            <tr key={p.id} className="border-b border-slate-100 dark:border-slate-800/60">
              <td className="py-2.5 pr-4">
                <p className="font-mono text-xs text-slate-700 dark:text-slate-200">{p.code}</p>
                <p className="text-[11px] text-slate-400">{p.description}</p>
              </td>
              {matrixQ.data.map((r) => (
                <td key={r.role} className="py-2.5 pr-4">
                  <input
                    type="checkbox"
                    checked={r.permissions.includes(p.code)}
                    disabled={r.role === "admin"}
                    onChange={() => togglePermission(r.role, r.permissions, p.code)}
                    className="w-4 h-4 accent-blue-600 disabled:opacity-40"
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-[11px] text-slate-400 mt-3">Admin always has every permission and can't be edited here.</p>
    </div>
  );
}

export default function Admin() {
  const [tab, setTab] = useState("users");

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="ADMINISTRATION" title="Admin" subtitle="Manage users, roles, permissions, and outlets across the franchise network." />

      <div className="flex bg-slate-100 dark:bg-slate-800/60 rounded-lg p-1 w-fit">
        <button onClick={() => setTab("users")}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-xs font-medium transition-all ${tab === "users" ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" : "text-slate-500 dark:text-slate-400"}`}>
          <Users size={13} /> Users
        </button>
        <button onClick={() => setTab("outlets")}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-xs font-medium transition-all ${tab === "outlets" ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" : "text-slate-500 dark:text-slate-400"}`}>
          <Store size={13} /> Outlets
        </button>
        <button onClick={() => setTab("permissions")}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-xs font-medium transition-all ${tab === "permissions" ? "bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm" : "text-slate-500 dark:text-slate-400"}`}>
          <Shield size={13} /> Permissions
        </button>
      </div>

      <GlassCard className="p-5">
        {tab === "users" ? <UsersTab /> : tab === "outlets" ? <OutletsTab /> : <PermissionsTab />}
      </GlassCard>
    </div>
  );
}
