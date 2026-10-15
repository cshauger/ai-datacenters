import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from 'next/link';
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CAS Research",
  description: "Technology Equity Research",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
      <body className="min-h-screen flex flex-col bg-white text-black font-sans">
        <header className="border-b border-gray-100">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <Link href="/" className="font-bold text-2xl tracking-tight text-gray-900">
                CAS Research
              </Link>
              <nav className="hidden md:flex space-x-6 pl-6 border-l border-gray-200">
                <Link href="/" className="text-gray-600 hover:text-black font-medium text-sm">Home</Link>
                <Link href="/datacenters" className="text-gray-600 hover:text-black font-medium text-sm">DC Tracker</Link>
                <Link href="/gpu" className="text-gray-600 hover:text-black font-medium text-sm">GPU Pricing</Link>
                <Link href="/npm" className="text-gray-600 hover:text-black font-medium text-sm">NPM Data</Link>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="hidden sm:block text-sm font-medium text-gray-600 hover:text-black">Sign in</Link>
              <button className="bg-[#FF6719] text-white px-4 py-2 rounded-full text-sm font-bold hover:bg-[#e55c16] transition-colors">Subscribe</button>
            </div>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
