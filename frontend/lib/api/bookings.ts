import { Booking, CreateBookingRequest } from "@/types";
import { apiClient } from "./client";

export const bookingsApi = {
  create: (data: CreateBookingRequest): Promise<{ data: Booking }> =>
    apiClient.post("/bookings", data),

  listMine: (status?: string): Promise<{ data: Booking[] }> =>
    apiClient.get("/bookings", { params: status ? { status } : undefined }),

  get: (booking_id: string): Promise<{ data: Booking }> =>
    apiClient.get(`/bookings/${booking_id}`),

  cancel: (booking_id: string, reason?: string): Promise<{ data: Booking }> =>
    apiClient.post(`/bookings/${booking_id}/cancel`, { reason }),

  // Operator — trip manifest
  getManifest: (trip_id: string): Promise<{ data: Booking[] }> =>
    apiClient.get(`/trips/${trip_id}/manifest`),
};