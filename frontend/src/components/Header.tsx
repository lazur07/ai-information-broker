// frontend/src/components/Header.tsx
import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-10 bg-white/90 backdrop-blur-lg border-b border-ios-gray-200 px-4 py-3">
      <div className="max-w-5xl mx-auto flex justify-between items-center">
        <h1 className="text-xl font-semibold text-black">AI Information</h1>
        <div className="text-sm font-medium text-ios-blue">
          Latest News
        </div>
      </div>
    </header>
  );
};

export default Header;