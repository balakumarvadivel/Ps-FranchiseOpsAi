import axios from "axios";

// In dev, requests to /api/v1/* are proxied to the FastAPI backend by vite.config.js.
// In production (e.g. Vercel frontend + Render backend), set VITE_API_BASE_URL to the
// full backend URL, e.g. https://franchiseops-api.onrender.com/api/v1
const baseURL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
    }
    return Promise.reject(error);
  }
);

export default api;
