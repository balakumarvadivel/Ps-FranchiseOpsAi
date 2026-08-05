import { useMemo, useState } from "react";
import { ArrowUpDown, ChevronLeft, ChevronRight, Search } from "lucide-react";

/**
 * Generic data table.
 * columns: [{ key, label, render?: (row) => node, sortable?: bool }]
 */
export function DataTable({ columns, rows, searchable = true, pageSize = 8, searchKeys = [] }) {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState("desc");
  const [page, setPage] = useState(1);

  const filtered = useMemo(() => {
    let data = rows;
    if (search && searchKeys.length) {
      const q = search.toLowerCase();
      data = data.filter((row) => searchKeys.some((k) => String(row[k] ?? "").toLowerCase().includes(q)));
    }
    if (sortKey) {
      data = [...data].sort((a, b) => {
        const dir = sortDir === "asc" ? 1 : -1;
        return a[sortKey] > b[sortKey] ? dir : a[sortKey] < b[sortKey] ? -dir : 0;
      });
    }
    return data;
  }, [rows, search, sortKey, sortDir, searchKeys]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  return (
    <div>
      {searchable && (
        <div className="relative w-full sm:w-64 mb-3">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search..."
            className="w-full pl-8 pr-3 py-2 text-xs rounded-lg bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none"
          />
        </div>
      )}

      <div className="overflow-x-auto -mx-1 px-1">
        <table className="w-full text-sm min-w-[600px]">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wide text-slate-400 border-b border-slate-200 dark:border-slate-800">
              {columns.map((col) => (
                <th key={col.key} className="py-2.5 pr-4 font-medium">
                  {col.sortable ? (
                    <button onClick={() => toggleSort(col.key)} className="flex items-center gap-1 hover:text-slate-600 dark:hover:text-slate-300">
                      {col.label} <ArrowUpDown size={11} className={sortKey === col.key ? "text-blue-500" : ""} />
                    </button>
                  ) : col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="py-8 text-center text-sm text-slate-400">
                  No records found
                </td>
              </tr>
            ) : (
              paged.map((row, i) => (
                <tr key={row.id ?? i} className="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50/80 dark:hover:bg-slate-800/40 transition-colors">
                  {columns.map((col) => (
                    <td key={col.key} className="py-3 pr-4">
                      {col.render ? col.render(row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
          <span className="text-xs text-slate-400">Page {page} of {totalPages} · {filtered.length} records</span>
          <div className="flex gap-1.5">
            <button disabled={page === 1} onClick={() => setPage((p) => p - 1)}
                    className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-slate-800">
              <ChevronLeft size={14} />
            </button>
            <button disabled={page === totalPages} onClick={() => setPage((p) => p + 1)}
                    className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-slate-800">
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
