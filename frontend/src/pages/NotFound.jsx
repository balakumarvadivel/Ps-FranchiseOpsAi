import { Link } from "react-router-dom";
import { Sparkles } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 px-4 text-center">
      <div>
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center mx-auto mb-4">
          <Sparkles size={24} className="text-white" />
        </div>
        <p className="text-5xl font-bold text-slate-900 dark:text-white mb-2">404</p>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">This page doesn't exist in FranchiseOps AI.</p>
        <Link to="/app/dashboard" className="px-4 py-2 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
