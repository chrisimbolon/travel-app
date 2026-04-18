import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { adminApi } from "@/lib/api/admin";
import { Route } from "@/types";
import toast from "react-hot-toast";

export function useAdminStats() {
  return useQuery({
    queryKey: ["admin", "stats"],
    queryFn: () => adminApi.getStats().then((r) => r.data),
  });
}

export function useAdminOperators() {
  return useQuery({
    queryKey: ["admin", "operators"],
    queryFn: () => adminApi.getOperators().then((r) => r.data),
  });
}

export function useApproveOperator() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => adminApi.approveOperator(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "operators"] });
      toast.success("Operator diaktifkan.");
    },
  });
}

export function useSuspendOperator() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => adminApi.suspendOperator(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "operators"] });
      toast.success("Operator disuspend.");
    },
  });
}

export function useAdminRoutes() {
  return useQuery({
    queryKey: ["admin", "routes"],
    queryFn: () => adminApi.getRoutes().then((r) => r.data),
  });
}

export function useCreateRoute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Omit<Route, "id">) => adminApi.createRoute(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "routes"] });
      toast.success("Rute baru ditambahkan.");
    },
    onError: () => toast.error("Gagal menambah rute."),
  });
}

export function useToggleRoute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      adminApi.toggleRoute(id, is_active).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "routes"] }),
  });
}
