import { apiClient } from "./client";
import { AuthTokens } from "@/types";

export const authApi = {
  requestOtp: (phone: string) =>
    apiClient.post("/auth/request-otp", { phone }),

  verifyOtp: (phone: string, otp_code: string): Promise<{ data: AuthTokens }> =>
    apiClient.post("/auth/verify-otp", { phone, otp_code }),
};
