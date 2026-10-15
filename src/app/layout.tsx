import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from 'next/link';
import "./tailwind.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CAS Research | Technology Equity Research",
  description: "Technology Equity Research for Long-Term Investors",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-white">
        <header className="bg-[#030A1D] border-b border-gray-800 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center cursor-pointer">
              <span className="font-semibold text-2xl tracking-tight text-white hover:text-gray-300 transition-colors">CAS Research</span>
            </Link>
            <nav className="hidden md:flex space-x-8">
              <Link href="/" className="text-white font-medium text-sm border-b-2 border-blue-600 py-5">Home</Link>
              <Link href="/blog" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">Research</Link>
              <Link href="/datacenters" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">Insights</Link>
              <Link href="/about" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">About</Link>
              <Link href="/contact" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">Contact</Link>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
