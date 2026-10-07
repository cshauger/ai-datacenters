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
  title: "CAS Research | Jetha Global",
  description: "Proprietary AI Infrastructure Intelligence",
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
      <body className="min-h-full flex flex-col bg-[#F8F9FA]">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-2 cursor-pointer group">
              <div className="w-8 h-8 bg-black rounded-sm flex items-center justify-center group-hover:bg-gray-800 transition-colors">
                <span className="text-white font-bold text-sm">CR</span>
              </div>
              <span className="font-bold text-xl tracking-tight text-gray-900 group-hover:text-gray-700 transition-colors">CAS Research</span>
            </Link>
            <nav className="hidden md:flex space-x-8">
              <Link href="/" className="text-gray-500 hover:text-gray-900 font-medium text-sm py-5 transition-colors">Home</Link>
              <Link href="/datacenters" className="text-gray-500 hover:text-gray-900 font-medium text-sm py-5 transition-colors">Infrastructure</Link>
              <Link href="/gpu" className="text-gray-500 hover:text-gray-900 font-medium text-sm py-5 transition-colors">GPU Tracker</Link>
              <Link href="/npm" className="text-gray-500 hover:text-gray-900 font-medium text-sm py-5 transition-colors">Alternative Data</Link>
            </nav>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
