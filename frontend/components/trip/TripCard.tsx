"use client";
import { useRouter } from "next/navigation";
import { Trip } from "@/types";
import { formatCurrency, formatShortDate } from "@/lib/utils/format";
import { cn } from "@/lib/utils/cn";

interface Props { trip: Trip }

export default function TripCard({ trip }: Props) {
  const router = useRouter();
  const isAlmostFull = trip.available_seats <= 3;

  return (
    <div
      className="card cursor-pointer active:scale-[0.98] transition-transform"
      onClick={() => router.push(`/trips/${trip.id}`)}
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <p className="font-semibold text-gray-900 text-base">
            {trip.origin} → {trip.destination}
          </p>
          <p className="text-gray-400 text-sm mt-0.5">{trip.operator_name}</p>
        </div>
        <p className="text-brand-600 font-bold text-base">{formatCurrency(trip.price)}</p>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-gray-600 text-sm">{formatShortDate(trip.departure_at)}</p>
        <span className={cn(
          "text-xs font-medium px-2.5 py-1 rounded-full",
          isAlmostFull
            ? "bg-red-50 text-red-600"
            : "bg-green-50 text-green-700"
        )}>
          {trip.available_seats} kursi tersisa
        </span>
      </div>
    </div>
  );
}
