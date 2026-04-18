import { useAuthStore } from "@/store/auth.store";
import { authApi } from "@/lib/api/auth";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

export function useAuth() {
  const { setTokens, clearAuth, role, isAuthenticated } = useAuthStore();
  const router = useRouter();

  const requestOtp = async (phone: string) => {
    await authApi.requestOtp(phone);
  };

  const verifyOtp = async (phone: string, otp: string) => {
    const { data } = await authApi.verifyOtp(phone, otp);
    setTokens(data.access_token, data.refresh_token, data.role);

    // Route by role
    const routes: Record<string, string> = {
      passenger: "/search",
      operator:  "/operator",
      driver:    "/driver",
      admin:     "/admin",
    };
    router.push(routes[data.role] ?? "/search");
    toast.success("Selamat datang!");
  };

  const logout = () => {
    clearAuth();
    router.push("/auth");
  };

  return { requestOtp, verifyOtp, logout, role, isAuthenticated };
}
