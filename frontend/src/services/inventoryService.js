import api from "./api";

export const inventoryService = {
  list: (params = {}) => api.get("/inventory", { params }).then((r) => r.data),
  updateStock: (id, quantity) => api.put(`/inventory/${id}/stock`, { quantity }).then((r) => r.data),
  createProduct: (payload) => api.post("/inventory/products", payload).then((r) => r.data),
  reorderAlerts: (outletId) =>
    api.get("/inventory/alerts/reorder", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
  transferSuggestions: () => api.get("/inventory/alerts/transfer-suggestions").then((r) => r.data),
  suppliers: () => api.get("/inventory/suppliers").then((r) => r.data),
  createSupplier: (payload) => api.post("/inventory/suppliers", payload).then((r) => r.data),
  batches: (params = {}) => api.get("/inventory/batches", { params }).then((r) => r.data),
  createBatch: (payload) => api.post("/inventory/batches", payload).then((r) => r.data),
  value: (outletId) => api.get("/inventory/value", { params: outletId ? { outlet_id: outletId } : {} }).then((r) => r.data),
};
