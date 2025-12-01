import React from 'react';
import { PageHeader, ComingSoonCard } from './ui';

interface ComingSoonPageProps {
  title: string;
  description: string;
  icon: string;
  cardTitle: string;
  cardDescription: string;
  features: { label: string }[];
}

export const ComingSoonPage: React.FC<ComingSoonPageProps> = ({
  title,
  description,
  icon,
  cardTitle,
  cardDescription,
  features,
}) => {
  return (
    <div className="space-y-6">
      <PageHeader
        title={title}
        description={description}
      />

      <ComingSoonCard
        icon={icon}
        title={cardTitle}
        description={cardDescription}
        features={features}
      />
    </div>
  );
};