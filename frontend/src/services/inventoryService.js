import api from "./api";

export const inventoryService = {
  list: (params = {}) => api.get("/inventory", { params }).then((r) => r.data),
  updateStock: (id, quantity) => api.put(`/inventory/${id}/stock`, { quantity }).then((r) => r.data),
  createProduct: (payload) => api.post("/inventory/products", payload).then((r) => r.data),
  reorderAlerts: (outletId) =>
    api.get("/inventory/alerts/reorder", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  transferSuggestions: () => api.get("/inventory/alerts/transfer-suggestions").then((r) => r.data),
};
