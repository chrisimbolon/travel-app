import { AuthTokens } from "@/types";
import { apiClient } from "./client";

export const authApi = {
  // Passenger — OTP flow
  requestOtp: (phone: string) =>
    apiClient.post("/auth/request-otp", { phone }),

  verifyOtp: (phone: string, otp_code: string): Promise<{ data: AuthTokens }> =>
    apiClient.post("/auth/verify-otp", { phone, otp_code }),

  // Operator / Admin — password flow
  login: (email: string, password: string): Promise<{ data: AuthTokens }> =>
    apiClient.post("/auth/login", { email, password }),

  // Shared
  refresh: (refresh_token: string): Promise<{ data: AuthTokens }> =>
    apiClient.post("/auth/refresh", { refresh_token }),
};