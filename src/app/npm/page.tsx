'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function NPMPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const databases = ['MDB', 'SNOW', 'ESTC', 'BASE'];
  const infrastructure = ['DDOG', 'NET', 'OKTA', 'HCP', 'DT'];
  const ecommerce = ['TWLO', 'SHOP', 'PYPL', 'SQ', 'AMPL', 'BRZE'];

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/api/npm');
        const json = await res.json();
        if (json.success) {
          setData(json.data);
        }
      } catch (error) {
        console.error("Failed to fetch NPM data", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const formatYAxis = (tickItem: any) => `${tickItem.toFixed(0)}%`;

  const formatTooltip = (value: any) => `${Number(value).toFixed(1)}%`;

  const colors = ['#2563EB', '#16A34A', '#D97706', '#DC2626', '#9333EA', '#0891B2'];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8F9FA] p-8 flex items-center justify-center">
        <div className="text-xl font-medium text-gray-500 animate-pulse">Loading Proprietary Data Models...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FA] pb-24">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 py-12 mb-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link href="/" className="text-sm font-bold text-blue-600 uppercase tracking-wide hover:underline mb-4 inline-block">&larr; Back to Research</Link>
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-4">NPM Alternative Data Tracker</h1>
          <p className="text-xl text-gray-600 max-w-3xl">
            Real-time developer mindshare tracking. We scrape the NPM registry daily to track SDK adoption across publicly traded infrastructure and software companies. Charts show week-over-week growth rates derived from 7-day rolling averages — normalizing weekend effects and making cross-company trends directly comparable.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Databases & Search</h2>
          <p className="text-gray-500 mb-8 text-sm">Tracking MongoDB, Snowflake, Elastic, and Couchbase</p>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{fontSize: 12}} tickMargin={10} minTickGap={30} />
                <YAxis tickFormatter={formatYAxis} tick={{fontSize: 12}} width={80} />
                <Tooltip formatter={formatTooltip} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                {databases.map((ticker, i) => (
                  <Line key={ticker} type="monotone" dataKey={ticker} stroke={colors[i % colors.length]} strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Infrastructure, Edge & Security</h2>
          <p className="text-gray-500 mb-8 text-sm">Tracking Cloudflare, Datadog, Okta, HashiCorp, and Dynatrace</p>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{fontSize: 12}} tickMargin={10} minTickGap={30} />
                <YAxis tickFormatter={formatYAxis} tick={{fontSize: 12}} width={80} />
                <Tooltip formatter={formatTooltip} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                {infrastructure.map((ticker, i) => (
                  <Line key={ticker} type="monotone" dataKey={ticker} stroke={colors[i % colors.length]} strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Communications, Analytics & E-Commerce</h2>
          <p className="text-gray-500 mb-8 text-sm">Tracking Twilio, Shopify, PayPal, Square, Amplitude, and Braze</p>
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{fontSize: 12}} tickMargin={10} minTickGap={30} />
                <YAxis tickFormatter={formatYAxis} tick={{fontSize: 12}} width={80} />
                <Tooltip formatter={formatTooltip} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                {ecommerce.map((ticker, i) => (
                  <Line key={ticker} type="monotone" dataKey={ticker} stroke={colors[i % colors.length]} strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
