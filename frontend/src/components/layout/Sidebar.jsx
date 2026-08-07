import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Store, Boxes, Users, Megaphone, ShieldCheck, Brain,
  Lightbulb, FileBarChart, Settings, Sparkles, X, Zap, UploadCloud, UserCog,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";

const baseNavItems = [
  { to: "/app/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/app/data-validation", label: "Data Validation", icon: UploadCloud },
  { to: "/app/outlets", label: "Outlet Performance Agent", icon: Store },
  { to: "/app/inventory", label: "Inventory Agent", icon: Boxes },
  { to: "/app/staff", label: "Staff Agent", icon: Users },
  { to: "/app/marketing", label: "Marketing Agent", icon: Megaphone },
  { to: "/app/audit", label: "Audit Agent", icon: ShieldCheck },
  { to: "/app/intelligence", label: "Intelligence Engine", icon: Brain },
  { to: "/app/recommendations", label: "Recommendations", icon: Lightbulb },
  { to: "/app/reports", label: "Reports", icon: FileBarChart },
  { to: "/app/settings", label: "Settings", icon: Settings },
];

const adminNavItem = { to: "/app/admin", label: "Admin", icon: UserCog };

export function Sidebar({ open, onClose }) {
  const { user } = useAuth();
  const navItems = ["admin", "regional_manager"].includes(user?.role)
    ? [...baseNavItems.slice(0, -1), adminNavItem, baseNavItems[baseNavItems.length - 1]]
    : baseNavItems;

  return (
    <>
      <aside
        className={`fixed lg:sticky top-0 z-40 h-screen w-64 shrink-0 border-r border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl flex flex-col
          ${open ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 transition-transform duration-300`}
      >
        <div className="flex items-center gap-2 px-6 h-16 border-b border-slate-200/70 dark:border-slate-800">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Sparkles size={18} className="text-white" />
          </div>
          <span className="font-semibold tracking-tight text-slate-900 dark:text-white">FranchiseOps AI</span>
          <button className="ml-auto lg:hidden" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all group relative ${
                  isActive
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md shadow-blue-500/25"
                    : "text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon size={17} className={isActive ? "text-white" : "text-slate-400 group-hover:text-blue-500"} />
                  <span className="font-medium truncate">{item.label}</span>
                  {isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-white animate-pulse" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-200/70 dark:border-slate-800">
          <div className="rounded-xl bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-500/10 dark:to-purple-500/10 border border-blue-100 dark:border-blue-500/20 p-3">
            <div className="flex items-center gap-2 text-xs font-medium text-blue-700 dark:text-blue-300">
              <Zap size={14} /> AI Engine Active
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">Live data from FastAPI backend</p>
          </div>
        </div>
      </aside>
      {open && <div className="fixed inset-0 bg-black/30 z-30 lg:hidden" onClick={onClose} />}
    </>
  );
}
