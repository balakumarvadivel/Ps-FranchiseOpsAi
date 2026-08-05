import { useQuery } from "@tanstack/react-query";
import { RefreshCw, Boxes, PackageX, PackageCheck, ArrowLeftRight } from "lucide-react";

import { PageHeader } from "../../components/common/PageHeader";
import { KPICard } from "../../components/common/KPICard";
import { GlassCard } from "../../components/common/GlassCard";
import { DataTable } from "../../components/common/DataTable";
import { StatusBadge } from "../../components/common/StatusBadge";
import { AIRecommendationCard } from "../../components/ai/AIRecommendationCard";
import { CardSkeleton, ErrorState, EmptyState } from "../../components/common/States";

import { inventoryService } from "../../services/inventoryService";

const statusTone = { in_stock: "success", low_stock: "warning", out_of_stock: "danger", overstock: "info" };

export default function InventoryAgent() {
  const inventoryQ = useQuery({ queryKey: ["inventory", "list"], queryFn: () => inventoryService.list() });
  const reorderQ = useQuery({ queryKey: ["inventory", "reorder"], queryFn: () => inventoryService.reorderAlerts() });
  const transferQ = useQuery({ queryKey: ["inventory", "transfer"], queryFn: () => inventoryService.transferSuggestions() });

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
    </div>
  );
}
