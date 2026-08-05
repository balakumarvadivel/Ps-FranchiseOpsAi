import { useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, CheckCircle2 } from "lucide-react";
import { authService } from "../../services/authService";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await authService.forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(err.response?.data?.message || "Something went wrong");
    } finally {
      setLoading(false);
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

        {sent ? (
          <div className="text-center py-4">
            <CheckCircle2 size={36} className="text-emerald-500 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-800 dark:text-slate-100">Check your email</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              If an account exists for {email}, a reset link has been sent.
            </p>
            <Link to="/login" className="inline-block mt-5 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline">
              Back to sign in
            </Link>
          </div>
        ) : (
          <>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white mb-1">Reset your password</h1>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Enter your email and we'll send you a reset link.</p>

            {error && <div className="text-xs text-rose-600 bg-rose-50 dark:bg-rose-500/10 dark:text-rose-400 rounded-lg px-3 py-2 mb-4">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-4">
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                placeholder="you@franchiseops.ai"
                className="w-full px-3 py-2.5 text-sm rounded-xl bg-slate-100/80 dark:bg-slate-800/60 border border-transparent focus:border-blue-400 focus:outline-none" />
              <button type="submit" disabled={loading}
                className="w-full py-2.5 rounded-xl text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 shadow-md shadow-blue-500/25 disabled:opacity-60">
                {loading ? "Sending..." : "Send reset link"}
              </button>
            </form>

            <p className="text-xs text-slate-500 dark:text-slate-400 text-center mt-6">
              <Link to="/login" className="text-blue-600 dark:text-blue-400 font-medium hover:underline">Back to sign in</Link>
            </p>
          </>
        )}
      </motion.div>
    </div>
  );
}
