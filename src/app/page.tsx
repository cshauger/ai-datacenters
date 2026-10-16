import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-white font-sans text-gray-900">
      
      {/* HERO SECTION */}
      <div className="bg-[#0a1628] text-white relative overflow-hidden">
        {/* Server rack background image */}
        <div 
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1558494949-ef010cbdcc31?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-r from-[#0a1628] via-[#0a1628]/90 to-[#0a1628]/70"></div>
        
        {/* Circular chip graphic */}
        <div className="absolute right-[5%] top-1/2 -translate-y-1/2 w-64 h-64 lg:w-80 lg:h-80 hidden md:block">
          <div className="relative w-full h-full">
            <div className="absolute inset-0 rounded-full border-2 border-blue-400/30"></div>
            <div className="absolute inset-4 rounded-full border border-blue-400/50 bg-[#0a1628]/50 flex items-center justify-center">
              <svg className="w-32 h-32 lg:w-40 lg:h-40 text-blue-400/70" viewBox="0 0 100 100" fill="none" stroke="currentColor">
                <rect x="25" y="25" width="50" height="50" strokeWidth="1.5" rx="4"/>
                <rect x="35" y="35" width="30" height="30" strokeWidth="1" rx="2"/>
                <line x1="35" y1="25" x2="35" y2="15" strokeWidth="1.5"/>
                <line x1="50" y1="25" x2="50" y2="15" strokeWidth="1.5"/>
                <line x1="65" y1="25" x2="65" y2="15" strokeWidth="1.5"/>
                <line x1="35" y1="75" x2="35" y2="85" strokeWidth="1.5"/>
                <line x1="50" y1="75" x2="50" y2="85" strokeWidth="1.5"/>
                <line x1="65" y1="75" x2="65" y2="85" strokeWidth="1.5"/>
                <line x1="25" y1="35" x2="15" y2="35" strokeWidth="1.5"/>
                <line x1="25" y1="50" x2="15" y2="50" strokeWidth="1.5"/>
                <line x1="25" y1="65" x2="15" y2="65" strokeWidth="1.5"/>
                <line x1="75" y1="35" x2="85" y2="35" strokeWidth="1.5"/>
                <line x1="75" y1="50" x2="85" y2="50" strokeWidth="1.5"/>
                <line x1="75" y1="65" x2="85" y2="65" strokeWidth="1.5"/>
                <circle cx="50" cy="50" r="3" fill="currentColor"/>
              </svg>
            </div>
            <svg className="absolute -right-8 top-0 w-24 h-full text-blue-400/20" viewBox="0 0 50 200">
              <path d="M 0 20 Q 40 100 0 180" fill="none" stroke="currentColor" strokeWidth="1"/>
            </svg>
          </div>
        </div>
        
        {/* Reduced left padding - was px-4 sm:px-6 lg:px-8, now px-1 sm:px-2 lg:px-4 */}
        <div className="max-w-7xl mx-auto px-1 sm:px-2 lg:px-4 py-16 lg:py-24 relative z-10">
          <div className="max-w-2xl pl-2 sm:pl-3 lg:pl-4">
            <h1 className="text-5xl lg:text-7xl font-bold tracking-tight mb-2 leading-[1.1]">
              CAS<br />Research
            </h1>
            <div className="w-28 h-1 bg-blue-500 mb-6 mt-4"></div>
            <p className="text-lg lg:text-xl text-gray-300 font-normal">
              <span className="font-semibold text-white">Technology Equity Research</span> for Long-Term Investors
            </p>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 py-12" id="research">
        
        {/* SECTION: OUR RESEARCH COVERAGE */}
        <div className="flex items-center justify-center mb-12">
          <div className="h-px bg-gray-200 flex-1 max-w-[200px]"></div>
          <h2 className="text-xs font-bold tracking-[0.25em] text-gray-500 uppercase px-6">Our Research Coverage</h2>
          <div className="h-px bg-gray-200 flex-1 max-w-[200px]"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {/* Card 1 - AI Infrastructure */}
          <div className="border border-gray-200 p-6 rounded-lg bg-white hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-bold text-gray-900 mb-3">AI Infrastructure</h3>
            <p className="text-gray-600 text-sm leading-relaxed mb-6">
              Deep research on the infrastructure buildout powering AI, from data centers and networking to power and cooling.
            </p>
            <div className="flex items-center text-xs font-semibold text-gray-700 pt-4 border-t border-gray-100">
              <div className="w-7 h-7 rounded bg-gray-100 text-gray-600 flex items-center justify-center mr-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                </svg>
              </div>
              Infrastructure & Enablers
            </div>
          </div>

          {/* Card 2 - Semiconductors & Optics */}
          <div className="border border-gray-200 p-6 rounded-lg bg-white hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Semiconductors & Optics</h3>
            <p className="text-gray-600 text-sm leading-relaxed mb-6">
              Analysis of semiconductor companies and optical technologies enabling compute, connectivity, and sensing.
            </p>
            <div className="flex items-center text-xs font-semibold text-gray-700 pt-4 border-t border-gray-100">
              <div className="w-7 h-7 rounded bg-gray-100 text-gray-600 flex items-center justify-center mr-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/>
                </svg>
              </div>
              Chips, Components & Photonics
            </div>
          </div>

          {/* Card 3 - Software & Cloud */}
          <div className="border border-gray-200 p-6 rounded-lg bg-white hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Software & Cloud</h3>
            <p className="text-gray-600 text-sm leading-relaxed mb-6">
              Research on software, cloud platforms, and enterprise solutions driving scalability, efficiency, and innovation.
            </p>
            <div className="flex items-center text-xs font-semibold text-gray-700 pt-4 border-t border-gray-100">
              <div className="w-7 h-7 rounded bg-gray-100 text-gray-600 flex items-center justify-center mr-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/>
                </svg>
              </div>
              Software, SaaS & Cloud
            </div>
          </div>
        </div>

        {/* INTERNAL DASHBOARDS */}
        <div className="mt-12 pt-10 border-t border-gray-100">
          <div className="flex items-center justify-center mb-8">
            <h2 className="text-xs font-bold tracking-[0.2em] text-gray-400 uppercase">Internal Tracking Dashboards</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/datacenters" className="block group">
              <div className="p-5 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors bg-gray-50">
                <h4 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600">Datacenter Capacity →</h4>
                <p className="text-sm text-gray-500">Live tracking of 76+ physical facilities and MW pipeline.</p>
              </div>
            </Link>

            <Link href="/gpu" className="block group">
              <div className="p-5 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors bg-gray-50">
                <h4 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600">GPU Spot Pricing →</h4>
                <p className="text-sm text-gray-500">Automated daily scraping of H100, H200, and B200 spot lease rates.</p>
              </div>
            </Link>

            <Link href="/npm" className="block group">
              <div className="p-5 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors bg-gray-50">
                <h4 className="font-semibold text-gray-900 mb-1 group-hover:text-blue-600">NPM Alternative Data →</h4>
                <p className="text-sm text-gray-500">Real-time developer adoption metrics tracking SDK downloads.</p>
              </div>
            </Link>
          </div>
        </div>

      </main>
    </div>
  );
}
