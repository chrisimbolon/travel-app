"use client";
import { cn } from "@/lib/utils/cn";
import Link from "next/link";

type Tab = "search" | "bookings" | "profile";

interface Props { active: Tab }

const tabs: { id: Tab; label: string; href: string; icon: string }[] = [
  { id: "search",   label: "Cari",   href: "/search",   icon: "🔍" },
  { id: "bookings", label: "Tiket",  href: "/bookings", icon: "🎫" },
  { id: "profile",  label: "Profil", href: "/profile",  icon: "👤" },
];

export default function BottomNav({ active }: Props) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 flex safe-area-pb">
      {tabs.map((tab) => (
        <Link
          key={tab.id}
          href={tab.href}
          className={cn(
            "flex-1 flex flex-col items-center py-3 text-xs gap-1",
            active === tab.id ? "text-brand-600 font-medium" : "text-gray-400"
          )}
        >
          <span style={{ fontSize: 20 }}>{tab.icon}</span>
          {tab.label}
        </Link>
      ))}
    </nav>
  );
}
