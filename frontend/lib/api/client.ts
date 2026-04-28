import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE,   // no /api/v1 — backend has no version prefix
  headers: { "Content-Type": "application/json" },
});

// Read token from Zustand store, not raw localStorage
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    // Zustand persist stores state as JSON under the store name
    try {
      const raw = localStorage.getItem("transitku-auth");
      if (raw) {
        const { state } = JSON.parse(raw);
        if (state?.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`;
        }
      }
    } catch {
      // ignore parse errors
    }
  }
  return config;
});

// Handle 401 globally
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("transitku-auth");
      window.location.href = "/auth";
    }
    return Promise.reject(err);
  }
);