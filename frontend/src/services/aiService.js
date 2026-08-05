import api from "./api";

export const aiService = {
  outletHealthScore: (outletId) => api.get(`/ai/outlets/${outletId}/health-score`).then((r) => r.data),
  forecastRevenue: (params = {}) => api.get("/ai/forecast/revenue", { params }).then((r) => r.data),
  recommendations: () => api.get("/ai/recommendations").then((r) => r.data),
  executiveSummary: () => api.get("/ai/executive-summary").then((r) => r.data),
};

export const recommendationService = {
  list: (params = {}) => api.get("/recommendations", { params }).then((r) => r.data),
  updateStatus: (id, status) => api.put(`/recommendations/${id}/status`, { status }).then((r) => r.data),
  refresh: () => api.post("/recommendations/refresh").then((r) => r.data),
};

export const alertService = {
  list: (params = {}) => api.get("/alerts", { params }).then((r) => r.data),
  markRead: (id) => api.put(`/alerts/${id}/read`).then((r) => r.data),
  scan: () => api.post("/alerts/scan").then((r) => r.data),
};

export const notificationService = {
  list: (unreadOnly = false) =>
    api.get("/notifications", { params: { unread_only: unreadOnly } }).then((r) => r.data),
  markRead: (id) => api.put(`/notifications/${id}/read`).then((r) => r.data),
  markAllRead: () => api.put("/notifications/read-all").then((r) => r.data),
};

export const reportService = {
  generate: (payload) => api.post("/reports/generate", payload).then((r) => r.data),
  list: () => api.get("/reports").then((r) => r.data),
  download: async (id, suggestedName = "report") => {
    const response = await api.get(`/reports/${id}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    const disposition = response.headers["content-disposition"];
    const match = disposition && disposition.match(/filename="?([^"]+)"?/);
    link.download = match ? match[1] : suggestedName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
