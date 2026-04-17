import { apiClient } from "./client";
import { Operator, Route, AdminStats } from "@/types";

export const adminApi = {
  getStats: (): Promise<{ data: AdminStats }> =>
    apiClient.get("/admin/stats"),

  // Operators
  getOperators: (): Promise<{ data: Operator[] }> =>
    apiClient.get("/admin/operators"),

  approveOperator: (id: string): Promise<{ data: Operator }> =>
    apiClient.patch(`/admin/operators/${id}/approve`),

  suspendOperator: (id: string): Promise<{ data: Operator }> =>
    apiClient.patch(`/admin/operators/${id}/suspend`),

  // Routes
  getRoutes: (): Promise<{ data: Route[] }> =>
    apiClient.get("/admin/routes"),

  createRoute: (data: Omit<Route, "id">): Promise<{ data: Route }> =>
    apiClient.post("/admin/routes", data),

  toggleRoute: (id: string, is_active: boolean): Promise<{ data: Route }> =>
    apiClient.patch(`/admin/routes/${id}`, { is_active }),
};
