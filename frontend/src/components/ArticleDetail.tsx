// frontend/src/components/ArticleDetail.tsx
import React from 'react';
import { NewsItem } from '../types';

interface ArticleDetailProps {
  article: NewsItem;
  onClose: () => void;
}

const ArticleDetail: React.FC<ArticleDetailProps> = ({ article, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm overflow-y-auto h-full w-full flex items-center justify-center">
      <div className="relative w-full max-w-4xl mx-auto p-4">
        <div className="bg-white rounded-ios shadow-ios-strong overflow-hidden">
          <div className="flex justify-between items-center p-4 border-b border-ios-gray-200">
            <div className="flex items-center space-x-2">
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                article.source === 'techcrunch' 
                  ? 'bg-uoft-light-blue/10 text-uoft-light-blue' 
                  : 'bg-uoft-blue/10 text-uoft-blue'
              }`}>
                {article.source === 'techcrunch' ? 'TechCrunch' : '36Kr'}
              </span>
              <span className="text-sm text-ios-gray-600">{article.gmt8time}</span>
            </div>
            <button 
              onClick={onClose}
              className="bg-ios-gray-100 text-ios-gray-700 rounded-full p-1.5 hover:bg-ios-gray-200 active:bg-ios-gray-300 transition-colors"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
            <h2 className="text-xl font-semibold text-ios-gray-900 mb-4">{article.title}</h2>
            
            {article.author && (
              <p className="text-sm text-ios-gray-600 mb-4">By {article.author}</p>
            )}
            
            {article.summary && (
              <div className="mb-6 bg-ios-gray-50 p-4 rounded-ios">
                <h3 className="text-sm font-semibold text-ios-gray-800 mb-2">Summary</h3>
                <p className="text-ios-gray-700">{article.summary}</p>
              </div>
            )}
            
            {article.content && (
              <div className="text-ios-gray-800 space-y-4 leading-relaxed">
                {article.content.split('\n').map((paragraph, i) => (
                  paragraph.trim() ? <p key={i}>{paragraph}</p> : null
                ))}
              </div>
            )}
            
            <div className="mt-8 pt-6 border-t border-ios-gray-200 flex justify-end">
              <a 
                href={article.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center px-5 py-2.5 rounded-ios font-medium text-white bg-uoft-blue hover:bg-opacity-90 active:bg-opacity-80 transition duration-150"
              >
                View Original Article
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleDetail;