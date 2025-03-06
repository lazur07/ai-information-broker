import React, { useState } from "react";
import Header from "./components/Header";
import FilterPanel from "./components/FilterPanel";
import ArticleList from "./components/ArticleList";
import ArticleDetail from "./components/ArticleDetail";
import FilesManager from "./components/FilesManager";
import NewsSection from "./components/NewsSection";
import FilesSection from "./components/FilesSection";
import AnalyticsSection from "./components/AnalyticsSection";
import { NewsItem, InfoCollectReq } from "./types";
import { useArticles } from "./hooks/useArticles";

type TabType = 'News' | 'Files' | 'Analytics';

const App: React.FC = () => {
  const { articles, loading, error, fetchArticles } = useArticles();
  const [selectedArticle, setSelectedArticle] = useState<NewsItem | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('News');
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const handleFilter = (params: InfoCollectReq) => {
    fetchArticles(params);
  };

  // Function to render the appropriate content based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'News':
        return <NewsSection />;
      case 'Files':
        return <FilesSection />;
      case 'Analytics':
        return <AnalyticsSection />;
      default:
        return <NewsSection />;
    }
  };

  return (
    <div className="min-h-screen bg-ios-gray-100">
      {/* Header with navigation tabs */}
      <header className="sticky top-0 z-20 bg-white/90 backdrop-blur-lg border-b border-ios-gray-200 px-4 py-3">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <div className="flex items-center">
            {/* Mobile menu button */}
            <button 
              className="md:hidden mr-3 text-ios-gray-700"
              onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <h1 className="text-xl font-semibold text-black">AI Information</h1>
          </div>
          
          {/* Desktop navigation */}
          <div className="hidden md:flex space-x-1">
            {(['News', 'Files', 'Analytics'] as TabType[]).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                  activeTab === tab 
                    ? 'bg-uoft-blue text-white' 
                    : 'text-ios-gray-600 hover:bg-ios-gray-100'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Mobile navigation for tab switching */}
      <div className="md:hidden bg-white border-b border-ios-gray-200 px-4 py-2">
        <div className="flex justify-between">
          {(['News', 'Files', 'Analytics'] as TabType[]).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-2 text-sm font-medium ${
                activeTab === tab 
                  ? 'text-uoft-blue border-b-2 border-uoft-blue' 
                  : 'text-ios-gray-500'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <main className="max-w-5xl mx-auto py-6 px-4 sm:px-6">
        <div className="md:flex md:space-x-6">
          {/* Mobile sidebar overlay */}
          {mobileSidebarOpen && (
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
              onClick={() => setMobileSidebarOpen(false)}
            />
          )}
          
          {/* Sidebar with filters */}
          <div 
            className={`md:w-1/3 fixed md:relative inset-y-0 left-0 z-40 md:z-auto transform ${
              mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
            } transition-transform duration-300 ease-in-out md:translate-x-0 bg-white md:bg-transparent h-full md:h-auto overflow-y-auto md:overflow-visible`}
          >
            <div className="p-4 md:p-0">
              {/* Close button for mobile */}
              <div className="flex justify-end md:hidden mb-4">
                <button 
                  onClick={() => setMobileSidebarOpen(false)}
                  className="p-2 rounded-full text-ios-gray-500 hover:bg-ios-gray-100"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <FilterPanel onFilter={handleFilter} loading={loading} />

              {/* Stats summary if articles are loaded */}
              {articles && (
                <div className="bg-white rounded-ios p-5 shadow-ios mt-5">
                  <h2 className="text-sm font-semibold text-ios-gray-800 mb-4">
                    Statistics
                  </h2>
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-xs text-ios-gray-600 mb-1">
                        Total Articles
                      </p>
                      <p className="text-2xl font-semibold text-ios-gray-900">
                        {articles.total_count}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-ios-gray-600 mb-1">Updated</p>
                      <p className="text-sm font-medium text-ios-gray-800">
                        {new Date(articles.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Files Manager - only show in sidebar on larger screens and if not on Files tab */}
              <div className="hidden md:block mt-5">
                {activeTab !== 'Files' && <FilesManager />}
              </div>
            </div>
          </div>

          {/* Main content area */}
          <div className="md:w-2/3 mt-6 md:mt-0">
            <div className="bg-white rounded-ios shadow-ios p-4 md:p-6">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </main>

      {/* Article detail modal - will be shown when an article is selected */}
      {selectedArticle && (
        <ArticleDetail
          article={selectedArticle}
          onClose={() => setSelectedArticle(null)}
        />
      )}
    </div>
  );
};

export default App;