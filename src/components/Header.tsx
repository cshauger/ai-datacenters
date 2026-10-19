'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, Plus, ArrowUpRight } from 'lucide-react';

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <header className="bg-[#030A1D] border-b border-gray-800 sticky top-0 z-50">
        <div className="w-full px-4 md:px-12 lg:px-16 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setMenuOpen(true)}
              className="text-white hover:text-gray-300 p-1 -ml-1 focus:outline-none"
              aria-label="Open Menu"
            >
              <Menu className="w-6 h-6" />
            </button>
            <Link href="/" className="flex items-center cursor-pointer">
              <span className="font-semibold text-2xl tracking-tight text-white hover:text-gray-300 transition-colors">CAS Research</span>
            </Link>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            <Link href="/" className="text-white font-medium text-sm border-b-2 border-blue-600 py-5">Home</Link>
            <Link href="/blog" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">Research</Link>
            <Link href="/datacenters" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">Insights</Link>
            <Link href="/about" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">About</Link>
            <Link href="/contact" className="text-gray-300 hover:text-white font-medium text-sm py-5 transition-colors">Contact</Link>
          </nav>
        </div>
      </header>

      {/* Full Screen Overlay Menu (Gartner Style) */}
      {menuOpen && (
        <div className="fixed inset-0 z-[60] bg-[#030A1D] md:bg-black/50 md:backdrop-blur-sm flex justify-start">
          <div className="bg-white w-full md:w-[400px] h-full flex flex-col shadow-2xl overflow-y-auto animate-in slide-in-from-left duration-300">
            
            {/* Menu Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <button 
                onClick={() => setMenuOpen(false)}
                className="text-gray-600 hover:text-gray-900 focus:outline-none p-1 -ml-1"
              >
                <X className="w-6 h-6" />
              </button>
              <span className="font-semibold text-xl tracking-tight text-[#030A1D]">CAS Research</span>
              <div className="flex items-center text-blue-600 font-medium text-sm hover:underline cursor-pointer">
                <span>Client Login</span>
                <ArrowUpRight className="w-4 h-4 ml-1" />
              </div>
            </div>

            {/* Menu Links */}
            <div className="flex-1 py-4">
              <ul className="flex flex-col text-[#030A1D]">
                <li className="border-b border-gray-100">
                  <Link href="/blog" onClick={() => setMenuOpen(false)} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 text-[15px]">
                    Insights
                    <Plus className="w-4 h-4 text-gray-400" />
                  </Link>
                </li>
                <li className="border-b border-gray-100">
                  <Link href="/datacenters" onClick={() => setMenuOpen(false)} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 text-[15px]">
                    Internal Trackers
                    <Plus className="w-4 h-4 text-gray-400" />
                  </Link>
                </li>
                <li className="border-b border-gray-100">
                  <Link href="/about" onClick={() => setMenuOpen(false)} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 text-[15px]">
                    Coverage Basket
                    <Plus className="w-4 h-4 text-gray-400" />
                  </Link>
                </li>
                <li className="border-b border-gray-100">
                  <Link href="/contact" onClick={() => setMenuOpen(false)} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 text-[15px]">
                    Methodology
                    <Plus className="w-4 h-4 text-gray-400" />
                  </Link>
                </li>
                
                <li className="mt-4">
                  <Link href="/about" onClick={() => setMenuOpen(false)} className="flex items-center px-6 py-3 hover:bg-gray-50 text-[15px]">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/contact" onClick={() => setMenuOpen(false)} className="flex items-center px-6 py-3 hover:bg-gray-50 text-[15px]">
                    Contact
                  </Link>
                </li>
              </ul>
            </div>

            {/* Menu Footer */}
            <div className="p-6 border-t border-gray-100 bg-gray-50 mt-auto">
              <Link href="/contact" onClick={() => setMenuOpen(false)} className="flex items-center text-[#030A1D] font-semibold text-lg hover:underline mb-2">
                Get Started <ArrowUpRight className="w-5 h-5 ml-1 text-blue-600" />
              </Link>
              <p className="text-gray-500 text-sm">or email info@casres.com</p>
            </div>
            
          </div>
        </div>
      )}
    </>
  );
}
