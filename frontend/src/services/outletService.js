import api from "./api";

export const outletService = {
  list: (params = {}) => api.get("/outlets", { params }).then((r) => r.data),
  get: (id) => api.get(`/outlets/${id}`).then((r) => r.data),
  create: (payload) => api.post("/outlets", payload).then((r) => r.data),
  update: (id, payload) => api.put(`/outlets/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/outlets/${id}`),
  ranking: (days = 30) => api.get("/outlets/kpi/ranking", { params: { days } }).then((r) => r.data),
};

export const salesService = {
  list: (params = {}) => api.get("/sales", { params }).then((r) => r.data),
  create: (payload) => api.post("/sales", payload).then((r) => r.data),
  trend: (params = {}) => api.get("/sales/trend", { params }).then((r) => r.data),
};
