import { bookingsApi } from "@/lib/api/bookings";
import { Booking, CreateBookingRequest } from "@/types";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export function useMyBookings(status?: string) {
  return useQuery<Booking[]>({
    queryKey: ["bookings", status],
    queryFn: async () => {
      const { data } = await bookingsApi.listMine(status);
      return data;
    },
  });
}

export function useCreateBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateBookingRequest) => bookingsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["trips"] });
    },
  });
}

export function useCancelBooking() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ booking_id, reason }: { booking_id: string; reason?: string }) =>
      bookingsApi.cancel(booking_id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["trips"] });
    },
  });
}