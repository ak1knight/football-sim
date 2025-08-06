import React from 'react';
import { PageHeader, ComingSoonCard } from './ui';

export const LeagueManagement: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="League Management"
        description="Configure league settings, rules, and structure"
      />

      <ComingSoonCard
        icon="🏆"
        title="League Management"
        description="Comprehensive league administration tools for configuring divisions, rules, and overall league structure."
        features={[
          { label: 'Division and conference setup' },
          { label: 'League rules configuration' },
          { label: 'Playoff format settings' },
          { label: 'League-wide statistics' }
        ]}
      />
    </div>
  );
};