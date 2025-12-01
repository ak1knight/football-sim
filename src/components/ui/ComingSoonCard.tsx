import React from 'react';
import { Card } from './Card';

interface Feature {
  label: string;
}

interface ComingSoonCardProps {
  icon: string;
  title: string;
  description: string;
  features: Feature[];
}

export const ComingSoonCard: React.FC<ComingSoonCardProps> = ({
  icon,
  title,
  description,
  features
}) => {
  return (
    <Card padding="lg" className="text-center">
      <div className="text-6xl mb-4">{icon}</div>
      <h2 className="text-xl font-semibold text-white mb-2">{title}</h2>
      <p className="text-secondary-400 mb-6">{description}</p>
      
      <div className="space-y-3 text-left max-w-md mx-auto">
        {features.map((feature, index) => (
          <div key={index} className="flex items-center text-secondary-300">
            <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
            {feature.label}
          </div>
        ))}
      </div>
      
      <div className="mt-8">
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-accent-900 text-accent-300">
          Coming Soon
        </span>
      </div>
    </Card>
  );
};