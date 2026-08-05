import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useAuth();

  if (allowedRoles && user && !allowedRoles.includes(user?.role)) {
    return (
      <div className="flex items-center justify-center h-full p-10 text-center">
        <div>
          <p className="text-lg font-semibold text-slate-800 dark:text-white">Access restricted</p>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Your role ({user?.role}) doesn't have access to this page.
          </p>
        </div>
      </div>
    );
  }

  return children;
}
