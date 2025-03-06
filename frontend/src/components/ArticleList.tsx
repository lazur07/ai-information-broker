import React from 'react';
import { NewsItem } from '../types';
import ArticleCard from './ArticleCard';

interface ArticleListProps {
  articles: NewsItem[];
  onSelectArticle: (article: NewsItem) => void;
}

const ArticleList: React.FC<ArticleListProps> = ({ articles, onSelectArticle }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      {articles.map(article => (
        <ArticleCard 
          key={article.id} 
          article={article} 
          onClick={() => onSelectArticle(article)} 
        />
      ))}
    </div>
  );
};

export default ArticleList;
