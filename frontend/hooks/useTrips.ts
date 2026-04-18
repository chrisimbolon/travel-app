import { useQuery } from "@tanstack/react-query";
import { tripsApi } from "@/lib/api/trips";

interface SearchParams {
  origin: string;
  destination: string;
  travel_date: string;
  seat_count: number;
}

export function useTrips(params: SearchParams | null) {
  return useQuery({
    queryKey: ["trips", params],
    queryFn: () => tripsApi.search(params!).then((r) => r.data),
    enabled: !!params,
    staleTime: 30_000,
  });
}

export function useTripSeats(tripId: string | null) {
  return useQuery({
    queryKey: ["seats", tripId],
    queryFn: () => tripsApi.getSeats(tripId!).then((r) => r.data),
    enabled: !!tripId,
    refetchInterval: 15_000, // poll every 15s to keep seat state fresh
  });
}
