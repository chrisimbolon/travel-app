import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "react-hot-toast";
import { Providers } from "./providers";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Transitku — Pesan Tiket Minibus Jambi",
  description: "Pesan tiket minibus antar kota di Jambi dengan mudah dan terpercaya.",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, statusBarStyle: "default", title: "Transitku" },
};

export const viewport: Viewport = {
  themeColor: "#1d9e75",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" className={inter.variable}>
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
      </head>
      <body>
        <Providers>
          {children}
          <Toaster position="top-center" toastOptions={{ duration: 3000 }} />
        </Providers>
      </body>
    </html>
  );
}
