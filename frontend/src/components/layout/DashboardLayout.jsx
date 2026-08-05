import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";

export function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-white to-blue-50/40 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 text-slate-800 dark:text-slate-100 transition-colors duration-300 flex">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 min-w-0 flex flex-col">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 px-4 lg:px-8 py-6 space-y-6 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
