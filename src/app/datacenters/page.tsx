'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

interface Datacenter {
  id: string;
  company: string;
  name: string;
  location: string;
  status: string;
  estimated_capacity_mw: number;
  source_url?: string;
  permitting_status?: string;
  permitting_notes?: string;
  utility_provider?: string;
  municipality?: string;
}

const STATUS_ORDER = [
  'Fully operational',
  'Operational/expanding',
  'Under construction',
  'Planned',
  'Decommissioned/abandoned'
];

export default function DatacentersKanban() {
  const [data, setData] = useState<Datacenter[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch('/api/datacenters')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading datacenters...</div>;

  const companies = Array.from(new Set(data.map(d => d.company))).filter(Boolean).sort();

  return (
    <main className="p-8 max-w-[1600px] mx-auto bg-gray-50 min-h-screen">
      <div className="mb-6 flex items-center gap-4">
        <Link href="/" className="text-gray-500 hover:text-gray-800">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-3xl font-bold text-gray-800">📋 Datacenter Kanban</h1>
      </div>

      <div className="flex flex-col gap-8">
        {companies.map(company => {
          const compData = data.filter(d => d.company === company);
          
          return (
            <div key={company} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="bg-gray-100 px-6 py-4 border-b border-gray-200 font-bold text-lg text-gray-800 flex justify-between">
                <span>🏢 {company}</span>
                <span className="text-gray-500 text-sm font-normal">{compData.length} properties</span>
              </div>
              
              <div className="p-6 overflow-x-auto">
                <div className="flex gap-6 min-w-max">
                  {STATUS_ORDER.map(status => {
                    const statusData = compData.filter(d => d.status === status);
                    return (
                      <div key={status} className="w-[300px] flex-shrink-0 bg-gray-50 rounded-md p-4">
                        <h3 className="font-semibold text-gray-700 mb-4 pb-2 border-b border-gray-200 flex justify-between">
                          {status} <span className="bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full text-xs">{statusData.length}</span>
                        </h3>
                        
                        <div className="flex flex-col gap-3">
                          {statusData.map(dc => (
                            <div key={dc.id} className="bg-white p-3 rounded shadow-sm border border-blue-100 border-l-4 border-l-blue-500 text-sm">
                              <div className="font-bold text-gray-800 mb-2">{dc.name || 'Unnamed Property'}</div>
                              <div className="text-green-700 font-medium mb-1">⚡ {dc.estimated_capacity_mw ? `${dc.estimated_capacity_mw} MW` : 'TBD MW'}</div>
                              
                              <div className="text-gray-500 mb-2">📍 {dc.location || 'Location TBD'}</div>
                              
                              
                              <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-1.5 rounded border border-gray-100">
                                <div className="mb-0.5">🏢 <strong>Utility:</strong> {dc.utility_provider || 'Unknown'}</div>
                                <div>🏛️ <strong>Municipality:</strong> {dc.municipality || 'Unknown'}</div>
                              </div>
                              
                              <div className="mt-2 pt-2 border-t border-gray-100">
                                <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                                  dc.permitting_status === 'Approved' ? 'bg-green-100 text-green-800' :
                                  dc.permitting_status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                                  dc.permitting_status === 'Denied/Challenged' ? 'bg-red-100 text-red-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  📝 Permitting: {dc.permitting_status || 'Unknown'}
                                </span>
                                {dc.permitting_notes && <p className="text-xs text-gray-500 mt-1 italic">{dc.permitting_notes}</p>}
                              </div>

                              {dc.source_url && (
                                <a href={dc.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline text-xs block mt-2 border-t pt-2">
                                  🔗 Source Link
                                </a>
                              )}
                            </div>
                          ))}
                          {statusData.length === 0 && (
                            <div className="text-gray-400 text-center text-sm py-4 border-2 border-dashed border-gray-200 rounded">
                              No properties
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </main>
  );
}
