import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#F8F9FA] font-sans">
      {/* Header/Nav */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-black rounded-sm flex items-center justify-center">
              <span className="text-white font-bold text-sm">CR</span>
            </div>
            <span className="font-bold text-xl tracking-tight text-gray-900">CASRES</span>
          </div>
          <nav className="hidden md:flex space-x-8">
            <Link href="/" className="text-gray-900 font-medium text-sm border-b-2 border-black py-5">Research</Link>
            <Link href="/datacenters" className="text-gray-500 hover:text-gray-900 font-medium text-sm py-5 transition-colors">Infrastructure</Link>
            <Link href="/gpu" className="text-gray-500 hover:text-gray-900 font-medium text-sm py-5 transition-colors">GPU Tracker</Link>
            <Link href="/npm" className="text-gray-500 hover:text-gray-900 font-medium text-sm py-5 transition-colors">Alternative Data</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="mb-16 border-b border-gray-200 pb-12">
          <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight leading-tight mb-4">
            The AI Infrastructure Nexus
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl leading-relaxed">
            Deep-dive analysis and proprietary datasets tracking the physical, financial, and silicon bottlenecks of the AI rollout for Jetha Global.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          
          {/* Main Content / Recent Research Feed */}
          <div className="lg:col-span-2 space-y-10">
            <h2 className="text-sm font-bold tracking-widest text-gray-400 uppercase mb-6">Latest Research</h2>
            
            {/* Article 1 */}
            <article className="group cursor-pointer">
              <span className="text-xs font-semibold text-blue-600 uppercase tracking-wide">Macro Strategy</span>
              <Link href="/blog">
                <h3 className="text-2xl font-bold text-gray-900 mt-2 mb-3 group-hover:text-blue-600 transition-colors">
                  Lucis Compute: The Photonic Neocloud Strategy
                </h3>
              </Link>
              <p className="text-gray-600 leading-relaxed mb-4">
                The traditional GPU Neocloud is a brute-force model rapidly approaching its physical limits. By harnessing Opticore’s photonic processing, Lucis eliminates the crippling capital intensity of the energy shell and radically scales revenue density per megawatt.
              </p>
              <div className="text-sm text-gray-500 font-medium">October 6, 2026 • 12 min read</div>
            </article>

            <hr className="border-gray-100" />

            {/* Article 2 */}
            <article className="group cursor-pointer">
              <span className="text-xs font-semibold text-purple-600 uppercase tracking-wide">Alternative Data</span>
              <Link href="/blog">
                <h3 className="text-2xl font-bold text-gray-900 mt-2 mb-3 group-hover:text-purple-600 transition-colors">
                  NPM Tracker: Q3 Developer Mindshare Winners & Losers
                </h3>
              </Link>
              <p className="text-gray-600 leading-relaxed mb-4">
                A massive 62% surge in Okta's enterprise SDK adoption and a 55% jump in Cloudflare's edge compute tooling signals strong Q3 consumption, while Couchbase adoption unexpectedly shrinks.
              </p>
              <div className="text-sm text-gray-500 font-medium">October 2, 2026 • 5 min read</div>
            </article>

            <hr className="border-gray-100" />

            {/* Article 3 */}
            <article className="group cursor-pointer">
              <span className="text-xs font-semibold text-green-600 uppercase tracking-wide">Infrastructure</span>
              <Link href="/blog">
                <h3 className="text-2xl font-bold text-gray-900 mt-2 mb-3 group-hover:text-green-600 transition-colors">
                  The 1 GW AI Race: Why CCGT is the New Gold Rush
                </h3>
              </Link>
              <p className="text-gray-600 leading-relaxed mb-4">
                TeraWulf's massive 1GW pivot to Eastern Kentucky exposes the fragility of the public grid. To bypass interconnection bottlenecks, Neoclouds are abandoning renewables for localized Combined Cycle Gas Turbines.
              </p>
              <div className="text-sm text-gray-500 font-medium">September 28, 2026 • 8 min read</div>
            </article>
          </div>

          {/* Sidebar / Data Models */}
          <div className="space-y-8">
            <h2 className="text-sm font-bold tracking-widest text-gray-400 uppercase mb-6">Proprietary Models</h2>
            
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                </div>
                <h3 className="font-bold text-gray-900">Datacenter Capacity</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">Live tracking of 76+ physical facilities, permitting statuses, and MW pipeline across primary Neoclouds.</p>
              <Link href="/datacenters" className="text-sm font-semibold text-blue-600 hover:text-blue-800">Access Tracker &rarr;</Link>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center text-green-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                </div>
                <h3 className="font-bold text-gray-900">GPU Spot Pricing</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">Automated daily scraping of H100, H200, and B200 spot lease rates across competing inference providers.</p>
              <Link href="/gpu" className="text-sm font-semibold text-green-600 hover:text-green-800">Access Tracker &rarr;</Link>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-purple-50 rounded-lg flex items-center justify-center text-purple-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                </div>
                <h3 className="font-bold text-gray-900">Alternative Data</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">Real-time developer adoption metrics tracking SDK downloads for MDB, SNOW, DDOG, and Okta.</p>
              <Link href="/npm" className="text-sm font-semibold text-purple-600 hover:text-purple-800">Access Tracker &rarr;</Link>
            </div>
            
          </div>
        </div>
      </main>
    </div>
  );
}
