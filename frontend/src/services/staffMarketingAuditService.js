import api from "./api";

export const staffService = {
  listEmployees: (outletId) =>
    api.get("/staff/employees", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  createEmployee: (payload) => api.post("/staff/employees", payload).then((r) => r.data),
  markAttendance: (payload) => api.post("/staff/attendance", payload).then((r) => r.data),
  scheduleShift: (payload) => api.post("/staff/shifts", payload).then((r) => r.data),
  recordPayroll: (payload) => api.post("/staff/payroll", payload).then((r) => r.data),
  performance: (outletId) =>
    api.get("/staff/performance", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  bestEmployee: (outletId) => api.get(`/staff/best-employee/${outletId}`).then((r) => r.data),
  shiftOptimization: (outletId) => api.get(`/staff/shift-optimization/${outletId}`).then((r) => r.data),
};

export const marketingService = {
  listCampaigns: (outletId) =>
    api.get("/marketing/campaigns", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  createCampaign: (payload) => api.post("/marketing/campaigns", payload).then((r) => r.data),
  updateCampaign: (id, payload) => api.put(`/marketing/campaigns/${id}`, payload).then((r) => r.data),
  ranking: (outletId) =>
    api.get("/marketing/campaigns/ranking", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  bestWorst: (outletId) =>
    api.get("/marketing/campaigns/best-worst", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  segments: (outletId) =>
    api.get("/marketing/customers/segments", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  budgetOptimization: () => api.get("/marketing/budget-optimization").then((r) => r.data),
  campaignRecommendation: (region) =>
    api.get("/marketing/campaign-recommendation", { params: { region } }).then((r) => r.data),
};

export const auditService = {
  list: (params = {}) => api.get("/audits", { params }).then((r) => r.data),
  pending: () => api.get("/audits/pending").then((r) => r.data),
  schedule: (payload) => api.post("/audits", payload).then((r) => r.data),
  complete: (id, payload) => api.put(`/audits/${id}/complete`, payload).then((r) => r.data),
  addFinding: (payload) => api.post("/audits/reports", payload).then((r) => r.data),
  reportsFor: (auditId) => api.get(`/audits/${auditId}/reports`).then((r) => r.data),
  risk: (auditId) => api.get(`/audits/${auditId}/risk`).then((r) => r.data),
  riskOverview: () => api.get("/audits/risk/overview").then((r) => r.data),
};
