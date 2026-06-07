/**
 * Root HTML layout — applies global fonts and sets the document shell.
 *
 * All pages share this layout. Two Google Fonts are loaded via next/font:
 *   - Hanken Grotesk → `--font-sans` (body text, headings)
 *   - JetBrains Mono → `--font-geist-mono` (mono chip labels, tool events)
 *
 * Both are CSS variables so Tailwind's `font-sans` / `font-mono` utilities
 * resolve to these values via `tailwind.config.ts`.
 */

import type { Metadata } from "next";
import { Hanken_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const hankenGrotesk = Hanken_Grotesk({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "BodyOps",
  description: "Your AI fat-loss OS",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${hankenGrotesk.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
