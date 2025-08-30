import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Dictionary App - Your Intelligent Dictionary with Extensions",
  description: "A powerful, extensible dictionary application with smart search, offline functionality, and a thriving extension marketplace.",
  keywords: ["dictionary", "definitions", "vocabulary", "language learning", "extensions", "offline dictionary"],
  authors: [{ name: "Dictionary App Team" }],
  openGraph: {
    title: "Dictionary App",
    description: "Your intelligent dictionary with extensions",
    url: "https://dictionaryapp.com",
    siteName: "Dictionary App",
    images: [
      {
        url: "/images/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Dictionary App",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Dictionary App",
    description: "Your intelligent dictionary with extensions",
    images: ["/images/og-image.jpg"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
