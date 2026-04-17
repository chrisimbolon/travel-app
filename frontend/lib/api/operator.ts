import { apiClient } from "./client";
import { Trip, TripCreate, Booking, Vehicle, Driver, OperatorStats } from "@/types";

export const operatorApi = {
  // Dashboard stats
  getStats: (): Promise<{ data: OperatorStats }> =>
    apiClient.get("/operators/stats"),

  // Trips
  getMyTrips: (): Promise<{ data: Trip[] }> =>
    apiClient.get("/operators/trips"),

  createTrip: (data: TripCreate): Promise<{ data: Trip }> =>
    apiClient.post("/operators/trips", data),

  updateTripStatus: (tripId: string, status: string): Promise<{ data: Trip }> =>
    apiClient.patch(`/operators/trips/${tripId}/status`, { status }),

  cancelTrip: (tripId: string): Promise<{ data: { message: string } }> =>
    apiClient.delete(`/operators/trips/${tripId}`),

  // Bookings
  getTripBookings: (tripId: string): Promise<{ data: Booking[] }> =>
    apiClient.get(`/operators/trips/${tripId}/bookings`),

  // Vehicles
  getVehicles: (): Promise<{ data: Vehicle[] }> =>
    apiClient.get("/operators/vehicles"),

  // Drivers
  getDrivers: (): Promise<{ data: Driver[] }> =>
    apiClient.get("/operators/drivers"),
};
