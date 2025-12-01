import React from 'react';

interface PageHeaderProps {
  title: string;
  description: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title, description }) => {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white">{title}</h1>
      <p className="text-secondary-400 mt-1">{description}</p>
    </div>
  );
};