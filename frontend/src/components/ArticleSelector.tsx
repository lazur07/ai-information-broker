// frontend/src/components/ArticleSelector.tsx
import React, { useState, useEffect } from 'react';
import { NewsItem } from '../types';

interface ArticleSelectorProps {
  filename: string;
  onSelectionChange: (selectedIds: string[]) => void;
  onClose: () => void;
}

const ArticleSelector: React.FC<ArticleSelectorProps> = ({ 
  filename, 
  onSelectionChange,
  onClose
}) => {
  const [articles, setArticles] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    const fetchArticles = async () => {
      if (!filename) return;
      
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`/data/info/files/${encodeURIComponent(filename)}`);
        
        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }
        
        const data = await response.json();