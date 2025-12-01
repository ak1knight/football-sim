import React from 'react';
import { ComingSoonPage } from './ComingSoonPage';

export const TeamManagement: React.FC = () => {
  return (
    <ComingSoonPage
      title="Team Management"
      description="Manage rosters, statistics, and team history"
      icon="👥"
      cardTitle="Team Management"
      cardDescription="Comprehensive team management tools for roster control, player statistics, and team performance analysis."
      features={[
        { label: 'Player roster management' },
        { label: 'Individual player statistics' },
        { label: 'Team performance metrics' },
        { label: 'Historical team data' }
      ]}
    />
  );
};