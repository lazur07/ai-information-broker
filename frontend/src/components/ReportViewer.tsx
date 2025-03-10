// frontend/src/components/ReportViewer.tsx
import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface ReportViewerProps {
  reportFile: string;
  onClose: () => void;
}

const ReportViewer: React.FC<ReportViewerProps> = ({ reportFile, onClose }) => {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`/data/info/files/${encodeURIComponent(reportFile)}`);
        
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.text();
        setContent(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load report');
      } finally {
        setLoading(false);
      }
    };

    if (reportFile) {
      fetchReport();
    }
  }, [reportFile]);

  return (
    <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm overflow-y-auto h-full w-full flex items-center justify-center">
      <div className="relative w-full max-w-4xl mx-auto p-4">
        <div className="bg-white rounded-ios shadow-ios-strong overflow-hidden">
          <div className="flex justify-between items-center p-4 border-b border-ios-gray-200">
            <h2 className="text-lg font-semibold text-ios-gray-900">AI News Report</h2>
            <button
              onClick={onClose}
              className="bg-ios-gray-100 text-ios-gray-700 rounded-full p-1.5 hover:bg-ios-gray-200 active:bg-ios-gray-300 transition-colors"
            >
              <svg
                className="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <div
            className="p-6 overflow-y-auto"
            style={{ maxHeight: "calc(100vh - 120px)" }}
          >
            {loading ? (
              <div className="flex justify-center items-center py-10">
                <div className="w-10 h-10 border-4 border-uoft-blue border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : error ? (
              <div className="bg-ios-red/10 text-ios-red p-4 rounded-ios">
                <p>Failed to load report: {error}</p>
              </div>
            ) : (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-ios-gray-200 flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-ios text-ios-gray-700 bg-ios-gray-100 hover:bg-ios-gray-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportViewer;