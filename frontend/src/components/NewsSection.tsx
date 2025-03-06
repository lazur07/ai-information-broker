import React, { useState, useEffect } from 'react';
import ArticleList from './ArticleList';
import ArticleDetail from './ArticleDetail';
import { NewsItem } from '../types';

const NewsSection: React.FC = () => {
  const [articles, setArticles] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<NewsItem | null>(null);

  useEffect(() => {
    // Fetch articles from the latest JSON file
    const fetchArticles = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // First, fetch the list of files to get the latest one
        const filesResponse = await fetch("/data/info/files");
        
        if (!filesResponse.ok) {
          throw new Error(`Error fetching files: ${filesResponse.status}`);
        }
        
        const files = await filesResponse.json();
        
        // Check if there are any files
        if (!files || files.length === 0) {
          setArticles([]);
          return;
        }
        
        // Sort files by creation date (newest first)
        const sortedFiles = [...files].sort((a, b) => b.created - a.created);
        const latestFile = sortedFiles[0];
        
        // Fetch the content of the latest file
        const contentResponse = await fetch(`/data/info/files/${encodeURIComponent(latestFile.filename)}`);
        
        if (!contentResponse.ok) {
          throw new Error(`Error fetching file content: ${contentResponse.status}`);
        }
        
        const fileContent = await contentResponse.json();
        
        // Transform the file content to match our NewsItem format
        const articlesData: NewsItem[] = fileContent.map((item: any, index: number) => ({
          id: item.id || `article-${index}`,
          url: item.url || '',
          title: item.title || 'Untitled Article',
          author: item.author || null,
          summary: item.summary || null,
          content: item.content || null,
          publish_timestamp: item.publish_timestamp || Date.now(),
          gmt8time: item.gmt8time || new Date().toISOString(),
          source: item.source || 'techcrunch'
        }));
        
        setArticles(articlesData);
      } catch (err) {
        setError('Failed to load articles. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-ios-gray-800 mb-1">Latest News</h2>
        <p className="text-ios-gray-600">Stay updated with the latest AI developments</p>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="relative w-12 h-12">
            <div className="absolute top-0 left-0 w-full h-full border-4 border-ios-gray-200 rounded-full"></div>
            <div className="absolute top-0 left-0 w-full h-full border-4 border-t-ios-blue rounded-full animate-spin"></div>
          </div>
        </div>
      ) : error ? (
        <div className="bg-ios-red/10 border-l-4 border-ios-red rounded-r-ios p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-ios-red" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-ios-red">{error}</p>
            </div>
          </div>
        </div>
      ) : articles.length === 0 ? (
        <div className="bg-white rounded-ios shadow-ios p-8 text-center">
          <svg className="mx-auto h-12 w-12 text-ios-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 20a8 8 0 100-16 8 8 0 000 16z" />
          </svg>
          <p className="mt-4 text-ios-gray-600">No articles found. Try adjusting your filters.</p>
        </div>
      ) : (
        <ArticleList articles={articles} onSelectArticle={setSelectedArticle} />
      )}
      
      {selectedArticle && (
        <ArticleDetail article={selectedArticle} onClose={() => setSelectedArticle(null)} />
      )}
    </div>
  );
};

export default NewsSection;