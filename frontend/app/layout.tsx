import type { Metadata } from "next";
import { PageTransitions } from "@/components/PageTransitions";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
  title: "LegacyLens — Modernization Intelligence",
  description: "Understand legacy code. See the risks. Modernize with confidence.",
  openGraph: {
    title: "LegacyLens — Modernization Intelligence",
    description:
      "Evidence-backed repository intelligence: transparent health scores, specialist findings, and phased renovation roadmaps for public GitHub repositories.",
    siteName: "LegacyLens",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="noise-overlay" aria-hidden="true" />
        <PageTransitions>{children}</PageTransitions>
      </body>
    </html>
  );
}
