import { format, parseISO } from "date-fns";
import { id } from "date-fns/locale";

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    minimumFractionDigits: 0,
  }).format(amount);
}

export function formatDeparture(isoString: string): string {
  return format(parseISO(isoString), "EEEE, d MMMM yyyy • HH:mm", { locale: id });
}

export function formatShortDate(isoString: string): string {
  return format(parseISO(isoString), "d MMM • HH:mm", { locale: id });
}

export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, "");
  if (!cleaned.startsWith("62")) return phone;
  return "0" + cleaned.slice(2);
}
