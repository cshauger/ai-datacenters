import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-white font-sans text-gray-900 flex-1 w-full">
      
      {/* HERO SECTION */}
      <div className="bg-[#040A18] text-white relative overflow-hidden">
        {/* Faint blue gradient to mimic the background lighting */}
        <div className="absolute inset-0 opacity-40 bg-[radial-gradient(ellipse_at_right,_var(--tw-gradient-stops))] from-blue-900 via-[#040A18] to-[#040A18]"></div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32 relative z-10">
          <div className="max-w-3xl">
            <h1 className="text-6xl lg:text-[5.5rem] font-bold tracking-tight mb-2 leading-[1.05]">
              CAS<br />Research
            </h1>
            <div className="w-24 h-1 bg-blue-600 mb-8 mt-4"></div>
            <p className="text-xl lg:text-2xl text-gray-300 font-medium tracking-wide">
              Technology Equity Research for Long-Term Investors
            </p>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        
        {/* SECTION: OUR RESEARCH COVERAGE */}
        <div className="flex items-center justify-center mb-12 mt-4">
          <div className="h-px bg-gray-200 flex-1 max-w-[200px]"></div>
          <h2 className="text-sm font-bold tracking-[0.2em] text-gray-800 uppercase px-6">Our Research Coverage</h2>
          <div className="h-px bg-gray-200 flex-1 max-w-[200px]"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          {/* Card 1 */}
          <div className="border border-gray-200 p-8 rounded-xl bg-white hover:shadow-lg transition-shadow">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">AI Infrastructure</h3>
            <p className="text-gray-600 leading-relaxed mb-10 min-h-[100px]">
              Deep research on the infrastructure buildout powering AI, from data centers and networking to power and cooling.
            </p>
            <div className="flex items-center text-sm font-semibold text-gray-800">
              <div className="w-10 h-10 rounded bg-blue-50 text-blue-600 flex items-center justify-center mr-3 border border-blue-100">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
              </div>
              Infrastructure & Enablers
            </div>
          </div>

          {/* Card 2 */}
          <div className="border border-gray-200 p-8 rounded-xl bg-white hover:shadow-lg transition-shadow">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Semiconductors & Optics</h3>
            <p className="text-gray-600 leading-relaxed mb-10 min-h-[100px]">
              Analysis of semiconductor companies and optical technologies enabling compute, connectivity, and sensing.
            </p>
            <div className="flex items-center text-sm font-semibold text-gray-800">
              <div className="w-10 h-10 rounded bg-blue-50 text-blue-600 flex items-center justify-center mr-3 border border-blue-100">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>
              </div>
              Chips, Components & Photonics
            </div>
          </div>

          {/* Card 3 */}
          <div className="border border-gray-200 p-8 rounded-xl bg-white hover:shadow-lg transition-shadow">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Software & Cloud</h3>
            <p className="text-gray-600 leading-relaxed mb-10 min-h-[100px]">
              Research on software, cloud platforms, and enterprise solutions driving scalability, efficiency, and innovation.
            </p>
            <div className="flex items-center text-sm font-semibold text-gray-800">
              <div className="w-10 h-10 rounded bg-blue-50 text-blue-600 flex items-center justify-center mr-3 border border-blue-100">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"></path></svg>
              </div>
              Software, SaaS & Cloud
            </div>
          </div>
        </div>

        {/* DATA MODELS (Kept at the bottom so you can still access the trackers) */}
        <div className="mt-20 border-t border-gray-100 pt-16">
            <div className="flex items-center justify-center mb-10">
              <h2 className="text-sm font-bold tracking-widest text-gray-400 uppercase">Internal Tracking Dashboards</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Link href="/datacenters" className="block group">
                <div className="p-6 border border-gray-200 rounded-xl hover:border-blue-600 transition-colors bg-gray-50">
                  <h4 className="font-bold text-gray-900 mb-2 group-hover:text-blue-600">Datacenter Capacity &rarr;</h4>
                  <p className="text-sm text-gray-500">Live tracking of 76+ physical facilities and MW pipeline.</p>
                </div>
              </Link>

              <Link href="/gpu" className="block group">
                <div className="p-6 border border-gray-200 rounded-xl hover:border-blue-600 transition-colors bg-gray-50">
                  <h4 className="font-bold text-gray-900 mb-2 group-hover:text-blue-600">GPU Spot Pricing &rarr;</h4>
                  <p className="text-sm text-gray-500">Automated daily scraping of H100, H200, and B200 spot lease rates.</p>
                </div>
              </Link>

              <Link href="/npm" className="block group">
                <div className="p-6 border border-gray-200 rounded-xl hover:border-blue-600 transition-colors bg-gray-50">
                  <h4 className="font-bold text-gray-900 mb-2 group-hover:text-blue-600">NPM Alternative Data &rarr;</h4>
                  <p className="text-sm text-gray-500">Real-time developer adoption metrics tracking SDK downloads.</p>
                </div>
              </Link>
            </div>
        </div>

      </main>
    </div>
  );
}
