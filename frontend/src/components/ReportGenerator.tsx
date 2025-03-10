// frontend/src/components/ReportGenerator.tsx
import React, { useState } from 'react';
import { NewsSource } from '../types';
import ReportViewer from './ReportViewer';

interface ReportGeneratorProps {
  selectedFile: string | null;
  onReportGenerated: () => void;
}

interface ReportOptions {
  item_ids?: string[];
}

interface GeneratedReport {
  timestamp: number;
  report_file: string;
  title: string;
  summary: string;
  key_points: string[];
  full_report: string;
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({ 
  selectedFile, 
  onReportGenerated 
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState<ReportOptions>({
    item_ids: undefined
  });
  const [showOptions, setShowOptions] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<GeneratedReport | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [showReportViewer, setShowReportViewer] = useState(false);

  const generateReport = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setGeneratedReport(null);
    
    try {
      const response = await fetch('/data/info/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: selectedFile,
          item_ids: options.item_ids
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error: ${response.status}`);
      }
      
      const data = await response.json();
      setGeneratedReport(data);
      setShowResult(true);
      onReportGenerated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const toggleSourceOption = (source: NewsSource) => {
    // No longer needed, but keeping empty function in case it's referenced elsewhere
  };

  return (
    <div>
      <div className="space-y-3">
        <button
          onClick={() => selectedFile ? generateReport() : setError('Please select a file first')}
          disabled={loading || !selectedFile}
          className="w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-ios-gray-800 bg-ios-gray-100 hover:bg-ios-gray-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm transition duration-150"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
        
        <button
          onClick={() => setShowOptions(!showOptions)}
          className="w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-ios-gray-800 bg-ios-gray-50 hover:bg-ios-gray-100 text-sm transition duration-150"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          {showOptions ? 'Hide Options' : 'Show Options'}
        </button>
      </div>

      {error && (
        <div className="mt-3 p-3 bg-ios-red/10 text-ios-red text-sm rounded-ios">
          {error}
        </div>
      )}

      {showOptions && (
        <div className="mt-4 p-4 border border-ios-gray-200 rounded-ios">
          <h4 className="text-sm font-medium text-ios-gray-800 mb-3">Report Options</h4>
          
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-ios-gray-700 mb-2">
                Article Selection
              </label>
              <p className="text-xs text-ios-gray-600 mb-2">
                Select specific articles by clicking on them in the files panel. 
                If no articles are selected, all articles in the selected file will be included.
              </p>
            </div>
          </div>
        </div>
      )}

      {showResult && generatedReport && (
        <div className="mt-4 p-4 border border-ios-gray-200 rounded-ios bg-ios-gray-50">
          <div className="flex justify-between items-center mb-3">
            <h4 className="text-sm font-medium text-ios-gray-800">Report Generated</h4>
            <button 
              onClick={() => setShowResult(false)}
              className="text-xs text-ios-gray-500 hover:text-ios-gray-700"
            >
              Close
            </button>
          </div>
          
          <div className="text-sm text-ios-gray-800">
            <p className="font-medium">{generatedReport.title}</p>
            <p className="mt-2 text-xs text-ios-gray-600">
              Generated on {new Date(generatedReport.timestamp * 1000).toLocaleString()}
            </p>
            
            <div className="mt-3 flex items-center">
              <button
                onClick={() => setShowReportViewer(true)}
                className="inline-flex items-center px-3 py-1.5 rounded-ios text-xs font-medium text-white bg-uoft-blue hover:bg-opacity-90 mr-2"
              >
                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                View Report
              </button>
              
              <a
                href={`/data/info/files/${generatedReport.report_file}`}
                download
                className="inline-flex items-center px-3 py-1.5 rounded-ios text-xs font-medium text-ios-gray-700 bg-ios-gray-100 hover:bg-ios-gray-200"
              >
                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                Download
              </a>
            </div>
          </div>
        </div>
      )}

      {showReportViewer && generatedReport && (
        <ReportViewer 
          reportFile={generatedReport.report_file} 
          onClose={() => setShowReportViewer(false)} 
        />
      )}
    </div>
  );
};

export default ReportGenerator;