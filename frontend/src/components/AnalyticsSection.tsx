import React from 'react';

const AnalyticsSection: React.FC = () => {
  return (
    <div className="py-8">
      <div className="text-center mb-8">
        <h2 className="text-lg font-semibold text-ios-gray-800 mb-2">Analytics Dashboard</h2>
        <p className="text-ios-gray-600">Visualize data and insights from your articles</p>
      </div>
      
      <div className="border-2 border-dashed border-ios-gray-200 rounded-ios p-12 bg-ios-gray-50">
        <div className="flex flex-col items-center justify-center text-center">
          <svg className="w-16 h-16 text-ios-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <h3 className="text-md font-medium text-uoft-blue mb-2">Analytics Visualizations Coming Soon</h3>
          <p className="text-ios-gray-500 max-w-md mx-auto">
            Future updates will include interactive charts, word clouds, and knowledge graphs to help you analyze your article collection.
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="bg-white rounded-ios shadow-ios p-6">
          <h3 className="text-sm font-semibold text-ios-gray-800 mb-4">Popular Topics</h3>
          <div className="h-40 flex items-center justify-center border border-ios-gray-200 rounded-ios bg-ios-gray-50">
            <p className="text-ios-gray-500 text-sm">Word cloud visualization coming soon</p>
          </div>
        </div>
        
        <div className="bg-white rounded-ios shadow-ios p-6">
          <h3 className="text-sm font-semibold text-ios-gray-800 mb-4">Article Trends</h3>
          <div className="h-40 flex items-center justify-center border border-ios-gray-200 rounded-ios bg-ios-gray-50">
            <p className="text-ios-gray-500 text-sm">Trend chart visualization coming soon</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsSection;