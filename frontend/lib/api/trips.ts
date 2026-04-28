import { apiClient } from "./client";
import { Route, Trip } from "@/types";

export const tripsApi = {
  // Get all active routes — used to populate search dropdowns
  listRoutes: (): Promise<{ data: Route[] }> =>
    apiClient.get("/routes"),

  // Find route by origin + destination — used in search
  findRoute: (origin: string, destination: string): Promise<{ data: Route[] }> =>
    apiClient.get("/routes", { params: { origin, destination } }),

  // List trips by route_id + optional date filter
  listByRoute: (
    route_id: string,
    params?: { from_dt?: string; limit?: number }
  ): Promise<{ data: Trip[] }> =>
    apiClient.get("/trips", { params: { route_id, ...params } }),

  // List trips owned by the logged-in operator
  listMyTrips: (
    operator_id: string,
    status?: string
  ): Promise<{ data: Trip[] }> =>
    apiClient.get("/trips", { params: { operator_id, status } }),

  // Get single trip
  getTrip: (trip_id: string): Promise<{ data: Trip }> =>
    apiClient.get(`/trips/${trip_id}`),
};