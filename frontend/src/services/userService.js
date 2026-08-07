import api from "./api";

export const userService = {
  list: (params = {}) => api.get("/users", { params }).then((r) => r.data),
  get: (id) => api.get(`/users/${id}`).then((r) => r.data),
  update: (id, payload) => api.put(`/users/${id}`, payload).then((r) => r.data),
  deactivate: (id) => api.delete(`/users/${id}`),
};
