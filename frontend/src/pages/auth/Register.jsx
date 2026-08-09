import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, AlertCircle } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Register() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", role: "outlet_manager", outlet_id: "", region: "South" });
  const [error, setError] = useState(null);

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const payload = { ...form, outlet_id: form.outlet_id ? Number(form.outlet_id) : undefined };
      await register(payload);
      navigate("/app/dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || "Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 px-4 py-10">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        className="w-full max-w-sm rounded-2xl border border-slate-200/70 dark:border-slate-700/60 bg-white/80 dark:bg-slate-900/70 backdrop-blur-xl shadow-xl p-8"
      >
        <div className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <span className="font-semibold text-lg text-slate-900 dark:text-white">FranchiseOps AI</span>
        </div>

        <h1 className="text-xl font-bold text-slate-900 dark:text-white mb-1">Create your account</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Get access to the franchise dashboard</p>

        {error && (
          <div className="flex items-center gap-2 text-xs text-rose-600 bg-rose-50 dark:bg-rose-500/10 dark:text-rose-400 rounded-lg px-3 py-2 mb-4">
            <AlertCircle size={14} /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Full name</label>
            <input required value={form.full_name} onChange={update("full_name")}
              className="w-full px-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none" />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Email</label>
            <input type="email" required value={form.email} onChange={update("email")}
              className="w-full px-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none" />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Password</label>
            <input type="password" required minLength={8} value={form.password} onChange={update("password")}
              className="w-full px-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none" />
          </div>
          <div>
            <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Role</label>
            <select value={form.role} onChange={update("role")}
              className="w-full px-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none">
              <option value="outlet_manager">Outlet Manager</option>
              <option value="regional_manager">Regional Manager</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          {form.role === "outlet_manager" && (
            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Outlet ID</label>
              <input type="number" required value={form.outlet_id} onChange={update("outlet_id")}
                placeholder="e.g. 1"
                className="w-full px-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none" />
            </div>
          )}
          {form.role === "regional_manager" && (
            <div>
              <label className="text-xs font-medium text-slate-600 dark:text-slate-300 mb-1 block">Region</label>
              <select value={form.region} onChange={update("region")}
                className="w-full px-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none">
                <option value="North">North</option>
                <option value="South">South</option>
                <option value="East">East</option>
                <option value="West">West</option>
              </select>
            </div>
          )}

          <button type="submit" disabled={loading}
            className="w-full py-2.5 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25 disabled:opacity-60 mt-2">
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="text-xs text-slate-500 dark:text-slate-400 text-center mt-6">
          Already have an account? <Link to="/login" className="text-blue-600 dark:text-blue-400 font-medium hover:underline">Sign in</Link>
        </p>
      </motion.div>
    </div>
  );
}
