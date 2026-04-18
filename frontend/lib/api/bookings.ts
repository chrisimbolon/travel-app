import { apiClient } from "./client";
import { Booking, BookingCreate } from "@/types";

export const bookingsApi = {
  create: (data: BookingCreate): Promise<{ data: Booking }> =>
    apiClient.post("/bookings", data),

  myBookings: (): Promise<{ data: Booking[] }> =>
    apiClient.get("/bookings/my"),

  cancel: (bookingId: string): Promise<{ data: { message: string; booking_code: string } }> =>
    apiClient.delete(`/bookings/${bookingId}`),
};
