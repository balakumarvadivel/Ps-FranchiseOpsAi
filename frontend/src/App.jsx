import { useState } from "react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider, MutationCache } from "@tanstack/react-query";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { ToastProvider, useToast } from "./context/ToastContext";
import { AppRoutes } from "./routes/AppRoutes";

function AppInner() {
  const toast = useToast();

  // Lazy-initialized once via useState, not recreated on every render —
  // a QueryClient must stay stable across the component's lifetime or its
  // cache resets constantly.
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            refetchOnWindowFocus: false,
            retry: 1,
            staleTime: 30_000,
          },
        },
        mutationCache: new MutationCache({
          onError: (error, _variables, _context, mutation) => {
            // Mutations can opt out of the global toast (e.g. a form that
            // shows its own inline error) via meta: { skipGlobalToast: true }.
            if (mutation.meta?.skipGlobalToast) return;
            const message = error?.response?.data?.message || "Something went wrong. Please try again.";
            toast.error(message);
          },
        }),
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <AppInner />
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
