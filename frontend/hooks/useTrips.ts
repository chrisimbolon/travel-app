import { tripsApi } from "@/lib/api/trips";
import { Route, Trip } from "@/types";
import { useQuery } from "@tanstack/react-query";

interface SearchParams {
  origin: string;
  destination: string;
  travel_date: string;
  seat_count: number;
}

// Fetch all routes — used to populate dropdowns
export function useRoutes() {
  return useQuery<Route[]>({
    queryKey: ["routes"],
    queryFn: async () => {
      const { data } = await tripsApi.listRoutes();
      return data;
    },
    staleTime: 1000 * 60 * 60, // routes don't change often — cache for 1 hour
  });
}

// Search trips — resolves route_id from origin+destination first
export function useTrips(params: SearchParams | null) {
  const { data: routes } = useRoutes();

  return useQuery<Trip[]>({
    queryKey: ["trips", params],
    enabled: !!params && !!routes,
    queryFn: async () => {
      if (!params || !routes) return [];

      // Find matching route
      const route = routes.find(
        (r) =>
          r.origin.toLowerCase().includes(params.origin.toLowerCase()) ||
          params.origin.toLowerCase().includes(r.origin.toLowerCase())
      );

      if (!route) return [];

      // Fetch trips on that route from the travel date onwards
      const from_dt = new Date(params.travel_date).toISOString();
      const { data } = await tripsApi.listByRoute(route.id, { from_dt, limit: 20 });

      // Filter by seat availability
      return data.filter((t) => t.available_seats >= params.seat_count);
    },
  });
}

// Operator's own trips
export function useMyTrips(operator_id: string | undefined, status?: string) {
  return useQuery<Trip[]>({
    queryKey: ["my-trips", operator_id, status],
    enabled: !!operator_id,
    queryFn: async () => {
      if (!operator_id) return [];
      const { data } = await tripsApi.listMyTrips(operator_id, status);
      return data;
    },
  });
}