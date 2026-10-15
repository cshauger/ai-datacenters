import Link from 'next/link';

export default function Home() {
  return (
    <main className="max-w-6xl mx-auto px-4 py-12 flex-1 w-full font-sans">
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* LEFT: Featured Post (2/3 width) */}
        <div className="lg:col-span-2">
          <Link href="/blog" className="block group">
            <div className="w-full aspect-[16/9] bg-gray-100 rounded-md mb-6 overflow-hidden flex items-center justify-center border border-gray-200">
              {/* Placeholder for Substack-style featured image */}
              <div className="w-16 h-16 opacity-20">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
              </div>
            </div>
            <h2 className="text-4xl font-extrabold text-gray-900 leading-tight mb-3 group-hover:underline decoration-2 underline-offset-4">
              Lucis Compute: The Photonic Neocloud Strategy
            </h2>
            <p className="text-xl text-gray-600 mb-6 leading-relaxed">
              The traditional GPU Neocloud is a brute-force model rapidly approaching its physical limits. By harnessing Opticore’s photonic processing, Lucis eliminates the crippling capital intensity of the energy shell and radically scales revenue density per megawatt.
            </p>
          </Link>
          <div className="flex items-center space-x-3 text-sm text-gray-500">
            <div className="w-10 h-10 rounded-full bg-gray-200 border border-gray-300"></div>
            <div>
              <span className="font-semibold text-gray-900 block">Curtis Shauger</span>
              <div className="flex items-center space-x-1">
                <span>Oct 6</span>
                <span>•</span>
                <span>12 min read</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT: Recent Posts List (1/3 width) */}
        <div className="lg:col-span-1 space-y-8">
          <h3 className="text-xs font-bold uppercase tracking-widest text-gray-400 border-b border-gray-200 pb-3">Recent</h3>
          
          {/* Article 2 */}
          <article>
            <Link href="/blog" className="block group">
              <h4 className="text-xl font-bold text-gray-900 mb-2 group-hover:underline decoration-2 underline-offset-2 leading-snug">
                NPM Tracker: Q3 Developer Mindshare Winners & Losers
              </h4>
              <p className="text-sm text-gray-600 mb-3 line-clamp-3 leading-relaxed">
                A massive 62% surge in Okta's enterprise SDK adoption and a 55% jump in Cloudflare's edge compute tooling signals strong Q3 consumption, while Couchbase shrinks.
              </p>
            </Link>
            <div className="text-xs text-gray-500 font-medium">Oct 2 • Curtis Shauger</div>
          </article>

          {/* Article 3 */}
          <article>
            <Link href="/blog" className="block group">
              <h4 className="text-xl font-bold text-gray-900 mb-2 group-hover:underline decoration-2 underline-offset-2 leading-snug">
                The 1 GW AI Race: Why CCGT is the New Gold Rush
              </h4>
              <p className="text-sm text-gray-600 mb-3 line-clamp-3 leading-relaxed">
                TeraWulf's massive 1GW pivot to Eastern Kentucky exposes the fragility of the public grid. To bypass bottlenecks, Neoclouds are abandoning renewables for natural gas.
              </p>
            </Link>
            <div className="text-xs text-gray-500 font-medium">Sep 28 • Curtis Shauger</div>
          </article>

          {/* Article 4 */}
          <article>
            <Link href="/blog" className="block group">
              <h4 className="text-xl font-bold text-gray-900 mb-2 group-hover:underline decoration-2 underline-offset-2 leading-snug">
                Volta Emerges: The $5B Debt Syndicate Explained
              </h4>
              <p className="text-sm text-gray-600 mb-3 line-clamp-3 leading-relaxed">
                JPMorgan is dangling an 11% yield to fund Volta's massive hyperscale AI data center buildout.
              </p>
            </Link>
            <div className="text-xs text-gray-500 font-medium">Sep 25 • Curtis Shauger</div>
          </article>
        </div>
      </div>
    </main>
  );
}
