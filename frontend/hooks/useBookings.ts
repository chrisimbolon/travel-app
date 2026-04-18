import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { bookingsApi } from "@/lib/api/bookings";
import { BookingCreate } from "@/types";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

export function useMyBookings() {
  return useQuery({
    queryKey: ["bookings", "my"],
    queryFn: () => bookingsApi.myBookings().then((r) => r.data),
  });
}

export function useCreateBooking() {
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: (data: BookingCreate) => bookingsApi.create(data).then((r) => r.data),
    onSuccess: (booking) => {
      qc.invalidateQueries({ queryKey: ["bookings"] });
      toast.success(`Booking ${booking.booking_code} dikonfirmasi!`);
      router.push(`/bookings/${booking.id}`);
    },
    onError: () => {
      toast.error("Kursi tidak tersedia. Silakan pilih kursi lain.");
    },
  });
}

export function useCancelBooking() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => bookingsApi.cancel(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bookings"] });
      toast.success("Booking dibatalkan.");
    },
  });
}
