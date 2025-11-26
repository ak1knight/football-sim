import React from 'react';
import { ComingSoonPage } from './ComingSoonPage';

export const LeagueManagement: React.FC = () => {
  return (
    <ComingSoonPage
      title="League Management"
      description="Configure league settings, rules, and structure"
      icon="🏆"
      cardTitle="League Management"
      cardDescription="Comprehensive league administration tools for configuring divisions, rules, and overall league structure."
      features={[
        { label: 'Division and conference setup' },
        { label: 'League rules configuration' },
        { label: 'Playoff format settings' },
        { label: 'League-wide statistics' }
      ]}
    />
  );
};