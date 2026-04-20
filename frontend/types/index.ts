export type UserRole = "passenger" | "operator" | "admin";

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: UserRole;
}

// ---- Routes ----
export interface Route {
  id: string;
  origin: string;
  destination: string;
  distance_km: number | null;
  estimated_duration_minutes: number | null;
  is_active: boolean;
}

// ---- Trips ----
export type TripStatus = "scheduled" | "boarding" | "departed" | "completed" | "cancelled";

export interface Trip {
  id: string;
  route_id: string;
  operator_id: string;
  driver_id: string | null;
  departure_at: string;
  total_seats: number;
  available_seats: number;
  price_per_seat: number;   // IDR integer
  status: TripStatus;
  booking_code: string;
  is_bookable: boolean;
  created_at: string;
}

// ---- Bookings ----
export type BookingStatus = "pending" | "confirmed" | "boarded" | "completed" | "cancelled";
export type PaymentMethod = "cash" | "qris" | "bank_transfer" | "ewallet";
export type PaymentStatus = "unpaid" | "paid" | "refunded";

export interface CreateBookingRequest {
  trip_id: string;
  passenger_name: string;
  passenger_phone: string;
  seat_numbers: number[];
  payment_method: PaymentMethod;
}

export interface Booking {
  id: string;
  trip_id: string;
  passenger_id: string;
  passenger_name: string;
  passenger_phone: string;
  seat_numbers: number[];
  seat_count: number;
  total_price: number;
  payment_method: PaymentMethod;
  payment_status: PaymentStatus;
  status: BookingStatus;
  booking_ref: string;
  payment_gateway_ref: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  created_at: string;
}

// ---- Operators / Drivers ----
export interface OperatorProfile {
  id: string;
  user_id: string;
  business_name: string;
  phone: string;
  is_approved: boolean;
  approved_at: string | null;
  created_at: string;
}

export interface Driver {
  id: string;
  operator_id: string;
  name: string;
  phone: string;
  licence_number: string | null;
  linked_user_id: string | null;
  is_active: boolean;
  created_at: string;
}