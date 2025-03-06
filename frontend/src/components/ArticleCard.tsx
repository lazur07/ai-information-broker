// frontend/src/components/ArticleCard.tsx
import React from 'react';
import { NewsItem } from '../types';

interface ArticleCardProps {
  article: NewsItem;
  onClick: () => void;
}

const ArticleCard: React.FC<ArticleCardProps> = ({ article, onClick }) => {
  // Format date to be more readable
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-ios overflow-hidden shadow-ios hover:shadow-ios-strong 
        transform transition duration-200 ease-in-out hover:-translate-y-0.5 cursor-pointer"
    >
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
            article.source === 'techcrunch' 
              ? 'bg-ios-green/10 text-ios-green' 
              : 'bg-uoft-light-blue/10 text-uoft-light-blue'
          }`}>
            {article.source === 'techcrunch' ? 'TechCrunch' : '36Kr'}
          </span>
          <span className="text-xs text-ios-gray-600">{formatDate(article.gmt8time)}</span>
        </div>
        <h3 className="font-semibold text-ios-gray-900 mb-2 line-clamp-2">{article.title}</h3>
        {article.summary && (
          <p className="text-sm text-ios-gray-600 line-clamp-2 mb-3">{article.summary}</p>
        )}
        <div className="mt-auto pt-2 flex items-center justify-between">
          {article.author && (
            <span className="text-xs text-ios-gray-500">{article.author}</span>
          )}
          <span className="text-xs text-ios-blue flex items-center">
            Read more
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </span>
        </div>
      </div>
    </div>
  );
};

export default ArticleCard;