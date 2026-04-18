import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { operatorApi } from "@/lib/api/operator";
import { TripCreate } from "@/types";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

export function useOperatorStats() {
  return useQuery({
    queryKey: ["operator", "stats"],
    queryFn: () => operatorApi.getStats().then((r) => r.data),
  });
}

export function useOperatorTrips() {
  return useQuery({
    queryKey: ["operator", "trips"],
    queryFn: () => operatorApi.getMyTrips().then((r) => r.data),
  });
}

export function useOperatorVehicles() {
  return useQuery({
    queryKey: ["operator", "vehicles"],
    queryFn: () => operatorApi.getVehicles().then((r) => r.data),
  });
}

export function useOperatorDrivers() {
  return useQuery({
    queryKey: ["operator", "drivers"],
    queryFn: () => operatorApi.getDrivers().then((r) => r.data),
  });
}

export function useTripBookings(tripId: string | null) {
  return useQuery({
    queryKey: ["operator", "trip-bookings", tripId],
    queryFn: () => operatorApi.getTripBookings(tripId!).then((r) => r.data),
    enabled: !!tripId,
  });
}

export function useCreateTrip() {
  const qc = useQueryClient();
  const router = useRouter();
  return useMutation({
    mutationFn: (data: TripCreate) => operatorApi.createTrip(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["operator", "trips"] });
      toast.success("Jadwal baru berhasil dibuat!");
      router.push("/operator");
    },
    onError: () => toast.error("Gagal membuat jadwal."),
  });
}

export function useUpdateTripStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ tripId, status }: { tripId: string; status: string }) =>
      operatorApi.updateTripStatus(tripId, status).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["operator", "trips"] });
      toast.success("Status jadwal diperbarui.");
    },
  });
}
