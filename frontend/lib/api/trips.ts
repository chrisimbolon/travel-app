import { apiClient } from "./client";
import { Trip, SeatsResponse } from "@/types";

export const tripsApi = {
  search: (params: {
    origin: string;
    destination: string;
    travel_date: string;
    seat_count: number;
  }): Promise<{ data: Trip[] }> =>
    apiClient.get("/trips/search", { params }),

  getSeats: (tripId: string): Promise<{ data: SeatsResponse }> =>
    apiClient.get(`/trips/${tripId}/seats`),
};
