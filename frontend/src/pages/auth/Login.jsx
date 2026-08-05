import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, Mail, Lock, AlertCircle } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      navigate(location.state?.from?.pathname || "/app/dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || "Invalid email or password");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 px-4">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        className="w-full max-w-sm rounded-2xl border border-slate-200/70 dark:border-slate-700/60 bg-white/80 dark:bg-slate-900/70 backdrop-blur-xl shadow-xl p-8"
      >
        <div className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <span className="font-semibold text-lg text-slate-900 dark:text-white">FranchiseOps AI</span>
        </div>

        <h1 className="text-xl font-bold text-slate-900 dark:text-white mb-1">Welcome back</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Sign in to your franchise dashboard</p>

        {error && (
          <div className="flex items-center gap-2 text-xs text-rose-600 bg-rose-50 dark:bg-rose-500/10 dark:text-rose-400 rounded-lg px-3 py-2 mb-4">
            <AlertCircle size={14} /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Email</label>
            <div className="relative">
              <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="you@franchiseops.ai"
                className="w-full pl-9 pr-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-500/10" />
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Password</label>
            <div className="relative">
              <Lock size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none focus:ring-4 focus:ring-blue-500/10" />
            </div>
            <div className="text-right mt-1.5">
              <Link to="/forgot-password" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">Forgot password?</Link>
            </div>
          </div>

          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25 disabled:opacity-60">
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="text-xs text-slate-500 dark:text-slate-400 text-center mt-6">
          Don't have an account? <Link to="/register" className="text-blue-600 dark:text-blue-400 font-medium hover:underline">Register</Link>
        </p>
      </motion.div>
    </div>
  );
}
