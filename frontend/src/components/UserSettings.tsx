import React from 'react';
import { ComingSoonPage } from './ComingSoonPage';

export const UserSettings: React.FC = () => {
  return (
    <ComingSoonPage
      title="User Settings"
      description="Manage your profile, preferences, and application settings"
      icon="⚙️"
      cardTitle="User Settings"
      cardDescription="Customize your football simulation experience with personalized settings and preferences."
      features={[
        { label: 'Profile management' },
        { label: 'Simulation preferences' },
        { label: 'UI theme customization' },
        { label: 'Notification settings' }
      ]}
    />
  );
};