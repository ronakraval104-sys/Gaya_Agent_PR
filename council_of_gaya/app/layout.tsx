import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "COUNCIL OF GAYA // v1.0",
  description: "Gaya Operator Console & Knowledge Deck for R0n (Sacred Gold & Obsidian)."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-persona="gaya">
      <body>{children}</body>
    </html>
  );
}
