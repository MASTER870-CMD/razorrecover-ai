import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RazorRecover AI — Find Revenue at Risk. Recover it Safely.",
  description:
    "Autonomous revenue recovery infrastructure for Razorpay merchants. Built for Razorpay AI Buildathon 2026 Track 03.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#F8FAFC] text-slate-900 min-h-screen antialiased selection:bg-brand-100 selection:text-brand-900">
        {children}
      </body>
    </html>
  );
}
