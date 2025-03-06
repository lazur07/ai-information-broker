import React, { useState, useEffect } from 'react';
import FilesManager from './FilesManager';

interface FileInfo {
  filename: string;
  time_range: string;
  article_count: number;
  file_size: string;
  created: number;
}

const FilesSection: React.FC = () => {
  const [recentFiles, setRecentFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching data
    setLoading(true);
    setTimeout(() => {
      // Mock data for example
      const mockRecentFiles: FileInfo[] = [
        {
          filename: 'ai_news_20250305.json',
          time_range: 'Mar 1, 2025 to Mar 5, 2025',
          article_count: 42,
          file_size: '156 KB',
          created: Date.now()
        },
        {
          filename: 'ai_news_20250228.json',
          time_range: 'Feb 20, 2025 to Feb 28, 2025',
          article_count: 86,
          file_size: '320 KB',
          created: Date.now() - 86400000
        }
      ];
      setRecentFiles(mockRecentFiles);
      setLoading(false);
    }, 800);
  }, []);

  return (
    <div className="py-6">
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-ios-gray-800 mb-2">File Management</h2>
        <p className="text-ios-gray-600">Access and download your saved article collections</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <FilesManager className="" />
        </div>
        
        <div className="bg-white rounded-ios shadow-ios p-5">
          <h3 className="text-sm font-semibold text-ios-gray-800 mb-4">Quick Actions</h3>
          
          <div className="space-y-3">
            <button className="w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-white bg-uoft-blue hover:bg-opacity-90 text-sm transition duration-150">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
              </svg>
              Create New Collection
            </button>
            
            <button className="w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-ios-gray-800 bg-ios-gray-100 hover:bg-ios-gray-200 text-sm transition duration-150">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              Export All Files
            </button>
            
            <button className="w-full flex items-center justify-center py-2.5 px-4 rounded-ios font-medium text-ios-gray-800 bg-ios-gray-100 hover:bg-ios-gray-200 text-sm transition duration-150">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilesSection;