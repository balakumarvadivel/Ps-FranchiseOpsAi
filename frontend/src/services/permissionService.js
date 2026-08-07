import api from "./api";

export const permissionService = {
  list: () => api.get("/permissions").then((r) => r.data),
  matrix: () => api.get("/permissions/matrix").then((r) => r.data),
  updateRole: (role, permissionCodes) =>
    api.put(`/permissions/matrix/${role}`, { permission_codes: permissionCodes }).then((r) => r.data),
  regions: () => api.get("/permissions/regions").then((r) => r.data),
};
