"use client";
import { useAuth } from "@/hooks/useAuth";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import toast from "react-hot-toast";
import { z } from "zod";

const phoneSchema = z.object({
  phone: z.string().regex(/^08\d{8,11}$/, "Masukkan nomor HP yang valid (contoh: 08123456789)"),
});
const otpSchema = z.object({
  otp: z.string().length(6, "Kode OTP harus 6 digit"),
});

type PhoneForm = z.infer<typeof phoneSchema>;
type OtpForm   = z.infer<typeof otpSchema>;

export default function AuthPage() {
  const [step, setStep]   = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const { requestOtp, verifyOtp } = useAuth();

  const phoneForm = useForm<PhoneForm>({ resolver: zodResolver(phoneSchema) });
  const otpForm   = useForm<OtpForm>({ resolver: zodResolver(otpSchema) });

  const onPhone = phoneForm.handleSubmit(async ({ phone: p }) => {
    try {
      const normalised = "62" + p.slice(1);
      await requestOtp(normalised);
      setPhone(normalised);
      setStep("otp");
      toast.success("Kode OTP dikirim via WhatsApp");
    } catch {
      toast.error("Gagal mengirim OTP. Coba lagi.");
    }
  });

  const onOtp = otpForm.handleSubmit(async ({ otp }) => {
    try {
      await verifyOtp(phone, otp);
    } catch {
      toast.error("Kode OTP salah atau sudah kadaluarsa.");
    }
  });

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-5 bg-white">
      <div className="w-full max-w-sm">
        <div className="mb-10 text-center">
          <div className="w-16 h-16 bg-brand-500 rounded-3xl mx-auto mb-4 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">T</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Transitku</h1>
          <p className="text-gray-500 text-sm mt-1">Pesan tiket minibus Jambi</p>
        </div>

        {step === "phone" ? (
          <form onSubmit={onPhone} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Nomor HP
              </label>
              <input
                {...phoneForm.register("phone")}
                type="tel"
                placeholder="08123456789"
                className="input"
                autoFocus
              />
              {phoneForm.formState.errors.phone && (
                <p className="text-red-500 text-xs mt-1">
                  {phoneForm.formState.errors.phone.message}
                </p>
              )}
            </div>
            <button type="submit" className="btn-primary" disabled={phoneForm.formState.isSubmitting}>
              {phoneForm.formState.isSubmitting ? "Mengirim..." : "Kirim Kode OTP"}
            </button>
            <p className="text-center text-xs text-gray-400">Kode dikirim via WhatsApp</p>
          </form>
        ) : (
          <form onSubmit={onOtp} className="space-y-4">
            <p className="text-sm text-gray-500 text-center">
              Masukkan kode 6 digit yang dikirim ke{" "}
              <span className="font-medium text-gray-800">+{phone}</span>
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Kode OTP
              </label>
              <input
                {...otpForm.register("otp")}
                type="number"
                placeholder="123456"
                className="input text-center text-2xl tracking-widest"
                autoFocus
                maxLength={6}
              />
              {otpForm.formState.errors.otp && (
                <p className="text-red-500 text-xs mt-1">
                  {otpForm.formState.errors.otp.message}
                </p>
              )}
            </div>
            <button type="submit" className="btn-primary" disabled={otpForm.formState.isSubmitting}>
              {otpForm.formState.isSubmitting ? "Memverifikasi..." : "Masuk"}
            </button>
            <button type="button" className="w-full text-sm text-brand-600 text-center"
              onClick={() => setStep("phone")}>
              Ganti nomor HP
            </button>
          </form>
        )}
      </div>
    </main>
  );
}
