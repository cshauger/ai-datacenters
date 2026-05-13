'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function GPUPricing() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGpu, setSelectedGpu] = useState('H100');

  useEffect(() => {
    fetch('/api/gpu')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading GPU pricing data...</div>;

  // Process data for charts
  const chartData: any[] = [];
  const gpuTypes = Array.from(new Set(data.map(d => d.gpu_type))).sort();
  
  if (data.length > 0) {
    // Group by date
    const byDate = data.reduce((acc: any, curr: any) => {
      // Postgres returns dates cleanly, but we parse to ISO string prefix
      const dateStr = curr.date.substring(0,10);
      if (!acc[dateStr]) acc[dateStr] = { date: dateStr };
      
      // We only care about the selected GPU type for the current view
      if (curr.gpu_type === selectedGpu) {
        acc[dateStr][curr.provider] = parseFloat(curr.price_per_hr);
      }
      return acc;
    }, {});
    
    // Convert to array and sort chronologically
    for (const [key, value] of Object.entries(byDate)) {
      chartData.push(value);
    }
    chartData.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }

  // Get unique providers for the selected GPU to generate lines
  const providers = Array.from(
    new Set(data.filter(d => d.gpu_type === selectedGpu).map(d => d.provider))
  );

  // Generate distinct colors
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#e57373', '#ba68c8', '#64b5f6'];

  return (
    <main className="p-8 max-w-7xl mx-auto bg-gray-50 min-h-screen">
      <div className="mb-6 flex items-center gap-4">
        <Link href="/" className="text-gray-500 hover:text-gray-800">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-3xl font-bold text-gray-800">📈 GPU Pricing Tracker</h1>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
        <div className="flex gap-4 mb-6">
          {gpuTypes.map(type => (
            <button
              key={type as string}
              onClick={() => setSelectedGpu(type as string)}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                selectedGpu === type 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {type as string}
            </button>
          ))}
        </div>

        <div className="h-[600px] w-full mt-8">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="date" />
              <YAxis 
                label={{ value: 'Price per Hour (USD)', angle: -90, position: 'insideLeft' }} 
                domain={['auto', 'auto']}
              />
              <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              {providers.map((provider, i) => (
                <Line 
                  key={provider as string} 
                  type="monotone" 
                  dataKey={provider as string} 
                  stroke={colors[i % colors.length]} 
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </main>
  );
}
