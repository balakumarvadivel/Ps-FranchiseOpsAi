import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Boxes, PackageX, PackageCheck, ArrowLeftRight, Wallet, Repeat, Truck, Plus, CalendarClock } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { AIRecommendationCard } from "../../components/ai/AIRecommendationCard";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { inventoryService } from "../../services/inventoryService";
import { compactCurrency } from "../../utils/formatters";

const statusTone = { in_stock: "success", low_stock: "warning", out_of_stock: "danger", overstock: "info" };

export default function InventoryAgent() {
  const queryClient = useQueryClient();
  const inventoryQ = useQuery({ queryKey: ["inventory", "list"], queryFn: () => inventoryService.list() });
  const reorderQ = useQuery({ queryKey: ["inventory", "reorder"], queryFn: () => inventoryService.reorderAlerts() });
  const transferQ = useQuery({ queryKey: ["inventory", "transfer"], queryFn: () => inventoryService.transferSuggestions() });
  const valueQ = useQuery({ queryKey: ["inventory", "value"], queryFn: () => inventoryService.value() });
  const suppliersQ = useQuery({ queryKey: ["inventory", "suppliers"], queryFn: inventoryService.suppliers });
  const batchesQ = useQuery({ queryKey: ["inventory", "batches", "expiring"], queryFn: () => inventoryService.batches({ expiring_within_days: 30 }) });

  const [supplierForm, setSupplierForm] = useState({ name: "", contact_person: "", phone: "", email: "" });
  const [showSupplierForm, setShowSupplierForm] = useState(false);

  const createSupplierMutation = useMutation({
    mutationFn: () => inventoryService.createSupplier(supplierForm),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory", "suppliers"] });
      setSupplierForm({ name: "", contact_person: "", phone: "", email: "" });
      setShowSupplierForm(false);
    },
  });

  const rows = inventoryQ.data || [];
  const lowStock = rows.filter((r) => r.warehouse_status === "low_stock").length;
  const outOfStock = rows.filter((r) => r.warehouse_status === "out_of_stock").length;
  const overstock = rows.filter((r) => r.warehouse_status === "overstock").length;
  const healthy = rows.length ? Math.round(((rows.length - lowStock - outOfStock) / rows.length) * 100) : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="AI AGENT · INVENTORY"
        title="Inventory Agent"
        subtitle="Track stock levels, detect shortages and overstock, and get AI-recommended reorder quantities and transfers."
        actions={
          <button onClick={() => { inventoryQ.refetch(); reorderQ.refetch(); transferQ.refetch(); }}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-900/60">
            <RefreshCw size={15} />
          </button>
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Total SKUs Tracked" value={rows.length} icon={Boxes} color="#3b82f6" trend="live" />
        <KPICard label="Low / Out of Stock" value={lowStock + outOfStock} icon={PackageX} color="#f43f5e" trend="needs action" up={false} />
        <KPICard label="Overstocked" value={overstock} icon={Boxes} color="#f59e0b" trend="review" />
        <KPICard label="Stock Health" value={`${healthy}%`} icon={PackageCheck} color="#10b981" trend="in-stock ratio" />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard label="Inventory Value" value={valueQ.data ? compactCurrency(valueQ.data.total_inventory_value) : "—"} icon={Wallet} color="#8b5cf6" trend="at cost price" />
        <KPICard label="Units On Hand" value={valueQ.data?.total_units_on_hand ?? "—"} icon={Boxes} color="#06b6d4" trend="live" />
        <KPICard label="Units Sold (90d)" value={valueQ.data?.units_sold_last_90_days ?? "—"} icon={Repeat} color="#10b981" trend="90 days" />
        <KPICard label="Inventory Turnover" value={valueQ.data ? `${valueQ.data.inventory_turnover_90d}x` : "—"} icon={Repeat} color="#f59e0b" trend="90d ratio" />
      </div>

      <GlassCard className="p-5">
        <h2 className="font-semibold text-slate-900 dark:text-white mb-1">Current Stock — All Outlets</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Live inventory levels from the database</p>
        {inventoryQ.isLoading ? <CardSkeleton /> : inventoryQ.isError ? (
          <ErrorState message="Couldn't load inventory." onRetry={inventoryQ.refetch} />
        ) : rows.length === 0 ? <EmptyState title="No inventory records yet" /> : (
          <DataTable
            searchKeys={["product_name"]}
            columns={[
              { key: "product_name", label: "Product", sortable: true },
              { key: "quantity", label: "Quantity", sortable: true },
              { key: "reorder_level", label: "Reorder Level", sortable: true },
              { key: "warehouse_status", label: "Status", render: (r) => (
                <StatusBadge label={r.warehouse_status.replace("_", " ")} tone={statusTone[r.warehouse_status] || "info"} />
              ) },
            ]}
            rows={rows}
          />
        )}
      </GlassCard>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <GlassCard className="p-5">
          <h2 className="font-semibold text-slate-900 dark:text-white mb-1">AI Reorder Recommendations</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Products at or below reorder level, prioritized</p>
          {reorderQ.isLoading ? <CardSkeleton /> : reorderQ.isError ? (
            <ErrorState message="Couldn't load recommendations." onRetry={reorderQ.refetch} />
          ) : reorderQ.data.length === 0 ? <EmptyState title="No reorder alerts right now" /> : (
            <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
              {reorderQ.data.map((rec, i) => <AIRecommendationCard key={i} rec={rec} />)}
            </div>
          )}
        </GlassCard>

        <GlassCard className="p-5">
          <div className="flex items-center gap-2 mb-1">
            <ArrowLeftRight size={16} className="text-blue-500" />
            <h2 className="font-semibold text-slate-900 dark:text-white">Suggested Stock Transfers</h2>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Overstocked outlets matched against understocked ones</p>
          {transferQ.isLoading ? <CardSkeleton /> : transferQ.isError ? (
            <ErrorState message="Couldn't load transfer suggestions." onRetry={transferQ.refetch} />
          ) : transferQ.data.length === 0 ? <EmptyState title="No transfer opportunities right now" /> : (
            <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
              {transferQ.data.map((rec, i) => <AIRecommendationCard key={i} rec={rec} />)}
            </div>
          )}
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
        <GlassCard className="p-5">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Truck size={16} className="text-blue-500" />
              <h2 className="font-semibold text-slate-900 dark:text-white">Suppliers</h2>
            </div>
            <button onClick={() => setShowSupplierForm((s) => !s)}
              className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800">
              <Plus size={11} /> Add Supplier
            </button>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Suppliers feeding products into the network</p>

          {showSupplierForm && (
            <div className="grid grid-cols-2 gap-2 mb-4 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
              <input placeholder="Name" value={supplierForm.name} onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
                className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5 col-span-2" />
              <input placeholder="Contact person" value={supplierForm.contact_person} onChange={(e) => setSupplierForm({ ...supplierForm, contact_person: e.target.value })}
                className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5" />
              <input placeholder="Phone" value={supplierForm.phone} onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })}
                className="text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-2 py-1.5" />
              <button onClick={() => createSupplierMutation.mutate()} disabled={!supplierForm.name || createSupplierMutation.isPending}
                className="col-span-2 text-xs font-medium py-1.5 rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 disabled:opacity-50">
                {createSupplierMutation.isPending ? "Saving..." : "Save Supplier"}
              </button>
            </div>
          )}

          {suppliersQ.isLoading ? <CardSkeleton /> : suppliersQ.isError ? (
            <ErrorState message="Couldn't load suppliers." onRetry={suppliersQ.refetch} />
          ) : suppliersQ.data.length === 0 ? <EmptyState title="No suppliers yet" /> : (
            <div className="space-y-2">
              {suppliersQ.data.map((s) => (
                <div key={s.id} className="flex items-center gap-3 rounded-xl border border-slate-100 dark:border-slate-800 p-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-500/10 flex items-center justify-center shrink-0">
                    <Truck size={14} className="text-blue-500" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{s.name}</p>
                    <p className="text-[11px] text-slate-400">{s.contact_person || "—"} {s.phone ? `· ${s.phone}` : ""}</p>
                  </div>
                  {s.rating > 0 && <span className="text-xs text-amber-500 font-medium shrink-0">★ {s.rating}</span>}
                </div>
              ))}
            </div>
          )}
        </GlassCard>

        <GlassCard className="p-5">
          <div className="flex items-center gap-2 mb-1">
            <CalendarClock size={16} className="text-rose-500" />
            <h2 className="font-semibold text-slate-900 dark:text-white">Batch & Expiry Tracking</h2>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Batches expiring within the next 30 days</p>

          {batchesQ.isLoading ? <CardSkeleton /> : batchesQ.isError ? (
            <ErrorState message="Couldn't load batch data." onRetry={batchesQ.refetch} />
          ) : batchesQ.data.length === 0 ? <EmptyState title="Nothing expiring soon" subtitle="No batches are within their expiry window." /> : (
            <div className="space-y-2 max-h-[360px] overflow-y-auto pr-1">
              {batchesQ.data.map((b) => {
                const daysLeft = Math.ceil((new Date(b.expiry_date) - new Date()) / 86400000);
                return (
                  <div key={b.id} className="flex items-center gap-3 rounded-xl border border-slate-100 dark:border-slate-800 p-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{b.product_name} <span className="text-slate-400 font-normal">· {b.outlet_name}</span></p>
                      <p className="text-[11px] text-slate-400">Batch {b.batch_number} · {b.quantity} units · expires {b.expiry_date}</p>
                    </div>
                    <StatusBadge label={daysLeft < 0 ? "Expired" : `${daysLeft}d left`} tone={daysLeft < 0 ? "danger" : daysLeft <= 7 ? "warning" : "info"} />
                  </div>
                );
              })}
            </div>
          )}
        </GlassCard>
      </div>
    </div>
  );
}
