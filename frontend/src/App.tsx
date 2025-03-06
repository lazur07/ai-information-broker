import React, { useState } from 'react';
import { useArticles } from './hooks/useArticles';
import { NewsItem } from './types';
import Header from './components/Header';
import FilterPanel from './components/FilterPanel';
import ArticleList from './components/ArticleList';
import ArticleDetail from './components/ArticleDetail';

const App: React.FC = () => {
  const { articles, loading, error, fetchArticles } = useArticles();
  const [selectedArticle, setSelectedArticle] = useState<NewsItem | null>(null);

  return (
    <div className="min-h-screen bg-ios-gray-100">
      <Header />
      
      <main className="max-w-5xl mx-auto py-6 px-4 sm:px-6">
        <div className="md:flex md:space-x-6">
          {/* Sidebar with filters */}
          <div className="md:w-1/3">
            <FilterPanel onFilter={fetchArticles} loading={loading} />
            
            {/* Stats summary if articles are loaded */}
            {articles && (
              <div className="bg-white rounded-ios p-5 shadow-ios">
                <h2 className="text-sm font-semibold text-ios-gray-800 mb-4">Statistics</h2>
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <p className="text-xs text-ios-gray-600 mb-1">Total Articles</p>
                    <p className="text-2xl font-semibold text-ios-gray-900">{articles.total_count}</p>
                  </div>
                  <div>
                    <p className="text-xs text-ios-gray-600 mb-1">Updated</p>
                    <p className="text-sm font-medium text-ios-gray-800">{new Date(articles.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* Main content area */}
          <div className="md:w-2/3 mt-6 md:mt-0">
            {loading && (
              <div className="flex justify-center items-center h-64">
                <div className="relative w-14 h-14">
                  <div className="absolute top-0 left-0 w-full h-full border-4 border-ios-gray-200 rounded-full"></div>
                  <div className="absolute top-0 left-0 w-full h-full border-4 border-t-ios-blue rounded-full animate-spin"></div>
                </div>
              </div>
            )}
            
            {error && (
              <div className="bg-ios-red/10 border-l-4 border-ios-red rounded-r-ios p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-ios-red" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-ios-red">
                      {error}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            {!loading && !error && articles && articles.items.length === 0 && (
              <div className="bg-white rounded-ios shadow-ios p-8 text-center">
                <svg className="mx-auto h-12 w-12 text-ios-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 20a8 8 0 100-16 8 8 0 000 16z" />
                </svg>
                <p className="mt-4 text-ios-gray-600">No articles found. Try adjusting your filters.</p>
              </div>
            )}
            
            {!loading && !error && articles && articles.items.length > 0 && (
              <ArticleList 
                articles={articles.items} 
                onSelectArticle={setSelectedArticle} 
              />
            )}
          </div>
        </div>
      </main>
      
      {/* Article detail modal */}
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
