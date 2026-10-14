import Link from 'next/link';
import Image from 'next/image';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#FDFDFD] font-sans text-gray-900">
      
      {/* 
        HERO SECTION
        SemiAnalysis uses a massive, bold hero section that instantly establishes authority.
      */}
      <div className="bg-[#111111] text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
          <div className="max-w-3xl">
            <h1 className="text-5xl lg:text-7xl font-bold tracking-tight mb-6 leading-[1.1]">
              The architecture of the AI transition.
            </h1>
            <p className="text-xl lg:text-2xl text-gray-400 font-light mb-10 leading-relaxed">
              Institutional-grade research and proprietary data models tracking the silicon, physical, and financial bottlenecks of the global compute rollout.
            </p>
            <div className="flex space-x-4">
              <Link href="#research" className="bg-white text-black px-8 py-4 rounded-full font-bold text-sm uppercase tracking-wide hover:bg-gray-200 transition-colors">
                Read Latest Research
              </Link>
              <Link href="#models" className="border border-gray-600 text-white px-8 py-4 rounded-full font-bold text-sm uppercase tracking-wide hover:border-white transition-colors">
                Access Data Models
              </Link>
            </div>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
          
          {/* 
            LEFT COLUMN: RESEARCH FEED (8 columns wide)
            Clean, minimalist article cards with heavy typography.
          */}
          <div className="lg:col-span-8" id="research">
            <div className="flex items-center justify-between border-b-2 border-black pb-4 mb-10">
              <h2 className="text-2xl font-bold tracking-tight">Recent Analysis</h2>
              <Link href="/blog" className="text-sm font-bold text-blue-600 uppercase tracking-wide hover:underline">View All &rarr;</Link>
            </div>

            <div className="space-y-12">
              {/* Featured Article */}
              <article className="group cursor-pointer">
                <p className="text-sm font-bold text-blue-600 uppercase tracking-wide mb-3">Macro Strategy</p>
                <Link href="/blog">
                  <h3 className="text-4xl font-extrabold tracking-tight mb-4 group-hover:text-blue-600 transition-colors leading-tight">
                    Lucis Compute: The Photonic Neocloud Strategy
                  </h3>
                </Link>
                <p className="text-lg text-gray-600 leading-relaxed mb-6">
                  The traditional GPU Neocloud is a brute-force model rapidly approaching its physical limits. By harnessing Opticore’s photonic processing, Lucis eliminates the crippling capital intensity of the energy shell and radically scales revenue density per megawatt. We break down the financial arbitrage.
                </p>
                <div className="flex items-center text-sm font-medium text-gray-500">
                  <span>Curtis Shauger</span>
                  <span className="mx-2">•</span>
                  <span>October 6, 2026</span>
                </div>
              </article>

              <hr className="border-gray-200" />

              {/* Standard Article 1 */}
              <article className="grid grid-cols-1 md:grid-cols-4 gap-6 group cursor-pointer">
                <div className="md:col-span-3">
                  <p className="text-xs font-bold text-purple-600 uppercase tracking-wide mb-2">Alternative Data</p>
                  <Link href="/blog">
                    <h3 className="text-2xl font-bold tracking-tight mb-3 group-hover:text-purple-600 transition-colors leading-snug">
                      NPM Tracker: Q3 Developer Mindshare Winners & Losers
                    </h3>
                  </Link>
                  <p className="text-gray-600 leading-relaxed mb-3">
                    A massive 62% surge in Okta's enterprise SDK adoption and a 55% jump in Cloudflare's edge compute tooling signals strong Q3 consumption, while Couchbase adoption unexpectedly shrinks.
                  </p>
                  <div className="text-sm font-medium text-gray-500">October 2, 2026</div>
                </div>
                <div className="hidden md:block bg-gray-100 rounded-lg aspect-square"></div>
              </article>

              <hr className="border-gray-200" />

              {/* Standard Article 2 */}
              <article className="grid grid-cols-1 md:grid-cols-4 gap-6 group cursor-pointer">
                <div className="md:col-span-3">
                  <p className="text-xs font-bold text-green-600 uppercase tracking-wide mb-2">Infrastructure</p>
                  <Link href="/blog">
                    <h3 className="text-2xl font-bold tracking-tight mb-3 group-hover:text-green-600 transition-colors leading-snug">
                      The 1 GW AI Race: Why CCGT is the New Gold Rush
                    </h3>
                  </Link>
                  <p className="text-gray-600 leading-relaxed mb-3">
                    TeraWulf's massive 1GW pivot to Eastern Kentucky exposes the fragility of the public grid. To bypass interconnection bottlenecks, Neoclouds are abandoning renewables for localized Combined Cycle Gas Turbines.
                  </p>
                  <div className="text-sm font-medium text-gray-500">September 28, 2026</div>
                </div>
                <div className="hidden md:block bg-gray-100 rounded-lg aspect-square"></div>
              </article>
            </div>
          </div>

          {/* 
            RIGHT COLUMN: DATA MODELS & SUBSCRIBE (4 columns wide)
            Clean, bordered utility boxes.
          */}
          <div className="lg:col-span-4 space-y-8" id="models">
            
            {/* Subscription/About Box */}
            <div className="bg-gray-50 border border-gray-200 p-8 rounded-2xl">
              <h3 className="text-lg font-bold mb-3">About CAS Research</h3>
              <p className="text-gray-600 text-sm mb-6 leading-relaxed">
                CAS Research is the internal intelligence engine for Jetha Global. We provide proprietary data pipelines and unvarnished analysis on the semiconductor and data center supply chains.
              </p>
              <button className="w-full bg-black text-white font-bold py-3 rounded-lg hover:bg-gray-800 transition-colors">
                Subscribe to Newsletter
              </button>
            </div>

            <div className="border-b-2 border-black pb-3 mt-10 mb-6">
              <h2 className="text-xl font-bold tracking-tight">Proprietary Models</h2>
            </div>

            {/* Model Links */}
            <div className="space-y-4">
              <Link href="/datacenters" className="block group">
                <div className="border border-gray-200 p-5 rounded-xl hover:border-blue-600 hover:shadow-md transition-all bg-white">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-bold text-gray-900 group-hover:text-blue-600">Datacenter Capacity &rarr;</h4>
                  </div>
                  <p className="text-sm text-gray-500">Live tracking of 76+ physical facilities and MW pipeline across primary Neoclouds.</p>
                </div>
              </Link>

              <Link href="/gpu" className="block group">
                <div className="border border-gray-200 p-5 rounded-xl hover:border-green-600 hover:shadow-md transition-all bg-white">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-bold text-gray-900 group-hover:text-green-600">GPU Spot Pricing &rarr;</h4>
                  </div>
                  <p className="text-sm text-gray-500">Automated daily scraping of H100, H200, and B200 spot lease rates.</p>
                </div>
              </Link>

              <Link href="/npm" className="block group">
                <div className="border border-gray-200 p-5 rounded-xl hover:border-purple-600 hover:shadow-md transition-all bg-white">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="font-bold text-gray-900 group-hover:text-purple-600">NPM Alternative Data &rarr;</h4>
                  </div>
                  <p className="text-sm text-gray-500">Real-time developer adoption metrics tracking SDK downloads for MDB, SNOW, DDOG.</p>
                </div>
              </Link>
            </div>

          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-12 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="font-bold text-xl tracking-tight text-gray-900 mb-4">CAS Research</div>
          <p className="text-sm text-gray-500">© 2026 Jetha Global. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
