import React from 'react';
import { ComingSoonPage } from './ComingSoonPage';

export const AppSettings: React.FC = () => {
  return (
    <ComingSoonPage
      title="App Settings"
      description="Manage application preferences and simulation settings"
      icon="⚙️"
      cardTitle="App Settings"
      cardDescription="Customize your football simulation experience with application-wide settings and preferences."
      features={[
        { label: 'Simulation preferences' },
        { label: 'UI theme customization' },
        { label: 'Notification settings' },
        { label: 'Database management' }
      ]}
    />
  );
};