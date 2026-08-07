import { Routes, Route, Navigate } from "react-router-dom";

import { DashboardLayout } from "../components/layout/DashboardLayout";
import { ProtectedRoute } from "./ProtectedRoute";

import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";
import ForgotPassword from "../pages/auth/ForgotPassword";
import Dashboard from "../pages/dashboard/Dashboard";
import DataValidation from "../pages/data-validation/DataValidation";
import OutletAgent from "../pages/outlet-agent/OutletAgent";
import InventoryAgent from "../pages/inventory-agent/InventoryAgent";
import StaffAgent from "../pages/staff-agent/StaffAgent";
import MarketingAgent from "../pages/marketing-agent/MarketingAgent";
import AuditAgent from "../pages/audit-agent/AuditAgent";
import IntelligenceEngine from "../pages/intelligence-engine/IntelligenceEngine";
import Recommendations from "../pages/recommendations/Recommendations";
import Reports from "../pages/reports/Reports";
import Settings from "../pages/settings/Settings";
import Admin from "../pages/admin/Admin";
import NotFound from "../pages/NotFound";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />

      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="data-validation" element={<DataValidation />} />
        <Route path="outlets" element={<OutletAgent />} />
        <Route path="inventory" element={<InventoryAgent />} />
        <Route path="staff" element={<StaffAgent />} />
        <Route path="marketing" element={<MarketingAgent />} />
        <Route path="audit" element={<AuditAgent />} />
        <Route path="intelligence" element={<IntelligenceEngine />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
        <Route
          path="admin"
          element={
            <ProtectedRoute allowedRoles={["admin", "regional_manager"]}>
              <Admin />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
