'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function SummaryBlog() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/blog')
      .then(res => res.json())
      .then(data => {
        setReports(data);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-8">Loading insights...</div>;

  return (
    <main className="p-8 max-w-4xl mx-auto bg-gray-50 min-h-screen">
      <div className="mb-6 flex items-center gap-4">
        <Link href="/" className="text-gray-500 hover:text-gray-800">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <h1 className="text-3xl font-bold text-gray-800">📰 Summary Blog & Insights</h1>
      </div>

      <div className="flex flex-col gap-8 mt-8">
        {reports.map((report) => (
          <div key={report.id || report.report_date} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div dangerouslySetInnerHTML={{ __html: report.html_content }} />
          </div>
        ))}
        {reports.length === 0 && (
          <div className="text-gray-500 text-center py-10">No reports available.</div>
        )}
      </div>
    </main>
  );
}
