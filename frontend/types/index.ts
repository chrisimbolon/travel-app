export type UserRole = "passenger" | "operator" | "driver" | "admin";

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: UserRole;
}

export type TripStatus = "scheduled"|"boarding"|"departed"|"completed"|"cancelled";

export interface Trip {
  id: string; route_id: string; origin: string; destination: string;
  departure_at: string; available_seats: number; total_seats: number;
  price: number; operator_name: string; vehicle_model: string; status: TripStatus;
}

export interface TripCreate {
  route_id: string; vehicle_id: string; driver_id?: string;
  departure_at: string; total_seats: number; price: number;
}

export interface Seat { seat_number: number; status: "available"|"locked"|"booked"; }
export interface SeatsResponse { trip_id: string; total_seats: number; seats: Seat[]; }

export type BookingStatus = "pending"|"confirmed"|"cancelled"|"completed";
export type PaymentMethod = "cash"|"qris";

export interface SeatDetail { seat_number: number; passenger_name: string; }
export interface BookingCreate { trip_id: string; seats: SeatDetail[]; payment_method: PaymentMethod; }
export interface Booking {
  id: string; booking_code: string; trip_id: string; seat_count: number;
  total_amount: number; payment_method: PaymentMethod; status: BookingStatus;
}

export type OperatorStatus = "pending"|"active"|"suspended";
export interface Operator {
  id: string; user_id: string; company_name: string;
  license_number: string; status: OperatorStatus; created_at: string;
}

export interface Vehicle {
  id: string; operator_id: string; plate_number: string;
  model: string; capacity: number; status: "active"|"maintenance"|"inactive";
}

export interface Driver {
  id: string; user_id: string; operator_id: string;
  license_number: string; status: "active"|"inactive"; name?: string; phone?: string;
}

export interface Route {
  id: string; origin: string; destination: string;
  distance_km: number; duration_min: number; is_active: boolean;
}

export interface OperatorStats {
  total_trips: number; active_trips: number; total_bookings: number;
  confirmed_bookings: number; total_revenue: number; this_month_revenue: number;
}

export interface AdminStats {
  total_operators: number; active_operators: number; total_passengers: number;
  total_trips: number; total_bookings: number; total_revenue: number;
}
