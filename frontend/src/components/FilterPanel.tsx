// frontend/src/components/FilterPanel.tsx
import React, { useState } from 'react';
import { InfoCollectReq, NewsSource } from '../types';

interface FilterPanelProps {
  onFilter: (params: InfoCollectReq) => void;
  loading: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ onFilter, loading }) => {
  const [filters, setFilters] = useState<InfoCollectReq>({
    days_back: 1,
    category: "AI",
    source: ["techcrunch", "36kr"],
    limit: 20
  });

  const handleSourceChange = (source: NewsSource) => {
    setFilters(prev => {
      const newSources = prev.source.includes(source)
        ? prev.source.filter(s => s !== source)
        : [...prev.source, source];
      
      // Ensure at least one source is selected
      return {
        ...prev,
        source: newSources.length > 0 ? newSources : prev.source
      };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilter(filters);
  };

  return (
    <div className="bg-white rounded-ios shadow-ios p-5 mb-5">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-ios-gray-800 mb-2">
            Days Back
          </label>
          <input
            type="number"
            min="1"
            max="7"
            value={filters.days_back}
            onChange={e => setFilters({...filters, days_back: parseInt(e.target.value) || 1})}
            className="block w-full rounded-ios bg-ios-gray-100 border-none px-4 py-3 text-ios-gray-800 focus:ring-2 focus:ring-uoft-blue focus:bg-white focus:outline-none transition duration-200"
          />
        </div>
        
        <div>
          <label className="block text-sm font-semibold text-ios-gray-800 mb-2">
            Category
          </label>
          <input
            type="text"
            value={filters.category}
            onChange={e => setFilters({...filters, category: e.target.value})}
            className="block w-full rounded-ios bg-ios-gray-100 border-none px-4 py-3 text-ios-gray-800 focus:ring-2 focus:ring-ios-blue focus:bg-white focus:outline-none transition duration-200"
          />
        </div>
        
        <div className="pt-2">
          <span className="block text-sm font-semibold text-ios-gray-800 mb-2">Sources</span>
          <div className="flex space-x-5">
            <label className="relative flex items-center space-x-3">
              <input
                type="checkbox"
                checked={filters.source.includes("techcrunch")}
                onChange={() => handleSourceChange("techcrunch")}
                className="peer sr-only"
              />
              <div className="w-6 h-6 rounded-full bg-ios-gray-100 peer-checked:bg-uoft-blue relative before:absolute before:w-3 before:h-2 before:border-white before:border-b-2 before:border-r-2 before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-45 before:scale-0 peer-checked:before:scale-100 before:transition duration-150"></div>
              <span className="text-sm text-ios-gray-700">TechCrunch</span>
            </label>
            
            <label className="relative flex items-center space-x-3">
              <input
                type="checkbox"
                checked={filters.source.includes("36kr")}
                onChange={() => handleSourceChange("36kr")}
                className="peer sr-only"
              />
              <div className="w-6 h-6 rounded-full bg-ios-gray-100 peer-checked:bg-uoft-blue relative before:absolute before:w-3 before:h-2 before:border-white before:border-b-2 before:border-r-2 before:top-1/2 before:left-1/2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-45 before:scale-0 peer-checked:before:scale-100 before:transition duration-150"></div>
              <span className="text-sm text-ios-gray-700">36Kr</span>
            </label>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-semibold text-ios-gray-800 mb-2">
            Limit
          </label>
          <input
            type="number"
            min="1"
            max="50"
            value={filters.limit}
            onChange={e => setFilters({...filters, limit: parseInt(e.target.value) || 20})}
            className="block w-full rounded-ios bg-ios-gray-100 border-none px-4 py-3 text-ios-gray-800 focus:ring-2 focus:ring-ios-blue focus:bg-white focus:outline-none transition duration-200"
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center mt-4 py-3.5 px-4 rounded-ios font-medium text-base text-white
            bg-uoft-blue hover:bg-opacity-90 active:bg-opacity-80 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-uoft-blue
            disabled:bg-opacity-70 disabled:cursor-not-allowed transition duration-150"
        >
          {loading ? (
            <div className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Loading...</span>
            </div>
          ) : 'Fetch Articles'}
        </button>
      </form>
    </div>
  );
};

export default FilterPanel;