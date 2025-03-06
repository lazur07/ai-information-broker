// frontend/src/components/StatsCard.tsx
import React from 'react';

interface StatsCardProps {
  totalCount: number;
  timestamp: string;
}

const StatsCard: React.FC<StatsCardProps> = ({ totalCount, timestamp }) => {
  return (
    <div className="ios-card rounded-ios-lg mt-4">
      <h2 className="text-sm font-semibold text-gray-700 mb-3">Statistics</h2>
      <div className="ios-divider"></div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-ios-gray-1">Total Articles</p>
          <p className="text-2xl font-semibold text-ios-blue">{totalCount}</p>
        </div>
        <div>
          <p className="text-xs text-ios-gray-1">Last Updated</p>
          <p className="text-sm">{new Date(timestamp).toLocaleTimeString()}</p>
        </div>
      </div>
    </div>
  );
};

export default StatsCard;