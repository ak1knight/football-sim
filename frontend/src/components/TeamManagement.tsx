import React from 'react';
import { PageHeader, ComingSoonCard } from './ui';

export const TeamManagement: React.FC = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Team Management"
        description="Manage rosters, statistics, and team history"
      />

      <ComingSoonCard
        icon="👥"
        title="Team Management"
        description="Comprehensive team management tools for roster control, player statistics, and team performance analysis."
        features={[
          { label: 'Player roster management' },
          { label: 'Individual player statistics' },
          { label: 'Team performance metrics' },
          { label: 'Historical team data' }
        ]}
      />
    </div>
  );
};