import React from 'react';

interface StatItemProps {
  label: string;
  value: string | number;
  valueColor?: string;
  className?: string;
}

export const StatItem: React.FC<StatItemProps> = ({ 
  label, 
  value, 
  valueColor = 'text-white',
  className = '' 
}) => {
  return (
    <div className={`flex justify-between items-center py-2 border-b border-secondary-800 last:border-b-0 ${className}`}>
      <span className="text-secondary-300 font-medium">{label}</span>
      <span className={`font-semibold ${valueColor}`}>{value}</span>
    </div>
  );
};

interface StatComparisonProps {
  label: string;
  awayValue: string | number;
  homeValue: string | number;
  valueColor?: string;
  className?: string;
}

export const StatComparison: React.FC<StatComparisonProps> = ({ 
  label, 
  awayValue, 
  homeValue, 
  valueColor = 'text-primary-400',
  className = '' 
}) => {
  return (
    <div className={`flex justify-between items-center ${className}`}>
      <span className="text-secondary-300">{label}</span>
      <div className="flex items-center space-x-4">
        <span className={`font-medium ${valueColor}`}>{awayValue}</span>
        <span className="text-secondary-500">-</span>
        <span className={`font-medium ${valueColor}`}>{homeValue}</span>
      </div>
    </div>
  );
};

interface StatGridProps {
  children: React.ReactNode;
  columns?: number;
  className?: string;
}

export const StatGrid: React.FC<StatGridProps> = ({ 
  children, 
  columns = 2, 
  className = '' 
}) => {
  const gridClasses = {
    1: 'grid-cols-1',
    2: 'grid md:grid-cols-2',
    3: 'grid md:grid-cols-2 lg:grid-cols-3',
    4: 'grid md:grid-cols-2 lg:grid-cols-4'
  };

  return (
    <div className={`${gridClasses[columns as keyof typeof gridClasses] || gridClasses[2]} gap-6 ${className}`}>
      {children}
    </div>
  );
};