import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Menu, Search, Bell, Sun, Moon, Sparkles, LogOut } from "lucide-react";
import { useTheme } from "../../context/ThemeContext";
import { useAuth } from "../../context/AuthContext";
import { useQuery } from "@tanstack/react-query";
import { alertService } from "../../services/aiService";

export function Navbar({ onMenuClick }) {
  const { dark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [now, setNow] = useState(new Date());
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 30000);
    return () => clearInterval(t);
  }, []);

  const { data: alerts } = useQuery({
    queryKey: ["alerts", "unread"],
    queryFn: () => alertService.list({ unread_only: true }),
    refetchInterval: 60000,
    retry: false,
  });
  const unreadCount = alerts?.length || 0;

  const initials = (user?.full_name || "U")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <header className="sticky top-0 z-20 h-16 border-b border-slate-200/70 dark:border-slate-800 bg-white/70 dark:bg-slate-950/70 backdrop-blur-xl flex items-center gap-4 px-4 lg:px-8">
      <button className="lg:hidden" onClick={onMenuClick}>
        <Menu size={20} />
      </button>

      <div className="relative hidden md:block w-72">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          placeholder="Search outlets, reports, insights..."
          className="w-full pl-9 pr-3 py-2 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:bg-white dark:focus:bg-slate-900 focus:outline-none focus:ring-4 focus:ring-blue-500/10 transition-all"
        />
      </div>

      <div className="ml-auto flex items-center gap-2 lg:gap-3">
        <button
          onClick={() => navigate("/app/intelligence")}
          className="hidden sm:flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25"
        >
          <Sparkles size={15} /> AI Assistant
        </button>

        <button onClick={() => navigate("/app/settings")} className="relative p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/60">
          <Bell size={18} />
          {unreadCount > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white dark:ring-slate-950" />
          )}
        </button>

        <button onClick={toggleTheme} className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800/60">
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className="hidden md:block text-right leading-tight px-2 border-l border-slate-200 dark:border-slate-800 ml-1 pl-3">
          <p className="text-xs font-medium text-slate-700 dark:text-slate-200">
            {now.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
          </p>
          <p className="text-[11px] text-slate-400">{now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}</p>
        </div>

        <div className="relative">
          <button onClick={() => setMenuOpen((o) => !o)}
                  className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-semibold shadow-md">
            {initials}
          </button>
          {menuOpen && (
            <div className="absolute right-0 mt-2 w-48 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 shadow-xl p-1.5 text-sm">
              <div className="px-2.5 py-2 border-b border-slate-100 dark:border-slate-800 mb-1">
                <p className="font-medium text-slate-800 dark:text-slate-100 truncate">{user?.full_name}</p>
                <p className="text-[11px] text-slate-400 truncate">{user?.email}</p>
              </div>
              <button onClick={logout} className="w-full flex items-center gap-2 px-2.5 py-2 rounded-lg text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-500/10">
                <LogOut size={14} /> Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
