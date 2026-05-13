import Link from 'next/link';

export default function Home() {
  return (
    <main className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-8 border-b pb-4">
        <h1 className="text-3xl font-bold text-gray-800">📋 AI Datacenter Tracker</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold mb-4 text-blue-600">📋 Datacenter Kanban</h2>
          <p className="text-gray-600 mb-6">Visualize datacenters grouped by Company and broken down by Pipeline Status.</p>
          <Link href="/datacenters" className="bg-blue-600 text-white px-4 py-2 rounded font-medium hover:bg-blue-700">
            Open Kanban Board &rarr;
          </Link>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
          <h2 className="text-xl font-semibold mb-4 text-green-600">📈 GPU Pricing</h2>
          <p className="text-gray-600 mb-6">Track historical and current spot pricing for H100, H200, and B200 instances.</p>
          <Link href="/gpu" className="bg-green-600 text-white px-4 py-2 rounded font-medium hover:bg-green-700">
            Open GPU Tracker &rarr;
          </Link>
        </div>
      </div>
    </main>
  );
}
